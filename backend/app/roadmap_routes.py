import json
from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .auth import current_user, require_csrf, verified_user
from .db import get_db
from .models import (CareerRoadmap, ChallengeSubmission, Course, CourseModule, Lesson, LessonProgress, RoadmapPrerequisite, RoadmapStage, RoadmapStep, RoadmapStepResource, StudentLearningGoal, StudentProject, StudentRoadmap, StudentRoadmapBookmark, User)
from .admin_routes import admin_user, full_admin, audit

router=APIRouter(prefix="/api/v1",tags=["roadmaps"])
class GoalIn(BaseModel): career_goal:str=Field(min_length=1,max_length=100); current_level:str; interests:list[str]=[]; weekly_hours:int=Field(ge=1,le=80); pace:str="steady"; timezone:str="UTC"
class RoadmapIn(BaseModel): title:str=Field(min_length=1,max_length=180); slug:str=Field(pattern=r"^[a-z0-9-]+$"); career_category:str; description_en:str=Field(min_length=1); description_mm:str|None=None; prerequisites_en:str=""; outcomes_en:str=""; estimated_hours:int=Field(default=0,ge=0)
class StageIn(BaseModel): title:str; description_en:str=""; description_mm:str|None=None; level:str; position:int=Field(ge=0)
class StepIn(BaseModel): title:str; instructions_en:str=""; instructions_mm:str|None=None; position:int=Field(ge=0); required:bool=True
class OrderIn(BaseModel): ids:list[UUID]
class PrereqIn(BaseModel): prerequisite_step_id:UUID
class ResourceIn(BaseModel): resource_type:str; resource_id:UUID
def step_dict(step,db):
    return {"id":step.id,"title":step.title,"instructions_en":step.instructions_en,"instructions_mm":step.instructions_mm,"position":step.position,"required":step.required,"resources":[{"resource_type":r.resource_type,"resource_id":r.resource_id} for r in db.scalars(select(RoadmapStepResource).where(RoadmapStepResource.step_id==step.id)).all()]}
def roadmap_dict(row,db,include_steps=True):
    stages=db.scalars(select(RoadmapStage).where(RoadmapStage.roadmap_id==row.id).order_by(RoadmapStage.position)).all(); out={"id":row.id,"title":row.title,"slug":row.slug,"career_category":row.career_category,"description_en":row.description_en,"description_mm":row.description_mm,"prerequisites_en":row.prerequisites_en,"outcomes_en":row.outcomes_en,"estimated_hours":row.estimated_hours,"status":row.status,"published":row.published,"stages":[]}
    if include_steps: out["stages"]=[{"id":s.id,"title":s.title,"description_en":s.description_en,"description_mm":s.description_mm,"level":s.level,"position":s.position,"steps":[step_dict(x,db) for x in db.scalars(select(RoadmapStep).where(RoadmapStep.stage_id==s.id).order_by(RoadmapStep.position)).all()]} for s in stages]
    return out
def evidence_complete(db,user_id,step_id):
    resources=db.scalars(select(RoadmapStepResource).where(RoadmapStepResource.step_id==step_id)).all()
    for r in resources:
        if r.resource_type=="challenge" and db.scalar(select(ChallengeSubmission.id).where(ChallengeSubmission.user_id==user_id,ChallengeSubmission.challenge_id==r.resource_id,ChallengeSubmission.status=="accepted")): return True
        if r.resource_type=="project" and db.scalar(select(StudentProject.id).where(StudentProject.user_id==user_id,StudentProject.project_id==r.resource_id,StudentProject.status=="approved")): return True
        if r.resource_type=="course":
            total=db.scalar(select(func.count(Lesson.id)).join(CourseModule).where(CourseModule.course_id==r.resource_id,Lesson.published.is_(True))) or 0; done=db.scalar(select(func.count(LessonProgress.id)).join(Lesson,Lesson.id==LessonProgress.lesson_id).join(CourseModule,CourseModule.id==Lesson.module_id).where(LessonProgress.user_id==user_id,CourseModule.course_id==r.resource_id,Lesson.published.is_(True),LessonProgress.completed.is_(True))) or 0
            if total and total==done: return True
    return False
