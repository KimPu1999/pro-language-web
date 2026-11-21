import ipaddress
import json
from datetime import datetime, timezone
from urllib.parse import urlparse
from uuid import UUID
from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .auth import current_user, require_csrf, verified_user
from .db import get_db
from .models import (PortfolioProject, ProjectAuditLog, ProjectBookmark, ProjectCategory, ProjectMilestone, ProjectRequirement, ProjectResource, ProjectReview, ProjectReviewScore, ProjectRubricCriterion, ProjectSubmission, ProjectTask, ProjectTemplate, ProjectSkill, StudentPortfolio, StudentProject, StudentProjectMilestone, VerifiedProjectSkill, User)
from .admin_routes import admin_user, audit
from .media_storage import remove_file_if_safe, safe_media_path, save_project_image, save_project_submission_archive

router=APIRouter(prefix="/api/v1",tags=["projects"])
class SubmissionIn(BaseModel): repository_url:str; branch_or_sha:str=Field(min_length=1,max_length=180); demo_url:str|None=None; project_description:str=""; setup_instructions:str=""; reviewer_notes:str=""
class MilestoneIn(BaseModel): completed:bool; notes:str=""
class ProjectIn(BaseModel): title:str=Field(min_length=1,max_length=180); slug:str=Field(pattern=r"^[a-z0-9-]+$"); description_en:str=""; description_mm:str|None=None; difficulty:str="beginner"; category_id:UUID|None=None; estimated_hours:int=Field(default=0,ge=0); requirements:str=""; learning_outcomes:str=""; technology_stack:str=""; prerequisites:str=""; architecture_overview:str=""; folder_structure:str=""; testing_guide:str=""; deployment_guide:str=""; cover_image:str|None=None; tags:list[str]=[]; languages:list[str]=[]; brief:dict={}
class ProjectPatch(BaseModel): title:str|None=Field(default=None,min_length=1,max_length=180); slug:str|None=Field(default=None,pattern=r"^[a-z0-9-]+$"); description_en:str|None=None; description_mm:str|None=None; difficulty:str|None=None; category_id:UUID|None=None; estimated_hours:int|None=Field(default=None,ge=0); requirements:str|None=None; learning_outcomes:str|None=None; technology_stack:str|None=None; prerequisites:str|None=None; architecture_overview:str|None=None; folder_structure:str|None=None; testing_guide:str|None=None; deployment_guide:str|None=None; cover_image:str|None=None; tags:list[str]|None=None; languages:list[str]|None=None; brief:dict|None=None
class ReviewIn(BaseModel): decision:str; comments:str=""; scores:dict[UUID,int]={}
class PortfolioIn(BaseModel): username:str=Field(pattern=r"^[a-z0-9-]{3,80}$"); headline:str=""; bio:str=""; github_url:str|None=None; visibility:str="private"
def safe_url(value:str,github=False):
    try: parsed=urlparse(value)
    except ValueError: raise HTTPException(422,"Invalid URL")
    host=(parsed.hostname or "").lower(); allowed={"github.com","www.github.com"} if github else {"http","https"}
    if github and host not in allowed: raise HTTPException(422,"Repository must be a GitHub URL")
    if not github and parsed.scheme not in allowed: raise HTTPException(422,"URL must use HTTP or HTTPS")
    if not parsed.netloc or parsed.username or parsed.password: raise HTTPException(422,"Unsafe URL")
    if host in {"localhost","127.0.0.1","::1"}:
        raise HTTPException(422,"Local URLs are not allowed")
    try:
        if ipaddress.ip_address(host).is_private: raise HTTPException(422,"Private network URLs are not allowed")
    except ValueError: pass
    return value
def json_value(value, fallback):
    try: return json.loads(value or "")
    except (TypeError, ValueError, json.JSONDecodeError): return fallback
def project_admin_out(row, db):
    return template_out(row, db)
def template_out(row,db,public=False):
    milestones=db.scalars(select(ProjectMilestone).where(ProjectMilestone.project_id==row.id).order_by(ProjectMilestone.position)).all(); criteria=db.scalars(select(ProjectRubricCriterion).where(ProjectRubricCriterion.project_id==row.id).order_by(ProjectRubricCriterion.position)).all(); requirements=db.scalars(select(ProjectRequirement).where(ProjectRequirement.project_id==row.id).order_by(ProjectRequirement.position)).all(); resources=db.scalars(select(ProjectResource).where(ProjectResource.project_id==row.id).order_by(ProjectResource.position)).all(); category=db.get(ProjectCategory,row.category_id) if row.category_id else None
    tasks_by_milestone={m.id:db.scalars(select(ProjectTask).where(ProjectTask.milestone_id==m.id).order_by(ProjectTask.position)).all() for m in milestones}
    visible_resources=[r for r in resources if r.is_public and r.status=="published"] if public else resources
    return {"id":row.id,"title":row.title,"slug":row.slug,"description_en":row.description_en,"description_mm":row.description_mm,"difficulty":row.difficulty,"estimated_hours":row.estimated_hours,"requirements":row.requirements,"learning_outcomes":row.learning_outcomes,"technology_stack":row.technology_stack,"prerequisites":row.prerequisites,"architecture_overview":row.architecture_overview,"folder_structure":row.folder_structure,"testing_guide":row.testing_guide,"deployment_guide":row.deployment_guide,"cover_image":row.cover_image,"tags":json_value(row.tags_json,[]),"languages":json_value(row.languages_json,[]),"brief":json_value(row.brief_json,{}),"category":{"id":category.id,"name":category.name,"slug":category.slug} if category else None,"status":row.status,"published":row.published,"milestones":[{"id":m.id,"title":m.title,"slug":m.slug or f"step-{m.position}","description_en":m.description_en,"description_mm":m.description_mm,"content_en":m.content_en,"content_mm":m.content_mm,"code":m.code,"filename":m.filename,"expected_output":m.expected_output,"line_explanation":m.line_explanation,"completion_criteria":m.completion_criteria,"resources":json_value(m.resources_json,[]),"position":m.position,"required":m.required,"tasks":[{"id":t.id,"title":t.title,"description":t.description,"completion_criteria":t.completion_criteria,"position":t.position,"required":t.required} for t in tasks_by_milestone[m.id]]} for m in milestones],"requirements_items":[{"id":r.id,"title":r.title,"description":r.description,"acceptance_criteria":r.acceptance_criteria,"required":r.required,"position":r.position} for r in requirements],"resources":[{"id":r.id,"milestone_id":r.milestone_id,"title":r.title,"resource_type":r.resource_type,"url":r.url,"storage_key":r.storage_key,"description":r.description,"position":r.position,"is_public":r.is_public,"status":r.status} for r in visible_resources],"rubric":[{"id":c.id,"name":c.name,"description":getattr(c,"description",""),"weight":c.weight,"position":c.position} for c in criteria]}
