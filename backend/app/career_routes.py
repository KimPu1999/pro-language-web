import json
from datetime import datetime, timedelta, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .auth import current_user, require_csrf, require_role, verified_user
from .db import get_db
from .models import (CareerGoal, CareerProfile, CareerReadinessSnapshot, CareerRoadmap, Course,
    InterviewAttempt, InterviewEvaluation, InterviewQuestion, InterviewSession, JobApplication,
    MentorAvailability, MentorProfile, MentorshipFeedback, MentorshipRequest, MentorshipSession,
    PortfolioReviewFeedback, PortfolioReviewRequest, ResumeDocument, ResumeVersion, StudentPortfolio,
    StudentProject, User)

router=APIRouter(prefix="/api/v1/career",tags=["career development"])
ADMIN={"admin","platform_admin","super_admin"}
class ProfileIn(BaseModel): headline:str=Field(default="",max_length=180); summary:str=Field(default="",max_length=10000); visibility:str="private"
class MentorApplyIn(BaseModel): bio:str=Field(min_length=1,max_length=10000); expertise:list[str]=Field(default_factory=list,max_length=20); languages:list[str]=Field(default_factory=list,max_length=20)
class SlotIn(BaseModel): starts_at:datetime; ends_at:datetime; timezone:str="UTC"
class RequestIn(BaseModel): mentor_id:UUID; availability_id:UUID; message:str=Field(default="",max_length=2000)
class ResumeIn(BaseModel): title:str=Field(default="My resume",max_length=180); content:dict
class ApplicationIn(BaseModel): company_name:str=Field(min_length=1,max_length=180); job_title:str=Field(min_length=1,max_length=180); status:str="planned"; notes:str=Field(default="",max_length=5000); application_date:datetime|None=None; interview_at:datetime|None=None; follow_up_at:datetime|None=None
class InterviewStartIn(BaseModel): session_type:str=Field(pattern="^(technical|coding|system_design|behavioral)$"); duration_minutes:int=Field(default=45,ge=10,le=180)
class AttemptIn(BaseModel): answer_text:str=Field(default="",max_length=30000); source_code:str=Field(default="",max_length=100000)
class QuestionIn(BaseModel): title:str=Field(min_length=1,max_length=180); prompt:str=Field(min_length=1,max_length=20000); topic:str=Field(min_length=1,max_length=80); difficulty:str; language:str|None=None; expected_concepts:str=""; published:bool=False
def now(): return datetime.now(timezone.utc)
def mentor_out(row,db):
    user=db.get(User,row.user_id); return {"id":row.id,"user_id":row.user_id,"name":user.display_name if user else "Approved mentor","bio":row.bio,"expertise":json.loads(row.expertise_json),"languages":json.loads(row.languages_json),"approval_status":row.approval_status}

@router.get("/dashboard")
def dashboard(user:User=Depends(current_user),db:Session=Depends(get_db)):
    profile=db.scalar(select(CareerProfile).where(CareerProfile.user_id==user.id)); goal=db.scalar(select(CareerGoal).where(CareerGoal.user_id==user.id,CareerGoal.active.is_(True))); portfolio=db.scalar(select(StudentPortfolio).where(StudentPortfolio.user_id==user.id)); resume=db.scalar(select(ResumeDocument).where(ResumeDocument.user_id==user.id)); sessions=db.scalar(select(func.count(MentorshipSession.id)).where(MentorshipSession.student_id==user.id,MentorshipSession.status=="scheduled")) or 0; interviews=db.scalar(select(func.count(InterviewSession.id)).where(InterviewSession.user_id==user.id)) or 0
    readiness="not_yet_assessed" if not profile and not goal else "developing"
    return {"profile":profile,"goal":{"roadmap_id":goal.roadmap_id,"target_level":goal.target_level} if goal else None,"readiness":{"status":readiness,"explanation":"Career readiness is based on observed skills, approved projects, resume completeness, and interview practice. It is not a hiring prediction."},"progress":{"portfolio_ready":bool(portfolio and portfolio.visibility=="public"),"resume_started":bool(resume),"upcoming_mentorship":sessions,"interview_sessions":interviews}}

@router.get("/paths")
def paths(search:str|None=None,db:Session=Depends(get_db)):
    q=select(CareerRoadmap).where(CareerRoadmap.published.is_(True));
    if search:q=q.where(CareerRoadmap.title.ilike(f"%{search}%"))
    return [{"id":x.id,"title":x.title,"slug":x.slug,"career_category":x.career_category,"description_en":x.description_en,"description_mm":x.description_mm,"estimated_hours":x.estimated_hours} for x in db.scalars(q.order_by(CareerRoadmap.title)).all()]
