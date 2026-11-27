import json
import re
from collections import defaultdict
from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, File, HTTPException, Query, Response, UploadFile
from pydantic import BaseModel, Field
from sqlalchemy import and_, exists, func, or_, select
from sqlalchemy.orm import Session
from .auth import current_user, require_csrf, verified_user
from .db import get_db
from .models import (AssessmentDefinition, CareerRoadmap, Challenge, ChallengeSubmission, Course, CourseModule, Lesson, LessonProgress, ProjectTemplate, RoadmapAssessment, RoadmapPrerequisite, RoadmapRevision, RoadmapStage, RoadmapStep, RoadmapStepResource, StudentLearningGoal, StudentProject, StudentRoadmap, StudentRoadmapBookmark, User)
from .admin_routes import admin_user, full_admin, audit
from .media_storage import remove_file_if_safe, save_roadmap_image

router=APIRouter(prefix="/api/v1",tags=["roadmaps"])
class GoalIn(BaseModel): career_goal:str=Field(min_length=1,max_length=100); current_level:str; interests:list[str]=[]; weekly_hours:int=Field(ge=1,le=80); pace:str="steady"; timezone:str="UTC"
class RoadmapIn(BaseModel): title:str=Field(default="",max_length=180); title_mm:str|None=Field(default=None,max_length=180); slug:str=Field(default="",max_length=180); career_category:str=""; description_en:str=""; description_mm:str|None=None; prerequisites_en:str=""; prerequisites_mm:str|None=None; outcomes_en:str=""; outcomes_mm:str|None=None; estimated_hours:int=Field(default=0,ge=0); cover_image:str|None=None; goals:list[str]=[]; skills:list[str]=[]; completion_rules:dict={}
class RoadmapPatch(BaseModel): title:str|None=Field(default=None,max_length=180); title_mm:str|None=Field(default=None,max_length=180); slug:str|None=Field(default=None,max_length=180); career_category:str|None=None; description_en:str|None=None; description_mm:str|None=None; prerequisites_en:str|None=None; prerequisites_mm:str|None=None; outcomes_en:str|None=None; outcomes_mm:str|None=None; estimated_hours:int|None=Field(default=None,ge=0); cover_image:str|None=None; goals:list[str]|None=None; skills:list[str]|None=None; completion_rules:dict|None=None
class StageIn(BaseModel): title:str; title_mm:str|None=None; description_en:str=""; description_mm:str|None=None; level:str="beginner"; objectives:list[str]=[]; skills:list[str]=[]; completion_rules:dict={}; position:int=Field(default=0,ge=0)
class StagePatch(BaseModel): title:str|None=None; title_mm:str|None=None; description_en:str|None=None; description_mm:str|None=None; level:str|None=None; objectives:list[str]|None=None; skills:list[str]|None=None; completion_rules:dict|None=None; position:int|None=Field(default=None,ge=0)
class StepIn(BaseModel): title:str; title_mm:str|None=None; instructions_en:str=""; instructions_mm:str|None=None; position:int=Field(default=0,ge=0); required:bool=True
class StepPatch(BaseModel): title:str|None=None; title_mm:str|None=None; instructions_en:str|None=None; instructions_mm:str|None=None; position:int|None=Field(default=None,ge=0); required:bool|None=None
class OrderIn(BaseModel): ids:list[UUID]
class PrereqIn(BaseModel): prerequisite_step_id:UUID
class ResourceIn(BaseModel): resource_type:str; resource_id:UUID
class AssessmentLinkIn(BaseModel): assessment_id:UUID; passing_score:int=Field(default=70,ge=0,le=100); required:bool=True; position:int=Field(default=0,ge=0)
def json_load(value, fallback):
    try: return json.loads(value or "")
    except (TypeError, ValueError, json.JSONDecodeError): return fallback
def localized(en: str | None, mm: str | None, locale: str) -> tuple[str, str, bool]:
    source = (en or "").strip()
    translated = (mm or "").strip()
    if locale == "my" and translated:
        return translated, "my", True
    return source, "en", bool(translated)

def translation_is_ready(source: str | None, translated: str | None, required: bool = False) -> bool:
    """Return whether a Burmese value is required and present.

    Optional English fields do not need an empty Burmese counterpart. Required
    labels such as titles still need an explicit Burmese value.
    """
    return (not required and not (source or "").strip()) or bool((translated or "").strip())

def roadmap_translation_missing(row, stages, steps_by_stage):
    missing = []
    fields = (
        ("title", row.title, row.title_mm, True),
        ("description", row.description_en, row.description_mm, False),
        ("prerequisites", row.prerequisites_en, row.prerequisites_mm, False),
        ("outcomes", row.outcomes_en, row.outcomes_mm, False),
    )
    for label, source, translated, required in fields:
        if not translation_is_ready(source, translated, required):
            missing.append(label)
    for stage in stages:
        if not translation_is_ready(stage.title, stage.title_mm, True):
            missing.append(f"stage:{stage.position}:title")
        if not translation_is_ready(stage.description_en, stage.description_mm):
            missing.append(f"stage:{stage.position}:description")
        for step in steps_by_stage.get(stage.id, []):
            if not translation_is_ready(step.title, step.title_mm, True):
                missing.append(f"step:{step.id}:title")
            if not translation_is_ready(step.instructions_en, step.instructions_mm):
                missing.append(f"step:{step.id}:instructions")
    return missing

def step_dict(step,db,locale="en"):
    resources=[]
    for resource in db.scalars(select(RoadmapStepResource).where(RoadmapStepResource.step_id==step.id)).all():
        item={"resource_type":resource.resource_type,"resource_id":resource.resource_id,"slug":None,"title":None,"course_slug":None,"href":None}
        model={"course":Course,"lesson":Lesson,"project":ProjectTemplate,"challenge":Challenge}.get(resource.resource_type)
        if model:
            target=db.get(model,resource.resource_id)
            if target:
                item.update({"slug":target.slug,"title":getattr(target,"title",None)})
                if resource.resource_type == "course": item["href"] = f"/courses/{target.slug}"
                elif resource.resource_type == "project": item["href"] = f"/projects/{target.slug}"
                elif resource.resource_type == "challenge": item["href"] = f"/challenges/{target.slug}"
                if resource.resource_type=="lesson":
                    module=db.get(CourseModule,target.module_id);course=db.get(Course,module.course_id) if module else None
                    item["course_slug"]=course.slug if course else None
                    item["href"] = f"/courses/{course.slug}/learn/{target.slug}" if course else None
        resources.append(item)
    step_title,step_locale,step_title_translated=localized(step.title,step.title_mm,locale)
    step_instructions,step_instructions_locale,step_instructions_translated=localized(step.instructions_en,step.instructions_mm,locale)
    step_ready = translation_is_ready(step.title, step.title_mm, True) and translation_is_ready(step.instructions_en, step.instructions_mm)
    return {"id":step.id,"title":step_title,"title_en":step.title,"title_mm":step.title_mm,"instructions":step_instructions,"instructions_en":step.instructions_en,"instructions_mm":step.instructions_mm,"position":step.position,"required":step.required,"resources":resources,"resolved_locale":locale if locale == "en" or step_ready else "en"}
