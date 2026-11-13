import json
from datetime import timedelta
from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .auth import current_user, require_csrf, verified_user
from .db import get_db
from .models import (AchievementDefinition, Challenge, ChallengeCategory, ChallengeHint, ChallengeLanguageConfig, ChallengeSubmission, ChallengeTestCase, ChallengeTopic, ChallengeTopicLink, CodeExecutionJob, CodeExecutionResult, DailyChallenge, StudentAchievement, StudentChallengeProgress, StudentSkillStatistic, User)
from .runner_queue import queue
from .runner_registry import get_runtime
from .admin_routes import admin_user, full_admin, audit

router = APIRouter(prefix="/api/v1/challenges", tags=["challenges"])
class SubmissionIn(BaseModel):
    language: str
    source_code: str = Field(min_length=1, max_length=100000)
class ChallengeIn(BaseModel):
    title: str = Field(min_length=1, max_length=180); slug: str = Field(pattern=r"^[a-z0-9-]+$"); description_en: str = Field(min_length=1); description_mm: str|None = None; difficulty: str; category_id: UUID|None = None
class TestIn(BaseModel):
    input_data: str = ""; expected_output: str = ""; is_hidden: bool = True; points: int = Field(default=1, ge=1, le=100); position: int = Field(default=0, ge=0)
class LanguageIn(BaseModel):
    language: str; starter_code: str = ""; time_limit_ms: int = Field(default=2000, ge=100, le=30000); memory_limit_mb: int = Field(default=128, ge=16, le=1024)
def json_list(value: str):
    try:
        parsed=json.loads(value or "[]")
        return parsed if isinstance(parsed, list) else []
    except (TypeError, ValueError):
        return []
def public_challenge(row, db, user_id=None):
    configs=db.scalars(select(ChallengeLanguageConfig).where(ChallengeLanguageConfig.challenge_id==row.id).order_by(ChallengeLanguageConfig.language)).all()
    topics=db.scalars(select(ChallengeTopic).join(ChallengeTopicLink, ChallengeTopic.id==ChallengeTopicLink.topic_id).where(ChallengeTopicLink.challenge_id==row.id)).all()
    solved=False
    if user_id: solved=db.scalar(select(StudentChallengeProgress.solved).where(StudentChallengeProgress.user_id==user_id,StudentChallengeProgress.challenge_id==row.id)) or False
    category = db.get(ChallengeCategory, row.category_id) if row.category_id else None
    return {"id":row.id,"title":row.title,"slug":row.slug,"description_en":row.description_en,"description_mm":row.description_mm,"examples":json_list(row.examples_json),"constraints":json_list(row.constraints_json),"difficulty":row.difficulty,"status":row.status,"category_id":row.category_id,"category":({"name":category.name,"slug":category.slug} if category else None),"languages":[{"language":x.language,"starter_code":x.starter_code,"time_limit_ms":x.time_limit_ms,"memory_limit_mb":x.memory_limit_mb} for x in configs],"topics":[{"name":x.name,"slug":x.slug} for x in topics],"solved":solved}
@router.get("/categories")
def list_challenge_categories(db: Session=Depends(get_db)):
    return db.scalars(select(ChallengeCategory).where(ChallengeCategory.status=="active").order_by(ChallengeCategory.name)).all()
@router.get("/topics")
def list_challenge_topics(db: Session=Depends(get_db)):
    return db.scalars(select(ChallengeTopic).order_by(ChallengeTopic.name)).all()
@router.get("/progress/me")
@router.get("/me/challenge-progress")
def progress(user: User=Depends(current_user), db: Session=Depends(get_db)):
    attempts=db.scalar(select(func.count(ChallengeSubmission.id)).where(ChallengeSubmission.user_id==user.id)) or 0
    solved=db.scalar(select(func.count(StudentChallengeProgress.id)).where(StudentChallengeProgress.user_id==user.id,StudentChallengeProgress.solved.is_(True))) or 0
    return {"attempts":attempts,"solved":solved,"acceptance_rate":round(solved/attempts*100,2) if attempts else 0}
