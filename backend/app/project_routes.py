import ipaddress
from datetime import datetime, timezone
from urllib.parse import urlparse
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .auth import current_user, require_csrf, verified_user
from .db import get_db
from .models import (PortfolioProject, ProjectAuditLog, ProjectBookmark, ProjectCategory, ProjectFeedback, ProjectMilestone, ProjectReview, ProjectReviewScore, ProjectRubricCriterion, ProjectSubmission, ProjectTemplate, ProjectSkill, StudentPortfolio, StudentProject, StudentProjectMilestone, SkillDefinition, VerifiedProjectSkill, User)
from .admin_routes import admin_user, full_admin, audit

router=APIRouter(prefix="/api/v1",tags=["projects"])
class SubmissionIn(BaseModel): repository_url:str; branch_or_sha:str=Field(min_length=1,max_length=180); demo_url:str|None=None; project_description:str=""; setup_instructions:str=""; reviewer_notes:str=""
class MilestoneIn(BaseModel): completed:bool; notes:str=""
class ProjectIn(BaseModel): title:str=Field(min_length=1,max_length=180); slug:str=Field(pattern=r"^[a-z0-9-]+$"); description_en:str=Field(min_length=1); description_mm:str|None=None; difficulty:str; category_id:UUID|None=None; estimated_hours:int=Field(default=0,ge=0); requirements:str=""; learning_outcomes:str=""; technology_stack:str=""; prerequisites:str=""; architecture_overview:str=""; folder_structure:str=""; testing_guide:str=""; deployment_guide:str=""
class ReviewIn(BaseModel): decision:str; comments:str=""; scores:dict[UUID,int]={}
class PortfolioIn(BaseModel): username:str=Field(pattern=r"^[a-z0-9-]{3,80}$"); headline:str=""; bio:str=""; github_url:str|None=None; visibility:str="private"
def safe_url(value:str,github=False):
    try: parsed=urlparse(value)
    except ValueError: raise HTTPException(422,"Invalid URL")
    host=(parsed.hostname or "").lower(); allowed={"github.com","www.github.com"} if github else {"http:","https:"}
    if github and host not in allowed: raise HTTPException(422,"Repository must be a GitHub URL")
    if not github and parsed.scheme not in allowed: raise HTTPException(422,"URL must use HTTP or HTTPS")
    if not parsed.netloc or parsed.username or parsed.password: raise HTTPException(422,"Unsafe URL")
    if host in {"localhost","127.0.0.1","::1"}:
        raise HTTPException(422,"Local URLs are not allowed")
    try:
        if ipaddress.ip_address(host).is_private: raise HTTPException(422,"Private network URLs are not allowed")
    except ValueError: pass
    return value
def template_out(row,db):
    milestones=db.scalars(select(ProjectMilestone).where(ProjectMilestone.project_id==row.id).order_by(ProjectMilestone.position)).all(); criteria=db.scalars(select(ProjectRubricCriterion).where(ProjectRubricCriterion.project_id==row.id).order_by(ProjectRubricCriterion.position)).all(); category=db.get(ProjectCategory,row.category_id) if row.category_id else None
    return {"id":row.id,"title":row.title,"slug":row.slug,"description_en":row.description_en,"description_mm":row.description_mm,"difficulty":row.difficulty,"estimated_hours":row.estimated_hours,"requirements":row.requirements,"learning_outcomes":row.learning_outcomes,"technology_stack":row.technology_stack,"prerequisites":row.prerequisites,"architecture_overview":row.architecture_overview,"folder_structure":row.folder_structure,"testing_guide":row.testing_guide,"deployment_guide":row.deployment_guide,"category":{"id":category.id,"name":category.name,"slug":category.slug} if category else None,"status":row.status,"published":row.published,"milestones":[{"id":m.id,"title":m.title,"slug":m.slug or f"step-{m.position}","description_en":m.description_en,"description_mm":m.description_mm,"content_en":m.content_en,"content_mm":m.content_mm,"code":m.code,"filename":m.filename,"expected_output":m.expected_output,"line_explanation":m.line_explanation,"position":m.position,"required":m.required} for m in milestones],"rubric":[{"id":c.id,"name":c.name,"weight":c.weight,"position":c.position} for c in criteria]}
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
    total=db.scalar(count) or 0;rows=db.scalars(q.order_by(ProjectTemplate.title).offset((page-1)*page_size).limit(page_size)).all();return {"items":[template_out(x,db) for x in rows],"page":page,"page_size":page_size,"total":total,"pages":(total+page_size-1)//page_size if total else 0}
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
    return template_out(row,db)
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
    rows=db.scalars(select(StudentProject).where(StudentProject.user_id==user.id).order_by(StudentProject.created_at.desc())).all();return [{"id":r.id,"project_id":r.project_id,"status":r.status,"progress":project_progress(db,r)} for r in rows]
@router.get("/me/projects/{project_id}")
def my_project(project_id:UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):
    row=db.scalar(select(StudentProject).where(StudentProject.id==project_id,StudentProject.user_id==user.id));
    if not row:raise HTTPException(404,"Project not found")
    milestones=db.scalars(select(StudentProjectMilestone).where(StudentProjectMilestone.student_project_id==row.id)).all();submission=db.scalar(select(ProjectSubmission).where(ProjectSubmission.student_project_id==row.id).order_by(ProjectSubmission.created_at.desc()));return {"id":row.id,"status":row.status,"project":template_out(db.get(ProjectTemplate,row.project_id),db),"progress":project_progress(db,row),"milestones":[{"id":m.milestone_id,"completed":m.completed,"notes":m.notes} for m in milestones],"submission":submission}
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
    safe_url(payload.repository_url,True);demo=safe_url(payload.demo_url) if payload.demo_url else None;submission=ProjectSubmission(student_project_id=student.id,repository_url=payload.repository_url,branch_or_sha=payload.branch_or_sha,demo_url=demo,project_description=payload.project_description,setup_instructions=payload.setup_instructions,reviewer_notes=payload.reviewer_notes,status="submitted");db.add(submission);student.status="submitted";db.commit();return {"id":submission.id,"status":submission.status}
@router.get("/instructor/projects/reviews")
def review_queue(user:User=Depends(admin_user),db:Session=Depends(get_db)):
    rows=db.scalars(select(ProjectSubmission).where(ProjectSubmission.status.in_(["submitted","in_review","changes_requested"])).order_by(ProjectSubmission.created_at)).all();return rows
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
    row=db.scalar(select(StudentPortfolio).where(StudentPortfolio.user_id==user.id));return row or {"visibility":"private","projects":[]}
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
    row=ProjectTemplate(**payload.model_dump(),created_by=user.id);db.add(row);audit(db,user,"project_created","project",row.id);db.commit();return {"id":row.id,"slug":row.slug}
@router.post("/admin/projects/{project_id}/milestones",status_code=201)
def create_milestone(project_id:UUID,payload:dict,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=ProjectMilestone(project_id=project_id,title=str(payload.get("title","")),slug=str(payload.get("slug", "")),description_en=str(payload.get("description_en","")),description_mm=payload.get("description_mm"),content_en=str(payload.get("content_en",payload.get("description_en",""))),content_mm=payload.get("content_mm"),code=str(payload.get("code","")),filename=payload.get("filename"),expected_output=str(payload.get("expected_output","")),line_explanation=str(payload.get("line_explanation","")),position=int(payload.get("position",0)),required=bool(payload.get("required",True)));db.add(row);db.commit();return {"id":row.id}