def roadmap_dict(row,db,include_steps=True,locale="en"):
    title,resolved_title,title_translated=localized(row.title,row.title_mm,locale); description,resolved_description,description_translated=localized(row.description_en,row.description_mm,locale); prerequisites,resolved_prerequisites,prerequisites_translated=localized(row.prerequisites_en,row.prerequisites_mm,locale); outcomes,resolved_outcomes,outcomes_translated=localized(row.outcomes_en,row.outcomes_mm,locale)
    stages=db.scalars(select(RoadmapStage).where(RoadmapStage.roadmap_id==row.id).order_by(RoadmapStage.position)).all()
    steps_by_stage=defaultdict(list)
    if stages:
        for step in db.scalars(select(RoadmapStep).where(RoadmapStep.stage_id.in_([stage.id for stage in stages])).order_by(RoadmapStep.stage_id, RoadmapStep.position)).all():
            steps_by_stage[step.stage_id].append(step)
    translation_missing=roadmap_translation_missing(row, stages, steps_by_stage)
    translation_available=not translation_missing
    assessments=db.scalars(select(RoadmapAssessment).where(RoadmapAssessment.roadmap_id==row.id).order_by(RoadmapAssessment.position)).all(); out={"id":row.id,"title":title,"title_en":row.title,"title_mm":row.title_mm,"slug":row.slug,"career_category":row.career_category,"description":description,"description_en":row.description_en,"description_mm":row.description_mm,"prerequisites":prerequisites,"prerequisites_en":row.prerequisites_en,"prerequisites_mm":row.prerequisites_mm,"outcomes":outcomes,"outcomes_en":row.outcomes_en,"outcomes_mm":row.outcomes_mm,"estimated_hours":row.estimated_hours,"cover_image":row.cover_image,"goals":json_load(row.goals_json,[]),"skills":json_load(row.skills_json,[]),"completion_rules":json_load(row.completion_rules_json,{}),"status":row.status,"published":row.published,"requested_locale":locale,"resolved_locale":"my" if locale == "my" and translation_available else "en","translation_available":translation_available,"translation_missing":translation_missing,"stages":[],"assessments":[{"id":a.id,"assessment_id":a.assessment_id,"passing_score":a.passing_score,"required":a.required,"position":a.position,"title":getattr(db.get(AssessmentDefinition,a.assessment_id),"title",None)} for a in assessments]}
    out["stages"]=[{"id":s.id,"title":localized(s.title,s.title_mm,locale)[0],"title_en":s.title,"title_mm":s.title_mm,"description":localized(s.description_en,s.description_mm,locale)[0],"description_en":s.description_en,"description_mm":s.description_mm,"level":s.level,"objectives":json_load(s.objectives_json,[]),"skills":json_load(s.skills_json,[]),"completion_rules":json_load(s.completion_rules_json,{}),"position":s.position,"steps":[step_dict(x,db,locale) for x in steps_by_stage[s.id]] if include_steps else []} for s in stages]
    step_ids=select(RoadmapStep.id).join(RoadmapStage).where(RoadmapStage.roadmap_id==row.id)
    resources=db.scalars(select(RoadmapStepResource).where(RoadmapStepResource.step_id.in_(step_ids))).all()
    out["stage_count"]=len(stages); out["step_count"]=db.scalar(select(func.count(RoadmapStep.id)).join(RoadmapStage).where(RoadmapStage.roadmap_id==row.id)) or 0; out["course_count"]=len({r.resource_id for r in resources if r.resource_type=="course"}); out["project_count"]=len({r.resource_id for r in resources if r.resource_type=="project"})
    return out
def admin_roadmap_dict(row,db,include_steps=True):
    result=roadmap_dict(row,db,include_steps,"en")
    burmese=roadmap_dict(row,db,include_steps,"my")
    result["translation_available"]=burmese["translation_available"]
    result["translation_missing"]=burmese["translation_missing"]
    return result
def evidence_complete(db,user_id,step_id):
    resources=db.scalars(select(RoadmapStepResource).where(RoadmapStepResource.step_id==step_id)).all()
    for r in resources:
        if r.resource_type=="challenge" and db.scalar(select(ChallengeSubmission.id).where(ChallengeSubmission.user_id==user_id,ChallengeSubmission.challenge_id==r.resource_id,ChallengeSubmission.status=="accepted")): return True
        if r.resource_type=="project" and db.scalar(select(StudentProject.id).where(StudentProject.user_id==user_id,StudentProject.project_id==r.resource_id,StudentProject.status=="approved")): return True
        if r.resource_type=="lesson" and db.scalar(select(LessonProgress.id).where(LessonProgress.user_id==user_id,LessonProgress.lesson_id==r.resource_id,LessonProgress.completed.is_(True))): return True
        if r.resource_type=="course":
            total=db.scalar(select(func.count(Lesson.id)).join(CourseModule).where(CourseModule.course_id==r.resource_id,Lesson.published.is_(True))) or 0; done=db.scalar(select(func.count(LessonProgress.id)).join(Lesson,Lesson.id==LessonProgress.lesson_id).join(CourseModule,CourseModule.id==Lesson.module_id).where(LessonProgress.user_id==user_id,CourseModule.course_id==r.resource_id,Lesson.published.is_(True),LessonProgress.completed.is_(True))) or 0
            if total and total==done: return True
    return False