@router.get("")
def list_challenges(search: str|None=None, difficulty: str|None=None, language: str|None=None, category: str|None=None, topic: str|None=None, page: int=Query(1,ge=1), page_size: int=Query(20,ge=1,le=50), db: Session=Depends(get_db)):
    q=select(Challenge).where(Challenge.published.is_(True)); count=select(func.count(func.distinct(Challenge.id))).select_from(Challenge).where(Challenge.published.is_(True))
    if search:
        term=f"%{search}%"; condition=Challenge.title.ilike(term) | Challenge.description_en.ilike(term); q=q.where(condition); count=count.where(condition)
    if difficulty: q=q.where(Challenge.difficulty==difficulty); count=count.where(Challenge.difficulty==difficulty)
    if language: q=q.join(ChallengeLanguageConfig).where(ChallengeLanguageConfig.language==language); count=count.join(ChallengeLanguageConfig).where(ChallengeLanguageConfig.language==language)
    if category: q=q.join(ChallengeCategory).where(ChallengeCategory.slug==category); count=count.join(ChallengeCategory).where(ChallengeCategory.slug==category)
    if topic: q=q.join(ChallengeTopicLink).join(ChallengeTopic).where(ChallengeTopic.slug==topic); count=count.join(ChallengeTopicLink).join(ChallengeTopic).where(ChallengeTopic.slug==topic)
    total=db.scalar(count) or 0; rows=db.scalars(q.order_by(Challenge.title).offset((page-1)*page_size).limit(page_size)).unique().all()
    return {"items":[public_challenge(x,db) for x in rows],"page":page,"page_size":page_size,"total":total,"pages":(total+page_size-1)//page_size if total else 0}
@router.get("/{challenge_id}/hints")
def challenge_hints(challenge_id: UUID, db: Session=Depends(get_db)):
    if not db.scalar(select(Challenge.id).where(Challenge.id==challenge_id, Challenge.published.is_(True))): raise HTTPException(404,"Challenge not found")
    return db.scalars(select(ChallengeHint).where(ChallengeHint.challenge_id==challenge_id).order_by(ChallengeHint.position)).all()
@router.get("/submissions/history")
def history(challenge_id: UUID|None=None,user: User=Depends(current_user),db: Session=Depends(get_db)):
    q=select(ChallengeSubmission).where(ChallengeSubmission.user_id==user.id).order_by(ChallengeSubmission.created_at.desc()).limit(50)
    if challenge_id: q=q.where(ChallengeSubmission.challenge_id==challenge_id)
    return db.scalars(q).all()
@router.get("/daily/today")
def daily(user: User|None=Depends(current_user),db: Session=Depends(get_db)):
    today=datetime.now(timezone.utc).date(); row=db.scalar(select(DailyChallenge).where(func.date(DailyChallenge.challenge_date)==today))
    if not row: return {"challenge":None,"completed":False}
    challenge=db.get(Challenge,row.challenge_id); solved=db.scalar(select(StudentChallengeProgress.solved).where(StudentChallengeProgress.user_id==user.id,StudentChallengeProgress.challenge_id==row.challenge_id)) if user else False
    return {"date":today.isoformat(),"challenge":public_challenge(challenge,db,user.id if user else None),"completed":bool(solved)}
@router.get("/skills/me")
def skills(user: User=Depends(current_user),db: Session=Depends(get_db)):
    attempts=db.scalar(select(func.count(ChallengeSubmission.id)).where(ChallengeSubmission.user_id==user.id)) or 0; solved=db.scalar(select(func.count(StudentChallengeProgress.id)).where(StudentChallengeProgress.user_id==user.id,StudentChallengeProgress.solved.is_(True))) or 0
    accepted=db.scalar(select(func.count(ChallengeSubmission.id)).where(ChallengeSubmission.user_id==user.id,ChallengeSubmission.status=="accepted")) or 0
    return {"attempts":attempts,"solved":solved,"acceptance_rate":round(accepted/attempts*100,2) if attempts else 0,"difficulty_distribution":[],"topic_progress":[],"recent_submissions":db.scalars(select(ChallengeSubmission).where(ChallengeSubmission.user_id==user.id).order_by(ChallengeSubmission.created_at.desc()).limit(10)).all()}
@router.get("/achievements/me")
def achievements(user: User=Depends(current_user),db: Session=Depends(get_db)):
    rows=db.execute(select(AchievementDefinition,StudentAchievement.awarded_at).join(StudentAchievement,StudentAchievement.achievement_id==AchievementDefinition.id).where(StudentAchievement.user_id==user.id)).all(); return [{"slug":d.slug,"title":d.title,"description":d.description,"awarded_at":awarded} for d,awarded in rows]
@router.get("/admin")
def admin_list(search: str|None=None, status: str|None=None, user: User=Depends(admin_user), db: Session=Depends(get_db)):
    query=select(Challenge).order_by(Challenge.updated_at.desc())
    if search: query=query.where(Challenge.title.ilike(f"%{search}%"))
    if status: query=query.where(Challenge.status==status)
    return [public_challenge(row, db) for row in db.scalars(query).all()]
@router.get("/{slug}")
def get_challenge(slug: str, db: Session=Depends(get_db)):
    row=db.scalar(select(Challenge).where(Challenge.slug==slug,Challenge.published.is_(True)))
    if not row: raise HTTPException(404,"Challenge not found")
    hints=db.scalars(select(ChallengeHint).where(ChallengeHint.challenge_id==row.id).order_by(ChallengeHint.position)).all()
    result=public_challenge(row,db); result["hints"]=[{"body_en":h.body_en,"body_mm":h.body_mm} for h in hints]; result["examples"]=result["examples"]
    result["public_tests"]= [{"input":t.input_data,"expected_output":t.expected_output,"points":t.points} for t in db.scalars(select(ChallengeTestCase).where(ChallengeTestCase.challenge_id==row.id,ChallengeTestCase.is_hidden.is_(False)).order_by(ChallengeTestCase.position)).all()]
    return result
def create_submission(challenge, payload, user, db, status_prefix="submit"):
    try: get_runtime(payload.language)
    except ValueError: raise HTTPException(422,"Unsupported language")
    config=db.scalar(select(ChallengeLanguageConfig).where(ChallengeLanguageConfig.challenge_id==challenge.id,ChallengeLanguageConfig.language==payload.language))
    if not config: raise HTTPException(422,"Language is not enabled for this challenge")
    job=CodeExecutionJob(user_id=user.id,exercise_id=None,language=payload.language,source_code=payload.source_code,status="queued",expires_at=datetime.now(timezone.utc)+timedelta(minutes=10))
    db.add(job); db.flush(); submission=ChallengeSubmission(user_id=user.id,challenge_id=challenge.id,job_id=job.id,language=payload.language,source_code=payload.source_code,status="queued"); db.add(submission); db.flush()
    if not queue.enqueue(str(job.id)):
        job.status="runner_unavailable"; submission.status="runner_unavailable"; job.finished_at=datetime.now(timezone.utc); db.add(CodeExecutionResult(job_id=job.id,stderr="The secure execution runner is unavailable.",error_code="RUNNER_UNAVAILABLE"))
    db.commit(); return {"id":submission.id,"status":submission.status,"score":submission.score,"job_id":job.id}
@router.post("/{challenge_id}/run",status_code=202)
def run_samples(challenge_id: UUID,payload: SubmissionIn,user: User=Depends(verified_user),_:None=Depends(require_csrf),db: Session=Depends(get_db)):
    challenge=db.scalar(select(Challenge).where(Challenge.id==challenge_id,Challenge.published.is_(True)))
    if not challenge: raise HTTPException(404,"Challenge not found")
    return create_submission(challenge,payload,user,db,"sample")
@router.post("/{challenge_id}/submit",status_code=202)
def submit(challenge_id: UUID,payload: SubmissionIn,user: User=Depends(verified_user),_:None=Depends(require_csrf),db: Session=Depends(get_db)):
    challenge=db.scalar(select(Challenge).where(Challenge.id==challenge_id,Challenge.published.is_(True)))
    if not challenge: raise HTTPException(404,"Challenge not found")
    return create_submission(challenge,payload,user,db)
@router.post("/admin",status_code=201)
def admin_create(payload: ChallengeIn,user: User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    if db.scalar(select(Challenge).where(Challenge.slug==payload.slug)): raise HTTPException(409,"Slug already exists")
    if payload.difficulty not in {"beginner","easy","medium","hard","expert","intermediate","professional"}: raise HTTPException(422,"Invalid difficulty")
    row=Challenge(**payload.model_dump(),created_by=user.id); db.add(row); audit(db,user,"challenge_created","challenge",row.id); db.commit(); return {"id":row.id,"slug":row.slug,"status":row.status}
@router.post("/admin/{challenge_id}/languages")
def admin_language(challenge_id:UUID,payload:LanguageIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    if not db.get(Challenge,challenge_id): raise HTTPException(404,"Challenge not found")
    if db.scalar(select(ChallengeLanguageConfig).where(ChallengeLanguageConfig.challenge_id==challenge_id,ChallengeLanguageConfig.language==payload.language)): raise HTTPException(409,"Language already configured")
    row=ChallengeLanguageConfig(challenge_id=challenge_id,**payload.model_dump()); db.add(row); db.commit(); return {"id":row.id}
@router.post("/admin/{challenge_id}/tests")
def admin_test(challenge_id:UUID,payload:TestIn,user:User=Depends(admin_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    if not db.get(Challenge,challenge_id): raise HTTPException(404,"Challenge not found")
    row=ChallengeTestCase(challenge_id=challenge_id,**payload.model_dump()); db.add(row); db.commit(); return {"id":row.id,"is_hidden":row.is_hidden}
@router.post("/admin/{challenge_id}/publish")
def admin_publish(challenge_id:UUID,user:User=Depends(full_admin),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(Challenge,challenge_id)
    if not row: raise HTTPException(404,"Challenge not found")
    if not row.title.strip() or not row.description_en.strip() or not db.scalar(select(func.count(ChallengeTestCase.id)).where(ChallengeTestCase.challenge_id==row.id)): raise HTTPException(422,"Challenge needs English content and at least one test")
    row.published=True; row.status="published"; audit(db,user,"challenge_published","challenge",row.id); db.commit(); return {"id":row.id,"status":row.status,"published":row.published}