def project_progress(db,student):
    total=db.scalar(select(func.count(ProjectMilestone.id)).where(ProjectMilestone.project_id==student.project_id,ProjectMilestone.required.is_(True))) or 0; done=db.scalar(select(func.count(StudentProjectMilestone.id)).join(ProjectMilestone,ProjectMilestone.id==StudentProjectMilestone.milestone_id).where(StudentProjectMilestone.student_project_id==student.id,StudentProjectMilestone.completed.is_(True),ProjectMilestone.required.is_(True))) or 0; return {"completed":done,"total":total,"percent":round(done/total*100,1) if total else 0}
@router.get("/project-categories")
def list_project_categories(db:Session=Depends(get_db)):
    return db.scalars(select(ProjectCategory).where(ProjectCategory.status=="active").order_by(ProjectCategory.name)).all()

@router.get("/projects")
def list_projects(search:str|None=None,difficulty:str|None=None,category:str|None=None,technology:str|None=None,page:int=Query(1,ge=1),page_size:int=Query(12,ge=1,le=50),db:Session=Depends(get_db)):
    q=select(ProjectTemplate).where(ProjectTemplate.published.is_(True)); count=select(func.count()).select_from(ProjectTemplate).where(ProjectTemplate.published.is_(True))
    if search:
        pattern=f"%{search}%"; q=q.where(ProjectTemplate.title.ilike(pattern)|ProjectTemplate.description_en.ilike(pattern));count=count.where(ProjectTemplate.title.ilike(pattern)|ProjectTemplate.description_en.ilike(pattern))
    if difficulty:q=q.where(ProjectTemplate.difficulty==difficulty);count=count.where(ProjectTemplate.difficulty==difficulty)
    if category:
        q=q.join(ProjectCategory,ProjectCategory.id==ProjectTemplate.category_id).where(ProjectCategory.slug==category);count=count.join(ProjectCategory,ProjectCategory.id==ProjectTemplate.category_id).where(ProjectCategory.slug==category)
    if technology:q=q.where(ProjectTemplate.technology_stack.ilike(f"%{technology}%"));count=count.where(ProjectTemplate.technology_stack.ilike(f"%{technology}%"))
    total=db.scalar(count) or 0;rows=db.scalars(q.order_by(ProjectTemplate.title).offset((page-1)*page_size).limit(page_size)).all();return {"items":[template_out(x,db,True) for x in rows],"page":page,"page_size":page_size,"total":total,"pages":(total+page_size-1)//page_size if total else 0}
@router.get("/projects/{slug}/modules")
def project_modules(slug:str,db:Session=Depends(get_db)):
    row=db.scalar(select(ProjectTemplate).where(ProjectTemplate.slug==slug,ProjectTemplate.published.is_(True)))
    if not row: raise HTTPException(404,"Project not found")
    return template_out(row,db)["milestones"]

@router.get("/projects/{slug}/steps")
def project_steps(slug:str,db:Session=Depends(get_db)):
    row=db.scalar(select(ProjectTemplate).where(ProjectTemplate.slug==slug,ProjectTemplate.published.is_(True)))
    if not row: raise HTTPException(404,"Project not found")
    return template_out(row,db)["milestones"]

@router.get("/projects/{slug}")
def get_project(slug:str,db:Session=Depends(get_db)):
    row=db.scalar(select(ProjectTemplate).where(ProjectTemplate.slug==slug,ProjectTemplate.published.is_(True)))
    if not row:raise HTTPException(404,"Project not found")
    return template_out(row,db,True)
@router.post("/me/projects/{slug}",status_code=201)
def start_project(slug:str,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    template=db.scalar(select(ProjectTemplate).where(ProjectTemplate.slug==slug,ProjectTemplate.published.is_(True)))
    if not template:raise HTTPException(404,"Published project not found")
    if db.scalar(select(StudentProject).where(StudentProject.user_id==user.id,StudentProject.project_id==template.id)):raise HTTPException(409,"Project already started")
    row=StudentProject(user_id=user.id,project_id=template.id);db.add(row);db.flush();milestones=db.scalars(select(ProjectMilestone).where(ProjectMilestone.project_id==template.id)).all();db.add_all([StudentProjectMilestone(student_project_id=row.id,milestone_id=m.id) for m in milestones]);db.commit();return {"id":row.id,"status":row.status,"progress":project_progress(db,row)}
@router.post("/projects/{project_id}/enroll",status_code=201)
def enroll_project(project_id:UUID,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    template=db.scalar(select(ProjectTemplate).where(ProjectTemplate.id==project_id,ProjectTemplate.published.is_(True)))
    if not template: raise HTTPException(404,"Published project not found")
    return start_project(template.slug,user,_,db)
@router.get("/me/projects")
def my_projects(user:User=Depends(current_user),db:Session=Depends(get_db)):
    rows=db.scalars(select(StudentProject).where(StudentProject.user_id==user.id).order_by(StudentProject.created_at.desc())).all();return [{"id":r.id,"project_id":r.project_id,"title":db.scalar(select(ProjectTemplate.title).where(ProjectTemplate.id==r.project_id)),"difficulty":db.scalar(select(ProjectTemplate.difficulty).where(ProjectTemplate.id==r.project_id)),"status":r.status,"progress":project_progress(db,r)} for r in rows]
@router.get("/me/projects/dashboard")
def my_project_dashboard(search:str|None=None,status:str|None=None,technology:str|None=None,page:int=Query(1,ge=1),page_size:int=Query(10,ge=1,le=50),user:User=Depends(current_user),db:Session=Depends(get_db)):
    base=select(StudentProject,ProjectTemplate).join(ProjectTemplate,ProjectTemplate.id==StudentProject.project_id).where(StudentProject.user_id==user.id)
    count=select(func.count()).select_from(StudentProject).join(ProjectTemplate,ProjectTemplate.id==StudentProject.project_id).where(StudentProject.user_id==user.id)
    if search:
        pattern=f"%{search}%"; condition=ProjectTemplate.title.ilike(pattern)|ProjectTemplate.description_en.ilike(pattern); base=base.where(condition);count=count.where(condition)
    if status:
        condition=StudentProject.status==("approved" if status=="completed" else status);base=base.where(condition);count=count.where(condition)
    if technology:
        condition=ProjectTemplate.technology_stack.ilike(f"%{technology}%");base=base.where(condition);count=count.where(condition)
    total=db.scalar(count) or 0; rows=db.execute(base.order_by(StudentProject.updated_at.desc()).offset((page-1)*page_size).limit(page_size)).all()
    items=[{"id":student.id,"project_id":template.id,"title":template.title,"difficulty":template.difficulty,"technology_stack":template.technology_stack,"status":"completed" if student.status=="approved" else student.status,"progress":project_progress(db,student),"updated_at":student.updated_at} for student,template in rows]
    return {"items":items,"page":page,"page_size":page_size,"total":total,"pages":(total+page_size-1)//page_size if total else 0}
@router.get("/me/projects/{project_id}")
def my_project(project_id:UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):
    row=db.scalar(select(StudentProject).where(StudentProject.id==project_id,StudentProject.user_id==user.id));
    if not row:raise HTTPException(404,"Project not found")
    milestones=db.scalars(select(StudentProjectMilestone).where(StudentProjectMilestone.student_project_id==row.id)).all();submissions=db.scalars(select(ProjectSubmission).where(ProjectSubmission.student_project_id==row.id).order_by(ProjectSubmission.created_at.desc())).all();reviews=db.scalars(select(ProjectReview).where(ProjectReview.submission_id.in_([s.id for s in submissions]))).all() if submissions else [];review_by_submission={review.submission_id:review for review in reviews};submission_payload=[{"id":submission.id,"repository_url":submission.repository_url,"branch_or_sha":submission.branch_or_sha,"demo_url":submission.demo_url,"project_description":submission.project_description,"setup_instructions":submission.setup_instructions,"status":submission.status,"submitted_at":submission.submitted_at,"attachment_name":submission.attachment_name,"attachment_size":submission.attachment_size,"has_attachment":bool(submission.attachment_key),"review":{"decision":review_by_submission[submission.id].decision,"comments":review_by_submission[submission.id].comments,"total_score":review_by_submission[submission.id].total_score} if submission.id in review_by_submission else None} for submission in submissions];return {"id":row.id,"status":row.status,"project":template_out(db.get(ProjectTemplate,row.project_id),db),"progress":project_progress(db,row),"milestones":[{"id":m.milestone_id,"completed":m.completed,"notes":m.notes} for m in milestones],"submission":submission_payload[0] if submission_payload else None,"submissions":submission_payload}
@router.get("/me/projects/{project_id}/progress")
def project_progress_endpoint(project_id:UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):
    row=db.scalar(select(StudentProject).where(StudentProject.id==project_id,StudentProject.user_id==user.id))
    if not row: raise HTTPException(404,"Project not found")
    return project_progress(db,row)
@router.post("/me/projects/{project_id}/milestones/{milestone_id}")
def update_milestone(project_id:UUID,milestone_id:UUID,payload:MilestoneIn,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.scalar(select(StudentProject).where(StudentProject.id==project_id,StudentProject.user_id==user.id));progress=db.scalar(select(StudentProjectMilestone).where(StudentProjectMilestone.student_project_id==project_id,StudentProjectMilestone.milestone_id==milestone_id))
    if not row or not progress:raise HTTPException(404,"Project milestone not found")
    progress.completed=payload.completed;progress.notes=payload.notes;progress.completed_at=datetime.now(timezone.utc) if payload.completed else None;db.commit();return project_progress(db,row)
@router.post("/projects/{project_id}/bookmark")
def bookmark_project(project_id:UUID,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.scalar(select(ProjectTemplate).where(ProjectTemplate.id==project_id,ProjectTemplate.published.is_(True)))
    if not row: raise HTTPException(404,"Published project not found")
    bookmark=db.scalar(select(ProjectBookmark).where(ProjectBookmark.project_id==project_id,ProjectBookmark.user_id==user.id))
    if bookmark: db.delete(bookmark); bookmarked=False
    else: db.add(ProjectBookmark(user_id=user.id,project_id=project_id)); bookmarked=True
    db.commit(); return {"bookmarked":bookmarked}
@router.post("/me/projects/{project_id}/submissions",status_code=201)
def submit_project(project_id:UUID,payload:SubmissionIn,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    student=db.scalar(select(StudentProject).where(StudentProject.id==project_id,StudentProject.user_id==user.id));
    if not student:raise HTTPException(404,"Project not found")
    if student.status in {"submitted", "in_review"}: raise HTTPException(409,"A submission is already awaiting review")
    if student.status == "approved": raise HTTPException(409,"Approved projects cannot be resubmitted")
    required_ids=set(db.scalars(select(ProjectMilestone.id).where(ProjectMilestone.project_id==student.project_id,ProjectMilestone.required.is_(True))).all())
    completed_ids=set(db.scalars(select(StudentProjectMilestone.milestone_id).where(StudentProjectMilestone.student_project_id==student.id,StudentProjectMilestone.completed.is_(True),StudentProjectMilestone.milestone_id.in_(required_ids))).all()) if required_ids else set()
    if required_ids - completed_ids:
        raise HTTPException(422,"Complete all required project tasks before submitting")
    safe_url(payload.repository_url,True);demo=safe_url(payload.demo_url) if payload.demo_url else None;submission=ProjectSubmission(student_project_id=student.id,repository_url=payload.repository_url,branch_or_sha=payload.branch_or_sha,demo_url=demo,project_description=payload.project_description,setup_instructions=payload.setup_instructions,reviewer_notes=payload.reviewer_notes,status="submitted");db.add(submission);student.status="submitted";db.commit();return {"id":submission.id,"status":submission.status}

@router.post("/me/projects/{project_id}/submissions/upload", status_code=201)
async def submit_project_with_archive(
    project_id: UUID,
    repository_url: str = Form(""),
    branch_or_sha: str = Form("main"),
    demo_url: str = Form(""),
    project_description: str = Form(""),
    setup_instructions: str = Form(""),
    reviewer_notes: str = Form(""),
    archive: UploadFile | None = File(None),
    user: User = Depends(verified_user),
    _: None = Depends(require_csrf),
    db: Session = Depends(get_db),
):
    """Submit GitHub evidence and/or a validated private ZIP archive.

    Archives are stored outside public media and are never extracted or executed
    by the API process.
    """
    student = db.scalar(select(StudentProject).where(StudentProject.id == project_id, StudentProject.user_id == user.id))
    if not student:
        raise HTTPException(404, "Project not found")
    if student.status in {"submitted", "in_review"}:
        raise HTTPException(409, "A submission is already awaiting review")
    if student.status == "approved":
        raise HTTPException(409, "Approved projects cannot be resubmitted")
    required_ids = set(db.scalars(select(ProjectMilestone.id).where(ProjectMilestone.project_id == student.project_id, ProjectMilestone.required.is_(True))).all())
    completed_ids = set(db.scalars(select(StudentProjectMilestone.milestone_id).where(StudentProjectMilestone.student_project_id == student.id, StudentProjectMilestone.completed.is_(True), StudentProjectMilestone.milestone_id.in_(required_ids))).all()) if required_ids else set()
    if required_ids - completed_ids:
        raise HTTPException(422, "Complete all required project tasks before submitting")
    repository_url = repository_url.strip()
    branch_or_sha = branch_or_sha.strip()
    if len(branch_or_sha) < 1 or len(branch_or_sha) > 180:
        raise HTTPException(422, "Branch or commit reference is required")
    if repository_url:
        safe_url(repository_url, True)
    elif archive is None:
        raise HTTPException(422, "Provide a GitHub repository URL or a ZIP project archive")
    demo = safe_url(demo_url.strip()) if demo_url.strip() else None
    attachment_key = attachment_name = None
    attachment_size = None
    if archive is not None:
        attachment_key, _, attachment_name, attachment_size = await save_project_submission_archive(archive)
    submission = ProjectSubmission(
        student_project_id=student.id,
        repository_url=repository_url,
        branch_or_sha=branch_or_sha,
        demo_url=demo,
        project_description=project_description,
        setup_instructions=setup_instructions,
        reviewer_notes=reviewer_notes,
        attachment_key=attachment_key,
        attachment_name=attachment_name,
        attachment_size=attachment_size,
        status="submitted",
    )
    db.add(submission)
    student.status = "submitted"
    db.commit()
    return {"id": submission.id, "status": submission.status, "attachment_name": submission.attachment_name, "attachment_size": submission.attachment_size}


def _submission_attachment_path(submission: ProjectSubmission):
    if not submission.attachment_key or not submission.attachment_key.startswith("projects/private/"):
        raise HTTPException(404, "Submission archive not found")
    path = safe_media_path(f"/media/{submission.attachment_key}")
    if not path or not path.is_file():
        raise HTTPException(404, "Submission archive not found")
    return path


@router.get("/me/project-submissions/{submission_id}/download")
def download_own_project_submission(submission_id: UUID, user: User = Depends(verified_user), db: Session = Depends(get_db)):
    submission = db.get(ProjectSubmission, submission_id)
    if not submission:
        raise HTTPException(404, "Submission not found")
    student = db.get(StudentProject, submission.student_project_id)
    if not student or student.user_id != user.id:
        raise HTTPException(403, "You do not have access to this submission")
    path = _submission_attachment_path(submission)
    return FileResponse(path, media_type="application/zip", filename=submission.attachment_name or "project-submission.zip")
@router.get("/instructor/projects/reviews")
def review_queue(user:User=Depends(admin_user),db:Session=Depends(get_db)):
    rows=db.scalars(select(ProjectSubmission).where(ProjectSubmission.status.in_(["submitted","in_review","changes_requested"])).order_by(ProjectSubmission.created_at)).all();return [{"id":row.id,"status":row.status,"submitted_at":row.submitted_at,"repository_url":row.repository_url,"branch_or_sha":row.branch_or_sha,"attachment_name":row.attachment_name,"attachment_size":row.attachment_size,"has_attachment":bool(row.attachment_key),"project_title":db.scalar(select(ProjectTemplate.title).join(StudentProject,StudentProject.project_id==ProjectTemplate.id).where(StudentProject.id==row.student_project_id))} for row in rows]
@router.get("/instructor/projects/reviews/{submission_id}")
def review_detail(submission_id:UUID,user:User=Depends(admin_user),db:Session=Depends(get_db)):
    submission=db.get(ProjectSubmission,submission_id)
    if not submission: raise HTTPException(404,"Submission not found")
    project=db.get(StudentProject,submission.student_project_id); template=db.get(ProjectTemplate,project.project_id) if project else None
    criteria=db.scalars(select(ProjectRubricCriterion).where(ProjectRubricCriterion.project_id==project.project_id).order_by(ProjectRubricCriterion.position)).all() if project else []
    return {"id":submission.id,"status":submission.status,"submitted_at":submission.submitted_at,"repository_url":submission.repository_url,"branch_or_sha":submission.branch_or_sha,"demo_url":submission.demo_url,"project_description":submission.project_description,"setup_instructions":submission.setup_instructions,"attachment_name":submission.attachment_name,"attachment_size":submission.attachment_size,"has_attachment":bool(submission.attachment_key),"project":{"id":template.id,"title":template.title} if template else None,"criteria":[{"id":c.id,"name":c.name,"description":c.description,"weight":c.weight,"position":c.position} for c in criteria]}
@router.post("/instructor/projects/reviews/{submission_id}")
def review_submission(submission_id:UUID,payload:ReviewIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    submission=db.get(ProjectSubmission,submission_id)
    if not submission:raise HTTPException(404,"Submission not found")
    allowed={"submitted":{"in_review","changes_requested","rejected","approved"},"in_review":{"changes_requested","rejected","approved"},"changes_requested":{"in_review","submitted"}}
    if payload.decision not in allowed.get(submission.status,set()):raise HTTPException(422,"Invalid submission state transition")
    project=db.get(StudentProject,submission.student_project_id);criteria=db.scalars(select(ProjectRubricCriterion).where(ProjectRubricCriterion.project_id==project.project_id)).all();weights=sum(c.weight for c in criteria)
    if payload.decision=="approved" and weights!=100:raise HTTPException(422,"Rubric weights must total 100")
    if payload.decision=="approved" and set(payload.scores)!={c.id for c in criteria}:raise HTTPException(422,"All rubric criteria require scores")
    review=ProjectReview(submission_id=submission.id,reviewer_id=user.id,decision=payload.decision,comments=payload.comments);db.add(review);db.flush();total=0
    for c in criteria:
        score=payload.scores.get(c.id,0); 
        if score<0 or score>100:raise HTTPException(422,"Scores must be between 0 and 100")
        db.add(ProjectReviewScore(review_id=review.id,criterion_id=c.id,score=score));total+=c.weight*score//100
    review.total_score=total if payload.decision=="approved" else None;submission.status=payload.decision;submission.reviewer_id=user.id;project.status="approved" if payload.decision=="approved" else project.status;db.add(ProjectAuditLog(actor_id=user.id,submission_id=submission.id,action=f"submission_{payload.decision}"))
    if payload.decision=="approved":
        for skill in db.scalars(select(ProjectSkill).where(ProjectSkill.project_id==project.project_id)).all():
            if not db.scalar(select(VerifiedProjectSkill).where(VerifiedProjectSkill.user_id==project.user_id,VerifiedProjectSkill.skill_id==skill.skill_id,VerifiedProjectSkill.student_project_id==project.id)):db.add(VerifiedProjectSkill(user_id=project.user_id,skill_id=skill.skill_id,student_project_id=project.id,review_id=review.id))
    db.commit();return {"id":review.id,"decision":review.decision,"total_score":review.total_score}
@router.get("/me/portfolio")
def get_portfolio(user:User=Depends(current_user),db:Session=Depends(get_db)):
    row=db.scalar(select(StudentPortfolio).where(StudentPortfolio.user_id==user.id))
    if not row: return {"visibility":"private","projects":[]}
    projects=db.execute(select(PortfolioProject,StudentProject,ProjectTemplate).join(StudentProject,StudentProject.id==PortfolioProject.student_project_id).join(ProjectTemplate,ProjectTemplate.id==StudentProject.project_id).where(PortfolioProject.portfolio_id==row.id)).all()
    return {"id":row.id,"username":row.username,"headline":row.headline,"bio":row.bio,"github_url":row.github_url,"visibility":row.visibility,"projects":[{"id":portfolio_project.id,"student_project_id":student_project.id,"title":template.title,"status":student_project.status,"visible":portfolio_project.visible} for portfolio_project,student_project,template in projects]}
@router.put("/me/portfolio")
def save_portfolio(payload:PortfolioIn,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.scalar(select(StudentPortfolio).where(StudentPortfolio.user_id==user.id)) or StudentPortfolio(user_id=user.id,username=payload.username);row.username=payload.username;row.headline=payload.headline;row.bio=payload.bio;row.github_url=safe_url(payload.github_url) if payload.github_url else None;row.visibility=payload.visibility if payload.visibility in {"private","public"} else "private";db.add(row);db.commit();return row
@router.post("/me/portfolio/projects/{student_project_id}")
def add_portfolio_project(student_project_id:UUID,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    portfolio=db.scalar(select(StudentPortfolio).where(StudentPortfolio.user_id==user.id));project=db.scalar(select(StudentProject).where(StudentProject.id==student_project_id,StudentProject.user_id==user.id,StudentProject.status=="approved"))
    if not portfolio or not project:raise HTTPException(403,"Only your approved projects can be showcased")
    db.add(PortfolioProject(portfolio_id=portfolio.id,student_project_id=project.id));db.commit();return {"status":"added"}
@router.get("/u/{username}")
def public_portfolio(username:str,db:Session=Depends(get_db)):
    portfolio=db.scalar(select(StudentPortfolio).where(StudentPortfolio.username==username,StudentPortfolio.visibility=="public"));
    if not portfolio:raise HTTPException(404,"Portfolio not found")
    projects=db.scalars(select(StudentProject).join(PortfolioProject,PortfolioProject.student_project_id==StudentProject.id).where(PortfolioProject.portfolio_id==portfolio.id,PortfolioProject.visible.is_(True),StudentProject.status=="approved")).all();return {"username":portfolio.username,"headline":portfolio.headline,"bio":portfolio.bio,"github_url":portfolio.github_url,"projects":[{"id":p.id,"project_id":p.project_id} for p in projects]}
@router.post("/admin/projects",status_code=201)
def create_project(payload:ProjectIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    if db.scalar(select(ProjectTemplate).where(ProjectTemplate.slug==payload.slug)):raise HTTPException(409,"Slug already exists")
    if payload.difficulty not in {"beginner","intermediate","advanced","professional"}:raise HTTPException(422,"Invalid difficulty")
    if payload.category_id and not db.get(ProjectCategory,payload.category_id): raise HTTPException(422,"Project category not found")
    values=payload.model_dump(exclude={"tags","languages","brief"}); values.update(tags_json=json.dumps(payload.tags),languages_json=json.dumps(payload.languages),brief_json=json.dumps(payload.brief),created_by=user.id)
    row=ProjectTemplate(**values);db.add(row);db.flush();audit(db,user,"project_created","project",row.id);db.commit();return {"id":row.id,"slug":row.slug,"status":row.status}
def project_quality(row,db):
    milestones=db.scalars(select(ProjectMilestone).where(ProjectMilestone.project_id==row.id)).all();criteria=db.scalars(select(ProjectRubricCriterion).where(ProjectRubricCriterion.project_id==row.id)).all();requirements_count=db.scalar(select(func.count(ProjectRequirement.id)).where(ProjectRequirement.project_id==row.id)) or 0;missing=[]
    requirements_value=row.requirements if (row.requirements or "").strip() else ("structured requirements" if requirements_count else "")
    for field,label in ((row.description_en,"overview"),(requirements_value,"requirements"),(row.learning_outcomes,"learning objectives"),(row.technology_stack,"technology stack"),(row.testing_guide,"testing guide")):
        if not (field or "").strip(): missing.append(label)
    if not milestones: missing.append("tutorial milestones")
    elif any(not (m.title.strip() and m.content_en.strip()) for m in milestones): missing.append("complete milestone content")
    if not criteria: missing.append("grading rubric")
    elif sum(c.weight for c in criteria)!=100: missing.append("rubric weights totaling 100")
    return {"ready":not missing,"missing":missing,"milestones":len(milestones),"rubric_weight":sum(c.weight for c in criteria)}
@router.get("/admin/projects")
def admin_projects(search:str|None=None,published:bool|None=None,page:int=Query(1,ge=1),page_size:int=Query(10,ge=1,le=50),user:User=Depends(admin_user),db:Session=Depends(get_db)):
    q=select(ProjectTemplate);count=select(func.count()).select_from(ProjectTemplate)
    if search:
        condition=ProjectTemplate.title.ilike(f"%{search}%")|ProjectTemplate.slug.ilike(f"%{search}%");q=q.where(condition);count=count.where(condition)
    if published is not None:q=q.where(ProjectTemplate.published==published);count=count.where(ProjectTemplate.published==published)
    total=db.scalar(count) or 0;rows=db.scalars(q.order_by(ProjectTemplate.updated_at.desc()).offset((page-1)*page_size).limit(page_size)).all()
    return {"items":[{"id":row.id,"title":row.title,"slug":row.slug,"status":row.status,"published":row.published,"updated_at":row.updated_at,"quality":project_quality(row,db)} for row in rows],"page":page,"page_size":page_size,"total":total,"pages":(total+page_size-1)//page_size if total else 0}
@router.get("/admin/projects/{project_id}")
def admin_project_detail(project_id:UUID,user:User=Depends(admin_user),db:Session=Depends(get_db)):
    row=db.get(ProjectTemplate,project_id)
    if not row: raise HTTPException(404,"Project not found")
    return {"project":template_out(row,db),"quality":project_quality(row,db)}
@router.patch("/admin/projects/{project_id}")
def update_project(project_id:UUID,payload:ProjectPatch,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(ProjectTemplate,project_id)
    if not row: raise HTTPException(404,"Project not found")
    values=payload.model_dump(exclude_unset=True)
    if "slug" in values and values["slug"]!=row.slug and db.scalar(select(ProjectTemplate).where(ProjectTemplate.slug==values["slug"],ProjectTemplate.id!=row.id)): raise HTTPException(409,"Slug already exists")
    if "difficulty" in values and values["difficulty"] not in {"beginner","intermediate","advanced","professional"}: raise HTTPException(422,"Invalid difficulty")
    if "category_id" in values and values["category_id"] and not db.get(ProjectCategory,values["category_id"]): raise HTTPException(422,"Project category not found")
    if "tags" in values: row.tags_json=json.dumps(values.pop("tags") or [])
    if "languages" in values: row.languages_json=json.dumps(values.pop("languages") or [])
    if "brief" in values: row.brief_json=json.dumps(values.pop("brief") or {})
    for key,value in values.items(): setattr(row,key,value)
    audit(db,user,"project_updated","project",row.id);db.commit();return {"id":row.id,"slug":row.slug,"quality":project_quality(row,db)}

@router.post("/admin/projects/{project_id}/cover-image")
async def upload_project_cover(project_id:UUID,image:UploadFile=File(...),user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=project_or_404(project_id,db)
    old=row.cover_image
    public_url,_,dimensions=await save_project_image(image)
    row.cover_image=public_url; audit(db,user,"project_cover_uploaded","project",row.id); db.commit()
    if old and old!=public_url and not db.scalar(select(ProjectTemplate.id).where(ProjectTemplate.cover_image==old,ProjectTemplate.id!=row.id)): remove_file_if_safe(old)
    return {"url":public_url,"width":dimensions[0],"height":dimensions[1]}
@router.post("/admin/projects/{project_id}/duplicate",status_code=201)
def duplicate_project(project_id:UUID,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    source=db.get(ProjectTemplate,project_id)
    if not source: raise HTTPException(404,"Project not found")
    slug=f"{source.slug}-copy";suffix=1
    while db.scalar(select(ProjectTemplate).where(ProjectTemplate.slug==slug)): suffix+=1;slug=f"{source.slug}-copy-{suffix}"
    values={key:getattr(source,key) for key in ("category_id","title","description_en","description_mm","difficulty","estimated_hours","requirements","learning_outcomes","technology_stack","prerequisites","architecture_overview","folder_structure","testing_guide","deployment_guide","cover_image","tags_json","languages_json","brief_json")};values["title"]=f"{source.title} (Copy)";values["slug"]=slug;values["published"]=False;values["status"]="draft";values["created_by"]=user.id
    row=ProjectTemplate(**values);db.add(row);db.flush(); source_milestones=db.scalars(select(ProjectMilestone).where(ProjectMilestone.project_id==source.id)).all(); milestone_map={}
    for milestone in source_milestones:
        copied=ProjectMilestone(project_id=row.id,title=milestone.title,slug=milestone.slug,description_en=milestone.description_en,description_mm=milestone.description_mm,content_en=milestone.content_en,content_mm=milestone.content_mm,code=milestone.code,filename=milestone.filename,expected_output=milestone.expected_output,line_explanation=milestone.line_explanation,completion_criteria=milestone.completion_criteria,resources_json=milestone.resources_json,position=milestone.position,required=milestone.required);db.add(copied);db.flush();milestone_map[milestone.id]=copied.id
        for task in db.scalars(select(ProjectTask).where(ProjectTask.milestone_id==milestone.id)).all(): db.add(ProjectTask(milestone_id=copied.id,title=task.title,description=task.description,completion_criteria=task.completion_criteria,position=task.position,required=task.required))
    for requirement in db.scalars(select(ProjectRequirement).where(ProjectRequirement.project_id==source.id)).all(): db.add(ProjectRequirement(project_id=row.id,title=requirement.title,description=requirement.description,acceptance_criteria=requirement.acceptance_criteria,required=requirement.required,position=requirement.position))
    for resource in db.scalars(select(ProjectResource).where(ProjectResource.project_id==source.id)).all(): db.add(ProjectResource(project_id=row.id,milestone_id=milestone_map.get(resource.milestone_id),title=resource.title,resource_type=resource.resource_type,url=resource.url,storage_key=resource.storage_key,description=resource.description,position=resource.position,is_public=False,status="draft"))
    for criterion in db.scalars(select(ProjectRubricCriterion).where(ProjectRubricCriterion.project_id==source.id)).all(): db.add(ProjectRubricCriterion(project_id=row.id,name=criterion.name,description=criterion.description,weight=criterion.weight,position=criterion.position))
    audit(db,user,"project_duplicated","project",row.id);db.commit();return {"id":row.id,"slug":row.slug,"published":False}
@router.post("/admin/projects/{project_id}/publish")
def publish_project(project_id:UUID,payload:dict,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(ProjectTemplate,project_id)
    if not row: raise HTTPException(404,"Project not found")
    publish=bool(payload.get("published",True));quality=project_quality(row,db)
    if publish and not quality["ready"]: raise HTTPException(422,{"message":"Project content is not ready to publish","missing":quality["missing"]})
    row.published=publish;row.status="published" if publish else "draft";audit(db,user,"project_published" if publish else "project_unpublished","project",row.id);db.commit();return {"id":row.id,"published":row.published,"status":row.status,"quality":quality}
@router.post("/admin/projects/{project_id}/archive")
def archive_project(project_id:UUID,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(ProjectTemplate,project_id)
    if not row: raise HTTPException(404,"Project not found")
    row.published=False;row.status="archived";audit(db,user,"project_archived","project",row.id);db.commit();return {"id":row.id,"status":row.status,"published":False}
@router.post("/admin/projects/{project_id}/milestones",status_code=201)
def create_milestone(project_id:UUID,payload:dict,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    if not db.get(ProjectTemplate,project_id): raise HTTPException(404,"Project not found")
    row=ProjectMilestone(project_id=project_id,title=str(payload.get("title","")),slug=str(payload.get("slug", "")),description_en=str(payload.get("description_en","")),description_mm=payload.get("description_mm"),content_en=str(payload.get("content_en",payload.get("description_en",""))),content_mm=payload.get("content_mm"),code=str(payload.get("code","")),filename=payload.get("filename"),expected_output=str(payload.get("expected_output","")),line_explanation=str(payload.get("line_explanation","")),completion_criteria=str(payload.get("completion_criteria","")),resources_json=json.dumps(payload.get("resources",[])),position=int(payload.get("position",0)),required=bool(payload.get("required",True)));db.add(row);db.commit();return {"id":row.id,"project_id":row.project_id,"position":row.position}

def project_or_404(project_id, db):
    row=db.get(ProjectTemplate,project_id)
    if not row: raise HTTPException(404,"Project not found")
    return row
def milestone_or_404(project_id, milestone_id, db):
    row=db.scalar(select(ProjectMilestone).where(ProjectMilestone.id==milestone_id,ProjectMilestone.project_id==project_id))
    if not row: raise HTTPException(404,"Project milestone not found")
    return row
def reorder_rows(rows, positions):
    requested=[]
    try: requested=[UUID(str(item.get("id"))) for item in positions]
    except (TypeError, ValueError): raise HTTPException(422,"Ordering contains an invalid item id")
    if set(requested)!={row.id for row in rows} or len(requested)!=len(rows): raise HTTPException(422,"Ordering must include every item exactly once")
    for index,row in enumerate(sorted(rows,key=lambda item:item.position)): row.position=100000+index
    for index,item_id in enumerate(requested): next(row for row in rows if row.id==item_id).position=index

@router.patch("/admin/projects/{project_id}/milestones/{milestone_id}")
def update_milestone(project_id:UUID,milestone_id:UUID,payload:dict,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=milestone_or_404(project_id,milestone_id,db)
    allowed={"title","slug","description_en","description_mm","content_en","content_mm","code","filename","expected_output","line_explanation","completion_criteria","position","required"}
    for key,value in payload.items():
        if key in allowed: setattr(row,key,value)
    if "resources" in payload: row.resources_json=json.dumps(payload.get("resources") or [])
    db.commit(); return {"id":row.id,"project_id":row.project_id,"position":row.position}

@router.delete("/admin/projects/{project_id}/milestones/{milestone_id}")
def delete_milestone(project_id:UUID,milestone_id:UUID,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=milestone_or_404(project_id,milestone_id,db); db.delete(row); db.commit(); return {"deleted":True}

@router.post("/admin/projects/{project_id}/milestones/reorder")
def reorder_milestones(project_id:UUID,payload:dict,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    project_or_404(project_id,db); rows=db.scalars(select(ProjectMilestone).where(ProjectMilestone.project_id==project_id)).all(); reorder_rows(rows,payload.get("items",[])); db.commit(); return {"items":[row.id for row in sorted(rows,key=lambda item:item.position)]}

@router.get("/admin/projects/{project_id}/requirements")
def list_requirements(project_id:UUID,user:User=Depends(admin_user),db:Session=Depends(get_db)):
    project_or_404(project_id,db); return db.scalars(select(ProjectRequirement).where(ProjectRequirement.project_id==project_id).order_by(ProjectRequirement.position)).all()

@router.post("/admin/projects/{project_id}/requirements",status_code=201)
def create_requirement(project_id:UUID,payload:dict,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    project_or_404(project_id,db); row=ProjectRequirement(project_id=project_id,title=str(payload.get("title","")).strip(),description=str(payload.get("description","")),acceptance_criteria=str(payload.get("acceptance_criteria","")),required=bool(payload.get("required",True)),position=int(payload.get("position",0)))
    if not row.title: raise HTTPException(422,"Requirement title is required")
    db.add(row);db.commit();return {"id":row.id}

@router.patch("/admin/projects/{project_id}/requirements/{requirement_id}")
def update_requirement(project_id:UUID,requirement_id:UUID,payload:dict,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    project_or_404(project_id,db); row=db.scalar(select(ProjectRequirement).where(ProjectRequirement.id==requirement_id,ProjectRequirement.project_id==project_id));
    if not row: raise HTTPException(404,"Requirement not found")
    for key in ("title","description","acceptance_criteria","required","position"):
        if key in payload: setattr(row,key,payload[key])
    if not row.title.strip(): raise HTTPException(422,"Requirement title is required")
    db.commit();return {"id":row.id}

@router.delete("/admin/projects/{project_id}/requirements/{requirement_id}")
def delete_requirement(project_id:UUID,requirement_id:UUID,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    project_or_404(project_id,db); row=db.scalar(select(ProjectRequirement).where(ProjectRequirement.id==requirement_id,ProjectRequirement.project_id==project_id));
    if not row: raise HTTPException(404,"Requirement not found")
    db.delete(row);db.commit();return {"deleted":True}

@router.post("/admin/projects/{project_id}/requirements/reorder")
def reorder_requirements(project_id:UUID,payload:dict,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    project_or_404(project_id,db); rows=db.scalars(select(ProjectRequirement).where(ProjectRequirement.project_id==project_id)).all();reorder_rows(rows,payload.get("items",[]));db.commit();return {"items":[row.id for row in sorted(rows,key=lambda item:item.position)]}

@router.post("/admin/projects/{project_id}/milestones/{milestone_id}/tasks",status_code=201)
def create_task(project_id:UUID,milestone_id:UUID,payload:dict,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    milestone_or_404(project_id,milestone_id,db); row=ProjectTask(milestone_id=milestone_id,title=str(payload.get("title","")).strip(),description=str(payload.get("description","")),completion_criteria=str(payload.get("completion_criteria","")),position=int(payload.get("position",0)),required=bool(payload.get("required",True)))
    if not row.title: raise HTTPException(422,"Task title is required")
    db.add(row);db.commit();return {"id":row.id}

@router.patch("/admin/projects/{project_id}/milestones/{milestone_id}/tasks/{task_id}")
def update_task(project_id:UUID,milestone_id:UUID,task_id:UUID,payload:dict,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    milestone_or_404(project_id,milestone_id,db); row=db.scalar(select(ProjectTask).where(ProjectTask.id==task_id,ProjectTask.milestone_id==milestone_id));
    if not row: raise HTTPException(404,"Task not found")
    for key in ("title","description","completion_criteria","position","required"):
        if key in payload:setattr(row,key,payload[key])
    if not row.title.strip():raise HTTPException(422,"Task title is required")
    db.commit();return {"id":row.id}

@router.delete("/admin/projects/{project_id}/milestones/{milestone_id}/tasks/{task_id}")
def delete_task(project_id:UUID,milestone_id:UUID,task_id:UUID,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    milestone_or_404(project_id,milestone_id,db); row=db.scalar(select(ProjectTask).where(ProjectTask.id==task_id,ProjectTask.milestone_id==milestone_id));
    if not row:raise HTTPException(404,"Task not found")
    db.delete(row);db.commit();return {"deleted":True}

@router.post("/admin/projects/{project_id}/milestones/{milestone_id}/tasks/reorder")
def reorder_tasks(project_id:UUID,milestone_id:UUID,payload:dict,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    milestone_or_404(project_id,milestone_id,db); rows=db.scalars(select(ProjectTask).where(ProjectTask.milestone_id==milestone_id)).all(); reorder_rows(rows,payload.get("items",[])); db.commit(); return {"items":[row.id for row in sorted(rows,key=lambda item:item.position)]}

@router.get("/admin/projects/{project_id}/resources")
def list_resources(project_id:UUID,user:User=Depends(admin_user),db:Session=Depends(get_db)):
    project_or_404(project_id,db);return db.scalars(select(ProjectResource).where(ProjectResource.project_id==project_id).order_by(ProjectResource.position)).all()

@router.post("/admin/projects/{project_id}/resources",status_code=201)
def create_resource(project_id:UUID,payload:dict,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    project_or_404(project_id,db); resource_type=str(payload.get("resource_type","link")); url=payload.get("url");
    if resource_type in {"link","repository","docs"}:
        if not url: raise HTTPException(422,"A resource URL is required")
        safe_url(url,resource_type=="repository")
    storage_key=payload.get("storage_key")
    if storage_key and (".." in storage_key or storage_key.startswith("/") or not storage_key.startswith("projects/")): raise HTTPException(422,"Invalid resource storage key")
    row=ProjectResource(project_id=project_id,milestone_id=payload.get("milestone_id"),title=str(payload.get("title","")).strip(),resource_type=resource_type,url=url,storage_key=storage_key,description=str(payload.get("description","")),position=int(payload.get("position",0)),is_public=bool(payload.get("is_public",False)),status=str(payload.get("status","draft")))
    if not row.title:raise HTTPException(422,"Resource title is required")
    db.add(row);db.commit();return {"id":row.id}

@router.patch("/admin/projects/{project_id}/resources/{resource_id}")
def update_resource(project_id:UUID,resource_id:UUID,payload:dict,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    project_or_404(project_id,db); row=db.scalar(select(ProjectResource).where(ProjectResource.id==resource_id,ProjectResource.project_id==project_id));
    if not row:raise HTTPException(404,"Resource not found")
    for key in ("title","resource_type","url","storage_key","description","position","is_public","status","milestone_id"):
        if key in payload:setattr(row,key,payload[key])
    if row.url:safe_url(row.url,row.resource_type=="repository")
    if row.storage_key and (".." in row.storage_key or row.storage_key.startswith("/") or not row.storage_key.startswith("projects/")):raise HTTPException(422,"Invalid resource storage key")
    db.commit();return {"id":row.id}

@router.delete("/admin/projects/{project_id}/resources/{resource_id}")
def delete_resource(project_id:UUID,resource_id:UUID,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    project_or_404(project_id,db); row=db.scalar(select(ProjectResource).where(ProjectResource.id==resource_id,ProjectResource.project_id==project_id));
    if not row:raise HTTPException(404,"Resource not found")
    db.delete(row);db.commit();return {"deleted":True}

@router.post("/admin/projects/{project_id}/rubric",status_code=201)
def create_rubric(project_id:UUID,payload:dict,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    project_or_404(project_id,db); name=str(payload.get("name","")).strip(); weight=int(payload.get("weight",0));
    if not name or weight<0 or weight>100:raise HTTPException(422,"Rubric name and a weight from 0 to 100 are required")
    row=ProjectRubricCriterion(project_id=project_id,name=name,description=str(payload.get("description","")),weight=weight,position=int(payload.get("position",0)));db.add(row);db.commit();return {"id":row.id}

@router.patch("/admin/projects/{project_id}/rubric/{criterion_id}")
def update_rubric(project_id:UUID,criterion_id:UUID,payload:dict,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    project_or_404(project_id,db); row=db.scalar(select(ProjectRubricCriterion).where(ProjectRubricCriterion.id==criterion_id,ProjectRubricCriterion.project_id==project_id));
    if not row:raise HTTPException(404,"Rubric criterion not found")
    for key in ("name","description","weight","position"):
        if key in payload:setattr(row,key,payload[key])
    if not row.name.strip() or row.weight<0 or row.weight>100:raise HTTPException(422,"Invalid rubric criterion")
    db.commit();return {"id":row.id}

@router.delete("/admin/projects/{project_id}/rubric/{criterion_id}")
def delete_rubric(project_id:UUID,criterion_id:UUID,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    project_or_404(project_id,db); row=db.scalar(select(ProjectRubricCriterion).where(ProjectRubricCriterion.id==criterion_id,ProjectRubricCriterion.project_id==project_id));
    if not row:raise HTTPException(404,"Rubric criterion not found")
    db.delete(row);db.commit();return {"deleted":True}

@router.post("/admin/projects/{project_id}/rubric/reorder")
def reorder_rubric(project_id:UUID,payload:dict,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    project_or_404(project_id,db); rows=db.scalars(select(ProjectRubricCriterion).where(ProjectRubricCriterion.project_id==project_id)).all(); reorder_rows(rows,payload.get("items",[])); db.commit(); return {"items":[row.id for row in sorted(rows,key=lambda item:item.position)]}

@router.get("/admin/project-metrics")
def project_metrics(user:User=Depends(admin_user),db:Session=Depends(get_db)):
    return {"total":db.scalar(select(func.count(ProjectTemplate.id))) or 0,"published":db.scalar(select(func.count(ProjectTemplate.id)).where(ProjectTemplate.published.is_(True))) or 0,"drafts":db.scalar(select(func.count(ProjectTemplate.id)).where(ProjectTemplate.status=="draft")) or 0,"archived":db.scalar(select(func.count(ProjectTemplate.id)).where(ProjectTemplate.status=="archived")) or 0,"submissions_pending":db.scalar(select(func.count(ProjectSubmission.id)).where(ProjectSubmission.status.in_(["submitted","in_review","changes_requested"]))) or 0,"students_started":db.scalar(select(func.count(StudentProject.id))) or 0}

@router.get("/admin/project-submissions")
def admin_project_submissions(status:str|None=None,search:str|None=None,user:User=Depends(admin_user),db:Session=Depends(get_db)):
    q=select(ProjectSubmission,StudentProject,ProjectTemplate).join(StudentProject,StudentProject.id==ProjectSubmission.student_project_id).join(ProjectTemplate,ProjectTemplate.id==StudentProject.project_id)
    if status:q=q.where(ProjectSubmission.status==status)
    if search:q=q.where(ProjectTemplate.title.ilike(f"%{search}%"))
    rows=db.execute(q.order_by(ProjectSubmission.created_at.desc())).all()
    return [{"id":submission.id,"status":submission.status,"submitted_at":submission.submitted_at,"repository_url":submission.repository_url,"demo_url":submission.demo_url,"attachment_name":submission.attachment_name,"attachment_size":submission.attachment_size,"has_attachment":bool(submission.attachment_key),"project_id":template.id,"project_title":template.title,"student_project_id":student.id} for submission,student,template in rows]


@router.get("/admin/project-submissions/{submission_id}/download")
def download_admin_project_submission(submission_id: UUID, user: User = Depends(admin_user), db: Session = Depends(get_db)):
    submission = db.get(ProjectSubmission, submission_id)
    if not submission:
        raise HTTPException(404, "Submission not found")
    path = _submission_attachment_path(submission)
    return FileResponse(path, media_type="application/zip", filename=submission.attachment_name or "project-submission.zip")