def progress_view(db,enrollment):
    steps=db.scalars(select(RoadmapStep).join(RoadmapStage).where(RoadmapStage.roadmap_id==enrollment.roadmap_id).order_by(RoadmapStage.position,RoadmapStep.position)).all()
    required_steps=[step for step in steps if step.required] or steps
    step_ids=[step.id for step in required_steps]
    resources=db.scalars(select(RoadmapStepResource).where(RoadmapStepResource.step_id.in_(step_ids))).all() if step_ids else []
    by_step=defaultdict(list)
    for resource in resources: by_step[resource.step_id].append(resource)
    course_ids={r.resource_id for r in resources if r.resource_type=="course"}; lesson_ids={r.resource_id for r in resources if r.resource_type=="lesson"}; challenge_ids={r.resource_id for r in resources if r.resource_type=="challenge"}; project_ids={r.resource_id for r in resources if r.resource_type=="project"}
    completed_lessons=set(db.scalars(select(LessonProgress.lesson_id).where(LessonProgress.user_id==enrollment.user_id,LessonProgress.lesson_id.in_(lesson_ids),LessonProgress.completed.is_(True))).all()) if lesson_ids else set()
    course_totals=dict(db.execute(select(Course.id,func.count(Lesson.id)).join(CourseModule,CourseModule.course_id==Course.id).join(Lesson,Lesson.module_id==CourseModule.id).where(Course.id.in_(course_ids),Lesson.published.is_(True)).group_by(Course.id)).all()) if course_ids else {}
    course_done=dict(db.execute(select(Course.id,func.count(LessonProgress.id)).join(CourseModule,CourseModule.course_id==Course.id).join(Lesson,Lesson.module_id==CourseModule.id).join(LessonProgress,LessonProgress.lesson_id==Lesson.id).where(Course.id.in_(course_ids),Lesson.published.is_(True),LessonProgress.user_id==enrollment.user_id,LessonProgress.completed.is_(True)).group_by(Course.id)).all()) if course_ids else {}
    completed_courses={course_id for course_id,total in course_totals.items() if total and course_done.get(course_id,0)>=total}
    completed_challenges=set(db.scalars(select(ChallengeSubmission.challenge_id).where(ChallengeSubmission.user_id==enrollment.user_id,ChallengeSubmission.challenge_id.in_(challenge_ids),ChallengeSubmission.status=="accepted")).all()) if challenge_ids else set()
    completed_projects=set(db.scalars(select(StudentProject.project_id).where(StudentProject.user_id==enrollment.user_id,StudentProject.project_id.in_(project_ids),StudentProject.status=="approved")).all()) if project_ids else set()
    def is_complete(step):
        return any((resource.resource_type=="lesson" and resource.resource_id in completed_lessons) or (resource.resource_type=="course" and resource.resource_id in completed_courses) or (resource.resource_type=="challenge" and resource.resource_id in completed_challenges) or (resource.resource_type=="project" and resource.resource_id in completed_projects) for resource in by_step.get(step.id,[]))
    completed_steps={step.id for step in required_steps if is_complete(step)}
    stage_rows=db.scalars(select(RoadmapStage).where(RoadmapStage.roadmap_id==enrollment.roadmap_id).order_by(RoadmapStage.position)).all(); stage_progress=[]
    for stage in stage_rows:
        stage_steps=[step for step in required_steps if step.stage_id==stage.id]; stage_done=sum(step.id in completed_steps for step in stage_steps); stage_progress.append({"stage_id":stage.id,"title":stage.title,"position":stage.position,"completed_steps":stage_done,"total_steps":len(stage_steps),"progress_percent":round(stage_done/len(stage_steps)*100,1) if stage_steps else 0})
    resume_rows=[]
    if course_ids:
        resume_rows=db.execute(select(LessonProgress,Lesson.slug,Lesson.title,Course.slug,Course.title).join(Lesson,Lesson.id==LessonProgress.lesson_id).join(CourseModule,CourseModule.id==Lesson.module_id).join(Course,Course.id==CourseModule.course_id).where(LessonProgress.user_id==enrollment.user_id,Course.id.in_(course_ids),Lesson.published.is_(True)).order_by(LessonProgress.completed.asc(),LessonProgress.last_visited_at.desc())).all()
    resume=None
    if resume_rows:
        progress_row,lesson_slug,lesson_title,course_slug,course_title=resume_rows[0]; resume={"lesson_slug":lesson_slug,"lesson_title":lesson_title,"course_slug":course_slug,"course_title":course_title,"href":f"/courses/{course_slug}/learn/{lesson_slug}","last_visited_at":progress_row.last_visited_at}
    last_activity=resume["last_visited_at"] if resume else None
    current=next((step for step in required_steps if step.id not in completed_steps),None)
    return {"completed_steps":len(completed_steps),"total_steps":len(required_steps),"progress_percent":round(len(completed_steps)/len(required_steps)*100,1) if required_steps else 0,"current_step_id":current.id if current else None,"current_stage_id":current.stage_id if current else None,"stage_progress":stage_progress,"last_activity_at":last_activity,"resume":resume}
def public_ready_clause():
    stage_exists=exists(select(RoadmapStage.id).where(RoadmapStage.roadmap_id==CareerRoadmap.id))
    resource_exists=exists(select(RoadmapStepResource.id).join(RoadmapStep,RoadmapStepResource.step_id==RoadmapStep.id).join(RoadmapStage,RoadmapStep.stage_id==RoadmapStage.id).where(RoadmapStage.roadmap_id==CareerRoadmap.id, or_(and_(RoadmapStepResource.resource_type=="course",exists(select(Course.id).where(Course.id==RoadmapStepResource.resource_id,Course.published.is_(True)))), and_(RoadmapStepResource.resource_type=="lesson",exists(select(Lesson.id).where(Lesson.id==RoadmapStepResource.resource_id,Lesson.published.is_(True)))), and_(RoadmapStepResource.resource_type=="project",exists(select(ProjectTemplate.id).where(ProjectTemplate.id==RoadmapStepResource.resource_id,ProjectTemplate.published.is_(True)))), and_(RoadmapStepResource.resource_type=="challenge",exists(select(Challenge.id).where(Challenge.id==RoadmapStepResource.resource_id,Challenge.published.is_(True)))))))
    return and_(CareerRoadmap.published.is_(True), stage_exists, resource_exists)