def progress_view(db,enrollment):
    steps=db.scalars(select(RoadmapStep).join(RoadmapStage).where(RoadmapStage.roadmap_id==enrollment.roadmap_id)).all(); completed=sum(1 for s in steps if evidence_complete(db,enrollment.user_id,s.id)); return {"completed_steps":completed,"total_steps":len(steps),"progress_percent":round(completed/len(steps)*100,1) if steps else 0}
@router.get("/learning-paths")
@router.get("/roadmaps")
def list_roadmaps(search:str|None=None,career_category:str|None=None,difficulty:str|None=None,page:int=Query(1,ge=1),page_size:int=Query(12,ge=1,le=50),db:Session=Depends(get_db)):
    q=select(CareerRoadmap).where(CareerRoadmap.published.is_(True)); count=select(func.count()).select_from(CareerRoadmap).where(CareerRoadmap.published.is_(True))
    if search:q=q.where(CareerRoadmap.title.ilike(f"%{search}%"));count=count.where(CareerRoadmap.title.ilike(f"%{search}%"))
    if career_category:q=q.where(CareerRoadmap.career_category==career_category);count=count.where(CareerRoadmap.career_category==career_category)
    if difficulty:
        matching=select(RoadmapStage.roadmap_id).where(RoadmapStage.level==difficulty)
        q=q.where(CareerRoadmap.id.in_(matching)); count=count.where(CareerRoadmap.id.in_(matching))
    total=db.scalar(count) or 0; rows=db.scalars(q.order_by(CareerRoadmap.title).offset((page-1)*page_size).limit(page_size)).all(); return {"items":[roadmap_dict(x,db,False) for x in rows],"page":page,"page_size":page_size,"total":total,"pages":(total+page_size-1)//page_size if total else 0}
@router.get("/learning-paths/categories")
def learning_path_categories(db:Session=Depends(get_db)):
    return db.scalars(select(CareerRoadmap.career_category).where(CareerRoadmap.published.is_(True)).distinct().order_by(CareerRoadmap.career_category)).all()
@router.get("/learning-paths/{slug}")
@router.get("/roadmaps/{slug}")
def get_roadmap(slug:str,db:Session=Depends(get_db)):
    row=db.scalar(select(CareerRoadmap).where(CareerRoadmap.slug==slug,CareerRoadmap.published.is_(True)))
    if not row: raise HTTPException(404,"Roadmap not found")
    return roadmap_dict(row,db)
@router.get("/learning-paths/{slug}/stages")
def roadmap_stages(slug:str,db:Session=Depends(get_db)):
    row=db.scalar(select(CareerRoadmap).where(CareerRoadmap.slug==slug,CareerRoadmap.published.is_(True)))
    if not row: raise HTTPException(404,"Roadmap not found")
    return roadmap_dict(row,db)["stages"]
@router.get("/learning-paths/{slug}/courses")
def roadmap_courses(slug:str,db:Session=Depends(get_db)):
    row=db.scalar(select(CareerRoadmap).where(CareerRoadmap.slug==slug,CareerRoadmap.published.is_(True)))
    if not row: raise HTTPException(404,"Roadmap not found")
    resource_ids=db.scalars(select(RoadmapStepResource.resource_id).join(RoadmapStep,RoadmapStepResource.step_id==RoadmapStep.id).join(RoadmapStage,RoadmapStep.stage_id==RoadmapStage.id).where(RoadmapStage.roadmap_id==row.id,RoadmapStepResource.resource_type=="course")).all()
    courses=db.scalars(select(Course).where(Course.id.in_(resource_ids),Course.published.is_(True)).order_by(Course.title)).all() if resource_ids else []
    return [{"id":course.id,"title":course.title,"slug":course.slug,"level":course.level,"duration_minutes":course.duration_minutes} for course in courses]
@router.post("/me/roadmaps/{roadmap_slug}",status_code=201)
def start_roadmap(roadmap_slug:str,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    roadmap=db.scalar(select(CareerRoadmap).where(CareerRoadmap.slug==roadmap_slug,CareerRoadmap.published.is_(True)))
    if not roadmap: raise HTTPException(404,"Published roadmap not found")
    existing=db.scalar(select(StudentRoadmap).where(StudentRoadmap.user_id==user.id,StudentRoadmap.roadmap_id==roadmap.id))
    if existing and existing.status=="active": raise HTTPException(409,"Roadmap already active")
    if existing: existing.status="active"; existing.paused_at=None; db.commit(); return {"id":existing.id,"status":existing.status,"progress":progress_view(db,existing)}
    row=StudentRoadmap(user_id=user.id,roadmap_id=roadmap.id);db.add(row);db.commit();return {"id":row.id,"status":row.status,"progress":progress_view(db,row)}
@router.post("/learning-paths/{roadmap_id}/enroll",status_code=201)
def enroll_learning_path(roadmap_id:UUID,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    roadmap=db.scalar(select(CareerRoadmap).where(CareerRoadmap.id==roadmap_id,CareerRoadmap.published.is_(True)))
    if not roadmap: raise HTTPException(404,"Published learning path not found")
    existing=db.scalar(select(StudentRoadmap).where(StudentRoadmap.user_id==user.id,StudentRoadmap.roadmap_id==roadmap.id))
    if existing and existing.status=="active": raise HTTPException(409,"Learning path already active")
    if existing: existing.status="active"; existing.paused_at=None; db.commit(); return {"id":existing.id,"status":existing.status,"progress":progress_view(db,existing)}
    row=StudentRoadmap(user_id=user.id,roadmap_id=roadmap.id); db.add(row); db.commit(); return {"id":row.id,"status":row.status,"progress":progress_view(db,row)}
@router.get("/me/roadmaps")
def my_roadmaps(user:User=Depends(current_user),db:Session=Depends(get_db)):
    rows=db.scalars(select(StudentRoadmap).where(StudentRoadmap.user_id==user.id).order_by(StudentRoadmap.created_at.desc())).all(); bookmarks={x.roadmap_id for x in db.scalars(select(StudentRoadmapBookmark).where(StudentRoadmapBookmark.user_id==user.id)).all()}; return [{"id":x.id,"roadmap_id":x.roadmap_id,"status":x.status,"bookmarked":x.roadmap_id in bookmarks,"progress":progress_view(db,x)} for x in rows]
@router.get("/me/learning-paths")
def my_learning_paths(user:User=Depends(current_user),db:Session=Depends(get_db)):
    return my_roadmaps(user,db)
@router.get("/me/learning-paths/{roadmap_id}/progress")
def learning_path_progress(roadmap_id:UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):
    return roadmap_progress(roadmap_id,user,db)
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
    if db.scalar(select(CareerRoadmap).where(CareerRoadmap.slug==payload.slug)):raise HTTPException(409,"Slug already exists")
    row=CareerRoadmap(**payload.model_dump(),created_by=user.id);db.add(row);audit(db,user,"roadmap_created","roadmap",row.id);db.commit();return {"id":row.id,"slug":row.slug,"status":row.status}
@router.post("/admin/roadmaps/{roadmap_id}/stages",status_code=201)
def create_stage(roadmap_id:UUID,payload:StageIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    if not db.get(CareerRoadmap,roadmap_id):raise HTTPException(404,"Roadmap not found")
    row=RoadmapStage(roadmap_id=roadmap_id,**payload.model_dump());db.add(row);db.commit();return {"id":row.id}
@router.post("/admin/stages/{stage_id}/steps",status_code=201)
def create_step(stage_id:UUID,payload:StepIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    if not db.get(RoadmapStage,stage_id):raise HTTPException(404,"Stage not found")
    row=RoadmapStep(stage_id=stage_id,**payload.model_dump());db.add(row);db.commit();return {"id":row.id}
@router.post("/admin/steps/{step_id}/resources")
def add_resource(step_id:UUID,payload:ResourceIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    if not db.get(RoadmapStep,step_id):raise HTTPException(404,"Step not found")
    row=RoadmapStepResource(step_id=step_id,**payload.model_dump());db.add(row);db.commit();return {"id":row.id}
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
@router.post("/admin/roadmaps/{roadmap_id}/publish")
def publish_roadmap(roadmap_id:UUID,user:User=Depends(full_admin),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(CareerRoadmap,roadmap_id); stages=db.scalars(select(RoadmapStage).where(RoadmapStage.roadmap_id==roadmap_id)).all() if row else []
    if not row:raise HTTPException(404,"Roadmap not found")
    if not row.description_en.strip() or not stages:raise HTTPException(422,"Roadmap needs English content and at least one stage")
    row.published=True;row.status="published";audit(db,user,"roadmap_published","roadmap",row.id);db.commit();return {"id":row.id,"published":row.published,"status":row.status}