@router.get("/paths/{slug}")
def path_detail(slug:str,db:Session=Depends(get_db)):
    row=db.scalar(select(CareerRoadmap).where(CareerRoadmap.slug==slug,CareerRoadmap.published.is_(True)))
    if not row:raise HTTPException(404,"Career path not found")
    return {"id":row.id,"title":row.title,"slug":row.slug,"career_category":row.career_category,"description_en":row.description_en,"description_mm":row.description_mm,"prerequisites_en":row.prerequisites_en,"outcomes_en":row.outcomes_en,"estimated_hours":row.estimated_hours}

@router.get("/profile")
def get_profile(user:User=Depends(current_user),db:Session=Depends(get_db)):return db.scalar(select(CareerProfile).where(CareerProfile.user_id==user.id)) or {"visibility":"private","headline":"","summary":""}
@router.put("/profile")
def save_profile(payload:ProfileIn,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.scalar(select(CareerProfile).where(CareerProfile.user_id==user.id)) or CareerProfile(user_id=user.id); row.headline=payload.headline;row.summary=payload.summary;row.visibility=payload.visibility if payload.visibility in {"private","public"} else "private";db.add(row);db.commit();return row

@router.get("/mentors")
def mentors(search:str|None=None,db:Session=Depends(get_db)):
    rows=db.scalars(select(MentorProfile).where(MentorProfile.approval_status=="approved").order_by(MentorProfile.created_at.desc())).all();out=[mentor_out(x,db) for x in rows]
    return [x for x in out if not search or search.lower() in (x["name"]+" "+x["bio"]+" "+" ".join(x["expertise"])).lower()]
@router.get("/mentors/{mentor_id}")
def mentor(mentor_id:UUID,db:Session=Depends(get_db)):
    row=db.scalar(select(MentorProfile).where(MentorProfile.id==mentor_id,MentorProfile.approval_status=="approved"));
    if not row:raise HTTPException(404,"Approved mentor not found")
    return {**mentor_out(row,db),"availability":[{"id":x.id,"starts_at":x.starts_at,"ends_at":x.ends_at,"timezone":x.timezone} for x in db.scalars(select(MentorAvailability).where(MentorAvailability.mentor_id==row.id,MentorAvailability.status=="open",MentorAvailability.starts_at>now()).order_by(MentorAvailability.starts_at)).all()]}
@router.post("/mentor-application",status_code=201)
def mentor_apply(payload:MentorApplyIn,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.scalar(select(MentorProfile).where(MentorProfile.user_id==user.id)) or MentorProfile(user_id=user.id);row.bio=payload.bio;row.expertise_json=json.dumps(payload.expertise);row.languages_json=json.dumps(payload.languages);row.approval_status="pending";db.add(row);db.commit();return {"id":row.id,"status":row.approval_status}
@router.post("/mentors/{mentor_id}/availability",status_code=201)
def add_slot(mentor_id:UUID,payload:SlotIn,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    mentor_row=db.get(MentorProfile,mentor_id)
    if not mentor_row or (user.role not in ADMIN and mentor_row.user_id!=user.id):raise HTTPException(403,"Mentor ownership required")
    if mentor_row.approval_status!="approved" or payload.starts_at.tzinfo is None or payload.ends_at<=payload.starts_at:raise HTTPException(422,"Approved mentor and valid timezone-aware slot required")
    row=MentorAvailability(mentor_id=mentor_id,starts_at=payload.starts_at.astimezone(timezone.utc),ends_at=payload.ends_at.astimezone(timezone.utc),timezone=payload.timezone);db.add(row);db.commit();return {"id":row.id,"starts_at":row.starts_at,"ends_at":row.ends_at}
@router.post("/requests",status_code=201)
def request_session(payload:RequestIn,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    slot=db.scalar(select(MentorAvailability).where(MentorAvailability.id==payload.availability_id,MentorAvailability.mentor_id==payload.mentor_id,MentorAvailability.status=="open",MentorAvailability.starts_at>now())); mentor_row=db.scalar(select(MentorProfile).where(MentorProfile.id==payload.mentor_id,MentorProfile.approval_status=="approved"))
    if not slot or not mentor_row:raise HTTPException(404,"Available mentor slot not found")
    row=MentorshipRequest(student_id=user.id,mentor_id=payload.mentor_id,availability_id=slot.id,message=payload.message);db.add(row);slot.status="requested"
    try:db.commit()
    except IntegrityError:db.rollback();raise HTTPException(409,"This slot is no longer available")
    return {"id":row.id,"status":row.status}
@router.get("/sessions")
def sessions(user:User=Depends(current_user),db:Session=Depends(get_db)):return db.scalars(select(MentorshipSession).where(MentorshipSession.student_id==user.id).order_by(MentorshipSession.created_at.desc())).all()

@router.get("/resume")
def resume(user:User=Depends(current_user),db:Session=Depends(get_db)):
    row=db.scalar(select(ResumeDocument).where(ResumeDocument.user_id==user.id));
    if not row:return {"document":None,"versions":[]}
    return {"document":row,"versions":db.scalars(select(ResumeVersion).where(ResumeVersion.resume_id==row.id).order_by(ResumeVersion.version_number.desc())).all()}
@router.put("/resume")
def save_resume(payload:ResumeIn,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.scalar(select(ResumeDocument).where(ResumeDocument.user_id==user.id)) or ResumeDocument(user_id=user.id,title=payload.title);row.title=payload.title;db.add(row);db.flush();version=(db.scalar(select(func.max(ResumeVersion.version_number)).where(ResumeVersion.resume_id==row.id)) or 0)+1;v=ResumeVersion(resume_id=row.id,content_json=json.dumps(payload.content),version_number=version);db.add(v);db.flush();row.active_version_id=v.id;db.commit();return {"id":row.id,"version_id":v.id,"version_number":version}
@router.get("/resume/export")
def export_resume(user:User=Depends(current_user)):raise HTTPException(501,"PDF export is not configured in this environment")

@router.post("/portfolio-reviews",status_code=201)
def portfolio_review(payload:dict,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    project_ids=payload.get("project_ids",[]); owned=db.scalars(select(StudentProject.id).where(StudentProject.user_id==user.id,StudentProject.status=="approved",StudentProject.id.in_(project_ids))).all() if project_ids else []
    if not project_ids or set(map(str,owned))!=set(map(str,project_ids)):raise HTTPException(422,"Only your approved projects can be reviewed")
    row=PortfolioReviewRequest(student_id=user.id,project_ids_json=json.dumps(project_ids),message=str(payload.get("message","")[:2000]));db.add(row);db.commit();return {"id":row.id,"status":row.status}

@router.get("/interviews/questions")
def questions(topic:str|None=None,difficulty:str|None=None,db:Session=Depends(get_db)):
    q=select(InterviewQuestion).where(InterviewQuestion.published.is_(True));
    if topic:q=q.where(InterviewQuestion.topic==topic)
    if difficulty:q=q.where(InterviewQuestion.difficulty==difficulty)
    return db.scalars(q.order_by(InterviewQuestion.created_at.desc())).all()
@router.post("/interviews",status_code=201)
def start_interview(payload:InterviewStartIn,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=InterviewSession(user_id=user.id,session_type=payload.session_type,ends_at=now()+timedelta(minutes=payload.duration_minutes));db.add(row);db.commit();return {"id":row.id,"ends_at":row.ends_at,"status":row.status}
@router.post("/interviews/{session_id}/questions/{question_id}",status_code=201)
def submit_attempt(session_id:UUID,question_id:UUID,payload:AttemptIn,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    session=db.scalar(select(InterviewSession).where(InterviewSession.id==session_id,InterviewSession.user_id==user.id)); question=db.scalar(select(InterviewQuestion).where(InterviewQuestion.id==question_id,InterviewQuestion.published.is_(True)))
    if not session or not question:raise HTTPException(404,"Interview resource not found")
    if session.ends_at<now() or session.status!="active":raise HTTPException(409,"Interview session has ended")
    row=InterviewAttempt(session_id=session.id,question_id=question.id,answer_text=payload.answer_text,source_code=payload.source_code);db.add(row);db.flush();db.add(InterviewEvaluation(attempt_id=row.id,explanation="Evaluation is pending; automated tests and rubric review are reported separately."));db.commit();return {"id":row.id,"status":row.status,"evaluation":"pending"}

@router.get("/applications")
def applications(user:User=Depends(current_user),db:Session=Depends(get_db)):return db.scalars(select(JobApplication).where(JobApplication.user_id==user.id).order_by(JobApplication.application_date.desc())).all()
@router.post("/applications",status_code=201)
def add_application(payload:ApplicationIn,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=JobApplication(user_id=user.id,company_name=payload.company_name,job_title=payload.job_title,status=payload.status,notes=payload.notes,application_date=payload.application_date or now(),interview_at=payload.interview_at,follow_up_at=payload.follow_up_at);db.add(row);db.commit();return row

@router.get("/admin/mentors")
def admin_mentors(user:User=Depends(require_role("admin","platform_admin","super_admin")),db:Session=Depends(get_db)):return [mentor_out(x,db) for x in db.scalars(select(MentorProfile).order_by(MentorProfile.created_at.desc())).all()]
@router.patch("/admin/mentors/{mentor_id}")
def review_mentor(mentor_id:UUID,status_value:str=Query(...,pattern="^(approved|rejected|suspended|pending)$"),user:User=Depends(require_role("admin","platform_admin","super_admin")),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(MentorProfile,mentor_id)
    if not row:raise HTTPException(404,"Mentor application not found")
    row.approval_status=status_value;row.reviewed_by=user.id;row.reviewed_at=now();db.commit();return {"id":row.id,"status":row.approval_status}
@router.post("/admin/interview-questions",status_code=201)
def create_question(payload:QuestionIn,user:User=Depends(require_role("admin","platform_admin","super_admin","instructor")),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=InterviewQuestion(**payload.model_dump());db.add(row);db.commit();return {"id":row.id,"published":row.published}