@router.get("/learning-paths")
@router.get("/roadmaps")
def list_roadmaps(search:str|None=None,career_category:str|None=None,difficulty:str|None=None,duration:str|None=None,technology:str|None=None,sort:str="title",locale:str=Query("en",pattern="^(en|my)$"),page:int=Query(1,ge=1),page_size:int=Query(12,ge=1,le=50),db:Session=Depends(get_db)):
    ready=public_ready_clause(); q=select(CareerRoadmap).where(ready); count=select(func.count()).select_from(CareerRoadmap).where(ready)
    if search:q=q.where(CareerRoadmap.title.ilike(f"%{search}%"));count=count.where(CareerRoadmap.title.ilike(f"%{search}%"))
    if career_category:q=q.where(CareerRoadmap.career_category==career_category);count=count.where(CareerRoadmap.career_category==career_category)
    if difficulty:
        matching=select(RoadmapStage.roadmap_id).where(RoadmapStage.level==difficulty)
        q=q.where(CareerRoadmap.id.in_(matching)); count=count.where(CareerRoadmap.id.in_(matching))
    if duration=="short": q=q.where(CareerRoadmap.estimated_hours<=40); count=count.where(CareerRoadmap.estimated_hours<=40)
    elif duration=="medium": q=q.where(CareerRoadmap.estimated_hours>40,CareerRoadmap.estimated_hours<=120); count=count.where(CareerRoadmap.estimated_hours>40,CareerRoadmap.estimated_hours<=120)
    elif duration=="long": q=q.where(CareerRoadmap.estimated_hours>120); count=count.where(CareerRoadmap.estimated_hours>120)
    if technology:
        term=f"%{technology.strip()}%"; q=q.where(CareerRoadmap.skills_json.ilike(term)); count=count.where(CareerRoadmap.skills_json.ilike(term))
    ordering={"newest":CareerRoadmap.created_at.desc(),"duration_asc":CareerRoadmap.estimated_hours.asc(),"duration_desc":CareerRoadmap.estimated_hours.desc()}.get(sort,CareerRoadmap.title.asc())
    total=db.scalar(count) or 0; rows=db.scalars(q.order_by(ordering).offset((page-1)*page_size).limit(page_size)).all(); return {"items":[roadmap_dict(x,db,False,locale) for x in rows],"page":page,"page_size":page_size,"total":total,"pages":(total+page_size-1)//page_size if total else 0}
@router.get("/learning-paths/categories")
def learning_path_categories(db:Session=Depends(get_db)):
    return db.scalars(select(CareerRoadmap.career_category).where(public_ready_clause()).distinct().order_by(CareerRoadmap.career_category)).all()
@router.get("/learning-paths/{slug}")
@router.get("/roadmaps/{slug}")
def get_roadmap(slug:str,locale:str=Query("en",pattern="^(en|my)$"),db:Session=Depends(get_db)):
    row=db.scalar(select(CareerRoadmap).where(CareerRoadmap.slug==slug,public_ready_clause()))
    if not row: raise HTTPException(404,"Roadmap not found")
    return roadmap_dict(row,db,True,locale)
@router.get("/learning-paths/{slug}/stages")
def roadmap_stages(slug:str,db:Session=Depends(get_db)):
    row=db.scalar(select(CareerRoadmap).where(CareerRoadmap.slug==slug,public_ready_clause()))
    if not row: raise HTTPException(404,"Roadmap not found")
    return roadmap_dict(row,db)["stages"]
@router.get("/learning-paths/{slug}/courses")
def roadmap_courses(slug:str,db:Session=Depends(get_db)):
    row=db.scalar(select(CareerRoadmap).where(CareerRoadmap.slug==slug,public_ready_clause()))
    if not row: raise HTTPException(404,"Roadmap not found")
    resource_ids=db.scalars(select(RoadmapStepResource.resource_id).join(RoadmapStep,RoadmapStepResource.step_id==RoadmapStep.id).join(RoadmapStage,RoadmapStep.stage_id==RoadmapStage.id).where(RoadmapStage.roadmap_id==row.id,RoadmapStepResource.resource_type=="course")).all()
    courses=db.scalars(select(Course).where(Course.id.in_(resource_ids),Course.published.is_(True)).order_by(Course.title)).all() if resource_ids else []
    return [{"id":course.id,"title":course.title,"slug":course.slug,"level":course.level,"duration_minutes":course.duration_minutes} for course in courses]
@router.post("/me/roadmaps/{roadmap_slug}",status_code=201)
def start_roadmap(roadmap_slug:str,response:Response,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    roadmap=db.scalar(select(CareerRoadmap).where(CareerRoadmap.slug==roadmap_slug,CareerRoadmap.published.is_(True)))
    if not roadmap: raise HTTPException(404,"Published roadmap not found")
    existing=db.scalar(select(StudentRoadmap).where(StudentRoadmap.user_id==user.id,StudentRoadmap.roadmap_id==roadmap.id))
    if existing and existing.status=="active": response.status_code=200; return {"id":existing.id,"status":existing.status,"progress":progress_view(db,existing),"idempotent":True}
    if existing: existing.status="active"; existing.paused_at=None; db.commit(); return {"id":existing.id,"status":existing.status,"progress":progress_view(db,existing)}
    row=StudentRoadmap(user_id=user.id,roadmap_id=roadmap.id);db.add(row);db.commit();return {"id":row.id,"status":row.status,"progress":progress_view(db,row)}
@router.post("/learning-paths/{roadmap_id}/enroll",status_code=201)
def enroll_learning_path(roadmap_id:UUID,response:Response,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    roadmap=db.scalar(select(CareerRoadmap).where(CareerRoadmap.id==roadmap_id,CareerRoadmap.published.is_(True)))
    if not roadmap: raise HTTPException(404,"Published learning path not found")
    existing=db.scalar(select(StudentRoadmap).where(StudentRoadmap.user_id==user.id,StudentRoadmap.roadmap_id==roadmap.id))
    if existing and existing.status=="active": response.status_code=200; return {"id":existing.id,"status":existing.status,"progress":progress_view(db,existing),"idempotent":True}
    if existing: existing.status="active"; existing.paused_at=None; db.commit(); return {"id":existing.id,"status":existing.status,"progress":progress_view(db,existing)}
    row=StudentRoadmap(user_id=user.id,roadmap_id=roadmap.id); db.add(row); db.commit(); return {"id":row.id,"status":row.status,"progress":progress_view(db,row)}
@router.get("/me/roadmaps")
def my_roadmaps(user:User=Depends(current_user),locale:str=Query("en",pattern="^(en|my)$"),db:Session=Depends(get_db)):
    rows=db.scalars(select(StudentRoadmap).where(StudentRoadmap.user_id==user.id).order_by(StudentRoadmap.created_at.desc())).all(); bookmarks={x.roadmap_id for x in db.scalars(select(StudentRoadmapBookmark).where(StudentRoadmapBookmark.user_id==user.id)).all()}; items=[]
    for enrollment in rows:
        roadmap=db.get(CareerRoadmap,enrollment.roadmap_id)
        if not roadmap: continue
        progress=progress_view(db,enrollment)
        summary=roadmap_dict(roadmap,db,False,locale)
        items.append({"id":enrollment.id,"roadmap_id":enrollment.roadmap_id,"roadmap_slug":roadmap.slug,"roadmap_title":summary["title"],"status":enrollment.status,"started_at":enrollment.started_at,"bookmarked":enrollment.roadmap_id in bookmarks,"progress":progress})
    return items
@router.get("/me/learning-paths")
def my_learning_paths(user:User=Depends(current_user),db:Session=Depends(get_db)):
    return my_roadmaps(user,db)
@router.get("/me/learning-paths/{roadmap_id}/progress")
def learning_path_progress(roadmap_id:UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):
    return roadmap_progress(roadmap_id,user,db)
@router.get("/me/learning-paths/{roadmap_id}")
def my_learning_path_detail(roadmap_id:UUID,locale:str=Query("en",pattern="^(en|my)$"),user:User=Depends(current_user),db:Session=Depends(get_db)):
    enrollment=db.scalar(select(StudentRoadmap).where(StudentRoadmap.id==roadmap_id,StudentRoadmap.user_id==user.id))
    if not enrollment: raise HTTPException(404,"Learning path enrollment not found")
    roadmap=db.get(CareerRoadmap,enrollment.roadmap_id)
    if not roadmap: raise HTTPException(404,"Learning path not found")
    return {"roadmap":roadmap_dict(roadmap,db,True,locale),"enrollment":{"id":enrollment.id,"status":enrollment.status,"started_at":enrollment.started_at},"progress":progress_view(db,enrollment)}
@router.post("/learning-paths/{roadmap_id}/bookmark")
def bookmark_learning_path(roadmap_id:UUID,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    if not db.scalar(select(CareerRoadmap.id).where(CareerRoadmap.id==roadmap_id,CareerRoadmap.published.is_(True))): raise HTTPException(404,"Published learning path not found")
    item=db.scalar(select(StudentRoadmapBookmark).where(StudentRoadmapBookmark.user_id==user.id,StudentRoadmapBookmark.roadmap_id==roadmap_id))
    if item: db.delete(item); bookmarked=False
    else: db.add(StudentRoadmapBookmark(user_id=user.id,roadmap_id=roadmap_id)); bookmarked=True
    db.commit(); return {"roadmap_id":roadmap_id,"bookmarked":bookmarked}
@router.post("/me/roadmaps/{roadmap_id}/pause")
def pause_roadmap(roadmap_id:UUID,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.scalar(select(StudentRoadmap).where(StudentRoadmap.id==roadmap_id,StudentRoadmap.user_id==user.id));
    if not row: raise HTTPException(404,"Roadmap enrollment not found")
    row.status="paused";row.paused_at=datetime.now(timezone.utc);db.commit();return {"status":row.status}
@router.get("/me/goals")
def get_goal(user:User=Depends(current_user),db:Session=Depends(get_db)):
    row=db.scalar(select(StudentLearningGoal).where(StudentLearningGoal.user_id==user.id)); return None if not row else {"career_goal":row.career_goal,"current_level":row.current_level,"interests":json.loads(row.interests_json),"weekly_hours":row.weekly_hours,"pace":row.pace,"timezone":row.timezone}
@router.put("/me/goals")
def save_goal(payload:GoalIn,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.scalar(select(StudentLearningGoal).where(StudentLearningGoal.user_id==user.id)) or StudentLearningGoal(user_id=user.id); row.career_goal=payload.career_goal;row.current_level=payload.current_level;row.interests_json=json.dumps(payload.interests);row.weekly_hours=payload.weekly_hours;row.pace=payload.pace;row.timezone=payload.timezone;db.add(row);db.commit();return {"status":"saved"}
@router.get("/me/roadmap-recommendations")
def recommendations(user:User=Depends(current_user),db:Session=Depends(get_db)):
    goal=db.scalar(select(StudentLearningGoal).where(StudentLearningGoal.user_id==user.id)); q=select(CareerRoadmap).where(CareerRoadmap.published.is_(True)); rows=db.scalars(q.order_by(CareerRoadmap.title).limit(5)).all(); selected=[x for x in rows if goal and goal.career_goal.lower() in (x.title+" "+x.career_category).lower()]; rows=selected or rows; return [{"resource_type":"roadmap","resource_id":x.id,"title":x.title,"reason":"Matches your learning goal." if goal else "Choose a learning goal to personalize this recommendation."} for x in rows]
@router.get("/me/roadmaps/{roadmap_id}/progress")
def roadmap_progress(roadmap_id:UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):
    row=db.scalar(select(StudentRoadmap).where(StudentRoadmap.id==roadmap_id,StudentRoadmap.user_id==user.id));
    if not row: raise HTTPException(404,"Roadmap enrollment not found")
    return {**progress_view(db,row),"status":row.status}
@router.post("/admin/roadmaps",status_code=201)
def create_roadmap(payload:RoadmapIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    values=payload.model_dump()
    values["slug"] = values["slug"].strip() or re.sub(r"[^a-z0-9]+", "-", values["title"].lower()).strip("-")
    if not values["slug"]: raise HTTPException(422,"A title or slug is required")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", values["slug"]): raise HTTPException(422,"Slug may contain lowercase letters, numbers, and hyphens only")
    if db.scalar(select(CareerRoadmap).where(CareerRoadmap.slug==values["slug"])):raise HTTPException(409,"Slug already exists")
    values["goals_json"] = json.dumps(values.pop("goals"), ensure_ascii=False)
    values["skills_json"] = json.dumps(values.pop("skills"), ensure_ascii=False)
    values["completion_rules_json"] = json.dumps(values.pop("completion_rules"), ensure_ascii=False)
    row=CareerRoadmap(**values,created_by=user.id);db.add(row);audit(db,user,"roadmap_created","roadmap",row.id);db.commit();return {"id":row.id,"slug":row.slug,"status":row.status}
@router.get("/admin/roadmaps")
def admin_roadmaps(search:str|None=None,status:str|None=None,page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=100),user:User=Depends(admin_user),db:Session=Depends(get_db)):
    query=select(CareerRoadmap);count=select(func.count()).select_from(CareerRoadmap)
    if search:
        condition=CareerRoadmap.title.ilike(f"%{search}%")|CareerRoadmap.slug.ilike(f"%{search}%")
        query=query.where(condition);count=count.where(condition)
    if status:
        query=query.where(CareerRoadmap.status==status);count=count.where(CareerRoadmap.status==status)
    total=db.scalar(count) or 0
    rows=db.scalars(query.order_by(CareerRoadmap.updated_at.desc()).offset((page-1)*page_size).limit(page_size)).all()
    return {"items":[admin_roadmap_dict(row,db,False) for row in rows],"page":page,"page_size":page_size,"total":total,"pages":(total+page_size-1)//page_size if total else 0}
def roadmap_quality(row, stages, db):
    errors=[]
    if not row.title.strip(): errors.append("Title is required")
    if not row.slug.strip(): errors.append("Slug is required")
    if not row.description_en.strip(): errors.append("English description is required")
    if not stages: errors.append("At least one stage is required")
    for stage in stages:
        if not stage.title.strip(): errors.append("Every stage needs a title")
        steps=db.scalars(select(RoadmapStep).where(RoadmapStep.stage_id==stage.id)).all()
        if not steps: errors.append(f"Stage '{stage.title}' needs at least one step")
        for step in steps:
            if not step.title.strip(): errors.append("Every step needs a title")
            resources=db.scalars(select(RoadmapStepResource).where(RoadmapStepResource.step_id==step.id)).all()
            if not resources:
                errors.append(f"Step '{step.title}' needs a course, project, or challenge resource")
            for resource in resources:
                model={"course":Course,"lesson":Lesson,"project":ProjectTemplate,"challenge":Challenge}.get(resource.resource_type)
                target=db.get(model,resource.resource_id) if model else None
                if not target: errors.append(f"Step '{step.title}' references missing content")
                elif not getattr(target,"published",True): errors.append(f"Step '{step.title}' references unpublished content")
    return errors

@router.get("/admin/roadmaps/{roadmap_id}")
def admin_roadmap_detail(roadmap_id:UUID,user:User=Depends(admin_user),db:Session=Depends(get_db)):
    row=db.get(CareerRoadmap,roadmap_id)
    if not row: raise HTTPException(404,"Roadmap not found")
    return admin_roadmap_dict(row,db)

@router.get("/admin/roadmaps/{roadmap_id}/preview")
def admin_roadmap_preview(roadmap_id:UUID,user:User=Depends(admin_user),db:Session=Depends(get_db)):
    """Return the current draft to an authorized admin for previewing.

    This intentionally uses the same persisted representation as the editor and
    does not make unpublished content available through the public routes.
    """
    row=db.get(CareerRoadmap,roadmap_id)
    if not row: raise HTTPException(404,"Roadmap not found")
    return admin_roadmap_dict(row,db)

@router.patch("/admin/roadmaps/{roadmap_id}")
def update_roadmap(roadmap_id:UUID,payload:RoadmapPatch,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(CareerRoadmap,roadmap_id)
    if not row: raise HTTPException(404,"Roadmap not found")
    db.add(RoadmapRevision(roadmap_id=row.id,changed_by=user.id,snapshot_json=json.dumps(roadmap_dict(row,db),default=str,ensure_ascii=False)))
    values=payload.model_dump(exclude_unset=True)
    for field in ("goals", "skills", "completion_rules"):
        if field in values:
            setattr(row, f"{field}_json", json.dumps(values.pop(field), ensure_ascii=False))
    if "slug" in values:
        values["slug"]=(values["slug"] or "").strip()
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", values["slug"]): raise HTTPException(422,"Slug may contain lowercase letters, numbers, and hyphens only")
        if db.scalar(select(CareerRoadmap).where(CareerRoadmap.slug==values["slug"],CareerRoadmap.id!=row.id)): raise HTTPException(409,"Slug already exists")
    for field,value in values.items(): setattr(row,field,value)
    audit(db,user,"roadmap_updated","roadmap",row.id);db.commit();return admin_roadmap_dict(row,db)

@router.post("/admin/roadmaps/{roadmap_id}/duplicate",status_code=201)
def duplicate_roadmap(roadmap_id:UUID,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    source=db.get(CareerRoadmap,roadmap_id)
    if not source: raise HTTPException(404,"Roadmap not found")
    slug=f"{source.slug}-copy"
    suffix=2
    while db.scalar(select(CareerRoadmap).where(CareerRoadmap.slug==slug)):
        slug=f"{source.slug}-copy-{suffix}";suffix+=1
    row=CareerRoadmap(title=f"{source.title} (Copy)",title_mm=source.title_mm,slug=slug,career_category=source.career_category,description_en=source.description_en,description_mm=source.description_mm,prerequisites_en=source.prerequisites_en,prerequisites_mm=source.prerequisites_mm,outcomes_en=source.outcomes_en,outcomes_mm=source.outcomes_mm,estimated_hours=source.estimated_hours,cover_image=source.cover_image,goals_json=source.goals_json,skills_json=source.skills_json,completion_rules_json=source.completion_rules_json,created_by=user.id)
    db.add(row);db.flush()
    for source_stage in db.scalars(select(RoadmapStage).where(RoadmapStage.roadmap_id==source.id).order_by(RoadmapStage.position)).all():
        stage=RoadmapStage(roadmap_id=row.id,title=source_stage.title,title_mm=source_stage.title_mm,description_en=source_stage.description_en,description_mm=source_stage.description_mm,level=source_stage.level,objectives_json=source_stage.objectives_json,skills_json=source_stage.skills_json,completion_rules_json=source_stage.completion_rules_json,position=source_stage.position);db.add(stage);db.flush()
        for source_step in db.scalars(select(RoadmapStep).where(RoadmapStep.stage_id==source_stage.id).order_by(RoadmapStep.position)).all():
            step=RoadmapStep(stage_id=stage.id,title=source_step.title,title_mm=source_step.title_mm,instructions_en=source_step.instructions_en,instructions_mm=source_step.instructions_mm,position=source_step.position,required=source_step.required);db.add(step);db.flush()
            for resource in db.scalars(select(RoadmapStepResource).where(RoadmapStepResource.step_id==source_step.id)).all(): db.add(RoadmapStepResource(step_id=step.id,resource_type=resource.resource_type,resource_id=resource.resource_id))
    audit(db,user,"roadmap_duplicated","roadmap",row.id);db.commit();return {"id":row.id,"slug":row.slug,"status":row.status}

@router.post("/admin/roadmaps/{roadmap_id}/cover-image")
async def upload_roadmap_cover(roadmap_id:UUID,file:UploadFile=File(...),user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(CareerRoadmap,roadmap_id)
    if not row: raise HTTPException(404,"Roadmap not found")
    old=row.cover_image
    url,_,dimensions=await save_roadmap_image(file)
    row.cover_image=url;audit(db,user,"roadmap_cover_updated","roadmap",row.id);db.commit()
    if old and old!=url: remove_file_if_safe(old)
    return {"cover_image":url,"width":dimensions[0],"height":dimensions[1]}

@router.delete("/admin/roadmaps/{roadmap_id}/cover-image")
def remove_roadmap_cover(roadmap_id:UUID,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(CareerRoadmap,roadmap_id)
    if not row: raise HTTPException(404,"Roadmap not found")
    old=row.cover_image;row.cover_image=None;audit(db,user,"roadmap_cover_removed","roadmap",row.id);db.commit()
    if old: remove_file_if_safe(old)
    return {"cover_image":None}
@router.post("/admin/roadmaps/{roadmap_id}/stages",status_code=201)
def create_stage(roadmap_id:UUID,payload:StageIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    if not db.get(CareerRoadmap,roadmap_id):raise HTTPException(404,"Roadmap not found")
    values=payload.model_dump();values["objectives_json"]=json.dumps(values.pop("objectives"),ensure_ascii=False);values["skills_json"]=json.dumps(values.pop("skills"),ensure_ascii=False);values["completion_rules_json"]=json.dumps(values.pop("completion_rules"),ensure_ascii=False)
    row=RoadmapStage(roadmap_id=roadmap_id,**values);db.add(row);db.commit();return {"id":row.id}

@router.patch("/admin/stages/{stage_id}")
def update_stage(stage_id:UUID,payload:StagePatch,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(RoadmapStage,stage_id)
    if not row: raise HTTPException(404,"Stage not found")
    values=payload.model_dump(exclude_unset=True)
    for field in ("objectives","skills","completion_rules"):
        if field in values: setattr(row,f"{field}_json",json.dumps(values.pop(field),ensure_ascii=False))
    for field,value in values.items(): setattr(row,field,value)
    db.commit();return {"id":row.id}

@router.delete("/admin/stages/{stage_id}")
def delete_stage(stage_id:UUID,user:User=Depends(full_admin),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(RoadmapStage,stage_id)
    if not row: raise HTTPException(404,"Stage not found")
    db.delete(row);db.commit();return {"status":"deleted"}

@router.post("/admin/roadmaps/{roadmap_id}/stages/reorder")
def reorder_stages(roadmap_id:UUID,payload:OrderIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    rows=db.scalars(select(RoadmapStage).where(RoadmapStage.roadmap_id==roadmap_id)).all();allowed={x.id for x in rows}
    if set(payload.ids)!=allowed: raise HTTPException(422,"Order must contain exactly the roadmap stages")
    for position,stage_id in enumerate(payload.ids): db.get(RoadmapStage,stage_id).position=position
    db.commit();return {"status":"reordered"}

@router.post("/admin/stages/{stage_id}/steps",status_code=201)
def create_step(stage_id:UUID,payload:StepIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    if not db.get(RoadmapStage,stage_id):raise HTTPException(404,"Stage not found")
    row=RoadmapStep(stage_id=stage_id,**payload.model_dump());db.add(row);db.commit();return {"id":row.id}

@router.patch("/admin/steps/{step_id}")
def update_step(step_id:UUID,payload:StepPatch,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(RoadmapStep,step_id)
    if not row: raise HTTPException(404,"Step not found")
    for field,value in payload.model_dump(exclude_unset=True).items(): setattr(row,field,value)
    db.commit();return {"id":row.id}

@router.delete("/admin/steps/{step_id}")
def delete_step(step_id:UUID,user:User=Depends(full_admin),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(RoadmapStep,step_id)
    if not row: raise HTTPException(404,"Step not found")
    db.delete(row);db.commit();return {"status":"deleted"}
@router.post("/admin/steps/{step_id}/resources")
def add_resource(step_id:UUID,payload:ResourceIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    if not db.get(RoadmapStep,step_id):raise HTTPException(404,"Step not found")
    model={"course":Course,"lesson":Lesson,"project":ProjectTemplate,"challenge":Challenge}.get(payload.resource_type)
    if not model: raise HTTPException(422,"Resource type must be course, lesson, project, or challenge")
    if not db.get(model,payload.resource_id): raise HTTPException(404,"Resource not found")
    row=RoadmapStepResource(step_id=step_id,**payload.model_dump());db.add(row);db.commit();return {"id":row.id}

@router.delete("/admin/steps/{step_id}/resources/{resource_type}/{resource_id}")
def delete_resource(step_id:UUID,resource_type:str,resource_id:UUID,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.scalar(select(RoadmapStepResource).where(RoadmapStepResource.step_id==step_id,RoadmapStepResource.resource_type==resource_type,RoadmapStepResource.resource_id==resource_id))
    if not row: raise HTTPException(404,"Resource link not found")
    db.delete(row);db.commit();return {"status":"deleted"}
@router.post("/admin/steps/{step_id}/prerequisites")
def add_prerequisite(step_id:UUID,payload:PrereqIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    if step_id==payload.prerequisite_step_id:raise HTTPException(422,"A step cannot depend on itself")
    if not db.get(RoadmapStep,payload.prerequisite_step_id):raise HTTPException(404,"Prerequisite step not found")
    edges={x.step_id:x.prerequisite_step_id for x in db.scalars(select(RoadmapPrerequisite)).all()};edges[step_id]=payload.prerequisite_step_id;cursor=payload.prerequisite_step_id;seen=set()
    while cursor in edges:
        if cursor in seen or cursor==step_id:raise HTTPException(422,"Circular prerequisite dependency")
        seen.add(cursor);cursor=edges[cursor]
    row=RoadmapPrerequisite(step_id=step_id,prerequisite_step_id=payload.prerequisite_step_id);db.add(row);db.commit();return {"status":"created"}
@router.post("/admin/stages/{stage_id}/reorder")
def reorder_steps(stage_id:UUID,payload:OrderIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    rows=db.scalars(select(RoadmapStep).where(RoadmapStep.stage_id==stage_id)).all(); allowed={x.id for x in rows}
    if set(payload.ids)!=allowed:raise HTTPException(422,"Order must contain exactly the stage steps")
    for position,step_id in enumerate(payload.ids):db.get(RoadmapStep,step_id).position=position
    db.commit();return {"status":"reordered"}

@router.get("/admin/roadmap-content")
def roadmap_content(kind:str=Query(...,pattern="^(course|lesson|challenge|project|assessment)$"),search:str|None=None,limit:int=Query(50,ge=1,le=100),user:User=Depends(admin_user),db:Session=Depends(get_db)):
    model={"course":Course,"challenge":Challenge,"project":ProjectTemplate,"assessment":AssessmentDefinition}.get(kind)
    if kind=="lesson":
        query=select(Lesson,CourseModule,Course).join(CourseModule,Lesson.module_id==CourseModule.id).join(Course,CourseModule.course_id==Course.id)
        if search: query=query.where(Lesson.title.ilike(f"%{search}%"))
        rows=db.execute(query.order_by(Lesson.title).limit(limit)).all()
        return [{"id":lesson.id,"title":lesson.title,"slug":lesson.slug,"status":lesson.status,"published":lesson.published,"course_id":course.id,"course_title":course.title} for lesson,module,course in rows]
    query=select(model)
    if search: query=query.where(model.title.ilike(f"%{search}%"))
    rows=db.scalars(query.order_by(model.title).limit(limit)).all()
    return [{"id":row.id,"title":row.title,"slug":getattr(row,"slug",None),"status":getattr(row,"status",None),"published":getattr(row,"published",None)} for row in rows]

@router.get("/admin/roadmaps/{roadmap_id}/assessments")
def roadmap_assessments(roadmap_id:UUID,user:User=Depends(admin_user),db:Session=Depends(get_db)):
    if not db.get(CareerRoadmap,roadmap_id): raise HTTPException(404,"Roadmap not found")
    return roadmap_dict(db.get(CareerRoadmap,roadmap_id),db,False)["assessments"]

@router.post("/admin/roadmaps/{roadmap_id}/assessments",status_code=201)
def link_assessment(roadmap_id:UUID,payload:AssessmentLinkIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    if not db.get(CareerRoadmap,roadmap_id): raise HTTPException(404,"Roadmap not found")
    if not db.get(AssessmentDefinition,payload.assessment_id): raise HTTPException(404,"Assessment not found")
    if db.scalar(select(RoadmapAssessment).where(RoadmapAssessment.roadmap_id==roadmap_id,RoadmapAssessment.assessment_id==payload.assessment_id)): raise HTTPException(409,"Assessment is already linked")
    row=RoadmapAssessment(roadmap_id=roadmap_id,**payload.model_dump());db.add(row);db.commit();return {"id":row.id}

@router.delete("/admin/roadmaps/{roadmap_id}/assessments/{assessment_id}")
def unlink_assessment(roadmap_id:UUID,assessment_id:UUID,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.scalar(select(RoadmapAssessment).where(RoadmapAssessment.roadmap_id==roadmap_id,RoadmapAssessment.assessment_id==assessment_id))
    if not row: raise HTTPException(404,"Assessment link not found")
    db.delete(row);db.commit();return {"status":"deleted"}

@router.get("/admin/roadmaps/{roadmap_id}/progress")
def roadmap_progress_report(roadmap_id:UUID,user:User=Depends(admin_user),db:Session=Depends(get_db)):
    if not db.get(CareerRoadmap,roadmap_id): raise HTTPException(404,"Roadmap not found")
    enrollments=db.scalars(select(StudentRoadmap).where(StudentRoadmap.roadmap_id==roadmap_id)).all()
    return {"total_enrollments":len(enrollments),"active_enrollments":sum(x.status=="active" for x in enrollments),"completed_enrollments":sum(progress_view(db,x)["progress_percent"]>=100 for x in enrollments),"items":[{"id":x.id,"user_id":x.user_id,"status":x.status,"progress":progress_view(db,x)} for x in enrollments]}
@router.post("/admin/roadmaps/{roadmap_id}/submit-review")
def submit_roadmap_review(roadmap_id:UUID,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(CareerRoadmap,roadmap_id)
    if not row: raise HTTPException(404,"Roadmap not found")
    stages=db.scalars(select(RoadmapStage).where(RoadmapStage.roadmap_id==roadmap_id)).all(); errors=roadmap_quality(row,stages,db)
    if errors: raise HTTPException(422,{"message":"Roadmap is not ready for review","errors":errors})
    row.status="in_review"; audit(db,user,"roadmap_submitted_for_review","roadmap",row.id); db.commit(); return {"id":row.id,"published":row.published,"status":row.status}
@router.post("/admin/roadmaps/{roadmap_id}/approve")
def approve_roadmap(roadmap_id:UUID,user:User=Depends(full_admin),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(CareerRoadmap,roadmap_id)
    if not row: raise HTTPException(404,"Roadmap not found")
    stages=db.scalars(select(RoadmapStage).where(RoadmapStage.roadmap_id==roadmap_id)).all(); errors=roadmap_quality(row,stages,db)
    if errors: raise HTTPException(422,{"message":"Roadmap is not ready for approval","errors":errors})
    row.status="approved"; audit(db,user,"roadmap_approved","roadmap",row.id); db.commit(); return {"id":row.id,"published":row.published,"status":row.status}
@router.post("/admin/roadmaps/{roadmap_id}/publish")
def publish_roadmap(roadmap_id:UUID,payload:dict|None=None,user:User=Depends(full_admin),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(CareerRoadmap,roadmap_id); stages=db.scalars(select(RoadmapStage).where(RoadmapStage.roadmap_id==roadmap_id)).all() if row else []
    if not row:raise HTTPException(404,"Roadmap not found")
    action=(payload or {}).get("action","publish")
    if action=="publish":
        if row.status not in {"approved", "published"}: raise HTTPException(409,"Roadmap must be approved before publishing")
        errors=roadmap_quality(row,stages,db)
        if errors: raise HTTPException(422,{"message":"Roadmap is not ready to publish","errors":errors})
        row.published=True;row.status="published"
    elif action=="archive": row.published=False;row.status="archived"
    else: row.published=False;row.status="draft"
    audit(db,user,f"roadmap_{action}","roadmap",row.id);db.commit();return {"id":row.id,"published":row.published,"status":row.status}
