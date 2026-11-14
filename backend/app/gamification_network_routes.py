import json
from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .admin_routes import full_admin, admin_user
from .auth import current_user, require_csrf, verified_user, check_rate_limit
from .db import get_db
from .models import (Challenge, CompetitionAppeal, CompetitionIntegrityCase, CompetitionParticipant, CompetitionRanking, CodingCompetition, GamificationAchievementAward, GamificationLevelRule, GamificationQuestAssignment, GamificationQuestCompletion, GamificationQuestDefinition, GamificationQuestVersion, GamificationStreakRecord, GamificationXPLedger, LeaderboardPreference, LearningStreak, StudentAchievement, StudentChallengeProgress, StudentXPBalance, User)

router=APIRouter(prefix="/api/v1/gamification-network",tags=["gamification network"])
class QuestIn(BaseModel): slug:str=Field(pattern=r"^[a-z0-9-]+$"); title:str=Field(min_length=2,max_length=180); description:str=Field(min_length=1,max_length=5000); quest_type:str=Field(pattern="^(daily|weekly|learning_path|skill|community|team)$"); rule_type:str=Field(pattern="^(challenge_solved|verified_event)$"); rule:dict={}; xp_reward:int=Field(ge=0,le=10000)
class AppealIn(BaseModel): reason:str=Field(min_length=3,max_length=4000)
class IntegrityIn(BaseModel): competition_id:UUID; subject_user_id:UUID; signal_type:str=Field(min_length=2,max_length=60); evidence_summary:str=Field(min_length=3,max_length=4000)
class LevelIn(BaseModel): version:str=Field(min_length=1,max_length=40); level:int=Field(ge=1,le=1000); minimum_xp:int=Field(ge=0); title:str=Field(default="",max_length=100)
def audit(db,user,action,entity,entity_id=None):
    from .models import GamificationAuditLog
    db.add(GamificationAuditLog(actor_id=user.id if user else None,action=action,entity_type=entity,entity_id=entity_id))
def level_for(db,xp):
    row=db.scalars(select(GamificationLevelRule).where(GamificationLevelRule.minimum_xp<=xp).order_by(GamificationLevelRule.minimum_xp.desc())).first();return row.level if row else 1
@router.get("/dashboard")
def dashboard(user=Depends(current_user),db:Session=Depends(get_db)):
    balance=db.scalar(select(StudentXPBalance).where(StudentXPBalance.user_id==user.id));ledger=db.scalar(select(func.coalesce(func.sum(GamificationXPLedger.amount),0)).where(GamificationXPLedger.user_id==user.id,GamificationXPLedger.status=="posted")) or 0;completed=db.scalar(select(func.count(GamificationQuestCompletion.id)).where(GamificationQuestCompletion.user_id==user.id,GamificationQuestCompletion.verified.is_(True))) or 0;awards=db.scalar(select(func.count(StudentAchievement.id)).where(StudentAchievement.user_id==user.id)) or 0
    return {"verified_xp":int(ledger),"level":balance.current_level if balance else level_for(db,int(ledger)),"completed_quests":completed,"achievements":awards,"streak":{"current":db.scalar(select(GamificationStreakRecord.current_streak).where(GamificationStreakRecord.user_id==user.id)) or db.scalar(select(LearningStreak.current_streak).where(LearningStreak.user_id==user.id)) or 0},"free_features":True}
@router.get("/quests")
def quests(user=Depends(current_user),db:Session=Depends(get_db)):
    rows=db.execute(select(GamificationQuestAssignment,GamificationQuestDefinition,GamificationQuestVersion).join(GamificationQuestDefinition,GamificationQuestDefinition.id==GamificationQuestAssignment.quest_id).join(GamificationQuestVersion,GamificationQuestVersion.id==GamificationQuestAssignment.version_id).where(GamificationQuestAssignment.user_id==user.id,GamificationQuestAssignment.status=="active")).all();return [{"assignment_id":a.id,"title":q.title,"description":q.description,"quest_type":q.quest_type,"xp_reward":v.xp_reward,"expires_at":a.expires_at,"completed":bool(db.scalar(select(GamificationQuestCompletion.id).where(GamificationQuestCompletion.assignment_id==a.id)))} for a,q,v in rows]
@router.post("/admin/quests",status_code=201)
def create_quest(body:QuestIn,user=Depends(admin_user),_=Depends(require_csrf),db:Session=Depends(get_db)):
    if db.scalar(select(GamificationQuestDefinition).where(GamificationQuestDefinition.slug==body.slug)):raise HTTPException(409,"Quest slug already exists")
    q=GamificationQuestDefinition(slug=body.slug,title=body.title,description=body.description,quest_type=body.quest_type,status="published");db.add(q);db.flush();v=GamificationQuestVersion(quest_id=q.id,version=1,rule_type=body.rule_type,rule_json=json.dumps(body.rule),xp_reward=body.xp_reward,status="published");db.add(v);audit(db,user,"quest_published","quest",q.id);db.commit();return {"id":q.id,"version_id":v.id,"status":q.status}
@router.post("/admin/quests/{quest_id}/assign/{user_id}",status_code=201)
def assign(quest_id:UUID,user_id:UUID,user=Depends(admin_user),_=Depends(require_csrf),db:Session=Depends(get_db)):
    q=db.get(GamificationQuestDefinition,quest_id);v=db.scalar(select(GamificationQuestVersion).where(GamificationQuestVersion.quest_id==quest_id,GamificationQuestVersion.status=="published").order_by(GamificationQuestVersion.version.desc()));
    if not q or not v or not db.get(User,user_id):raise HTTPException(404,"Published quest or user not found")
    row=GamificationQuestAssignment(quest_id=q.id,version_id=v.id,user_id=user_id);db.add(row)
    try:db.commit()
    except IntegrityError:db.rollback();raise HTTPException(409,"Quest already assigned")
    return {"id":row.id,"status":row.status}
@router.post("/quests/{assignment_id}/complete")
def complete(assignment_id:UUID,user=Depends(verified_user),_=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.scalar(select(GamificationQuestAssignment).where(GamificationQuestAssignment.id==assignment_id,GamificationQuestAssignment.user_id==user.id));
    if not row:raise HTTPException(404,"Quest assignment not found")
    if row.expires_at and row.expires_at<=datetime.now(timezone.utc):raise HTTPException(409,"Quest has expired")
    version=db.get(GamificationQuestVersion,row.version_id);rule=json.loads(version.rule_json or "{}");verified=False;evidence_id=None
    if version.rule_type=="challenge_solved":
        try:challenge_id=UUID(str(rule["challenge_id"]))
        except (KeyError,ValueError):raise HTTPException(422,"Quest rule is invalid")
        solved=db.scalar(select(StudentChallengeProgress).where(StudentChallengeProgress.user_id==user.id,StudentChallengeProgress.challenge_id==challenge_id,StudentChallengeProgress.solved.is_(True)));verified=bool(solved);evidence_id=challenge_id
    if not verified:raise HTTPException(409,"Required verified evidence is not present")
    existing=db.scalar(select(GamificationQuestCompletion).where(GamificationQuestCompletion.assignment_id==row.id))
    if existing:return {"status":"already_completed"}
    completion=GamificationQuestCompletion(assignment_id=row.id,user_id=user.id,evidence_type=version.rule_type,evidence_id=evidence_id,verified=True);db.add(completion)
    try:
        db.flush()
        ledger=GamificationXPLedger(user_id=user.id,amount=version.xp_reward,evidence_type="quest_completion",evidence_id=completion.id,rule_version=f"quest-{version.version}");db.add(ledger);balance=db.scalar(select(StudentXPBalance).where(StudentXPBalance.user_id==user.id)) or StudentXPBalance(user_id=user.id);balance.total_xp=(balance.total_xp or 0)+version.xp_reward;balance.current_level=level_for(db,balance.total_xp);db.add(balance);audit(db,user,"quest_completed","quest_assignment",row.id)
        db.commit()
    except IntegrityError:db.rollback();return {"status":"already_completed"}
    return {"status":"verified","xp_awarded":version.xp_reward,"level":balance.current_level}
@router.get("/challenges/global")
def global_challenges(search:str|None=None,db:Session=Depends(get_db)):
    q=select(Challenge).where(Challenge.published.is_(True));
    if search:q=q.where(Challenge.title.ilike(f"%{search}%"))
    return [{"id":x.id,"slug":x.slug,"title":x.title,"difficulty":x.difficulty,"description":x.description_en} for x in db.scalars(q.order_by(Challenge.title).limit(100)).all()]
@router.get("/competitions")
def competition_list(db:Session=Depends(get_db)):return db.scalars(select(CodingCompetition).where(CodingCompetition.published.is_(True)).order_by(CodingCompetition.starts_at)).all()
@router.get("/leaderboards")
def leaderboards(period:str=Query("all_time",pattern="^(weekly|monthly|all_time)$"),db:Session=Depends(get_db)):
    rows=db.execute(select(User.display_name,StudentXPBalance.total_xp).join(StudentXPBalance,StudentXPBalance.user_id==User.id).join(LeaderboardPreference,LeaderboardPreference.user_id==User.id).where(LeaderboardPreference.opted_in.is_(True)).order_by(StudentXPBalance.total_xp.desc()).limit(100)).all();return {"period":period,"verified_only":True,"items":[{"display_name":name,"xp":xp,"rank":i+1} for i,(name,xp) in enumerate(rows)]}
@router.post("/competitions/{competition_id}/appeals",status_code=201)
def appeal(competition_id:UUID,body:AppealIn,user=Depends(verified_user),_=Depends(require_csrf),db:Session=Depends(get_db)):
    if not db.scalar(select(CodingCompetition.id).where(CodingCompetition.id==competition_id)):raise HTTPException(404,"Competition not found")
    row=CompetitionAppeal(competition_id=competition_id,appellant_id=user.id,reason=body.reason);db.add(row);db.commit();return {"id":row.id,"status":row.status}
@router.get("/platform/integrity")
def integrity(user=Depends(full_admin),db:Session=Depends(get_db)):return db.scalars(select(CompetitionIntegrityCase).where(CompetitionIntegrityCase.status=="open").order_by(CompetitionIntegrityCase.created_at)).all()
@router.post("/platform/integrity",status_code=201)
def create_integrity(body:IntegrityIn,user=Depends(full_admin),_=Depends(require_csrf),db:Session=Depends(get_db)):
    row=CompetitionIntegrityCase(**body.model_dump(),status="open");db.add(row);audit(db,user,"integrity_case_created","competition",body.competition_id);db.commit();return {"id":row.id,"status":row.status,"human_review_required":True}
@router.get("/platform/analytics")
def analytics(user=Depends(full_admin),db:Session=Depends(get_db)):
    return {"assigned_quests":db.scalar(select(func.count()).select_from(GamificationQuestAssignment)) or 0,"verified_completions":db.scalar(select(func.count()).select_from(GamificationQuestCompletion).where(GamificationQuestCompletion.verified.is_(True))) or 0,"published_competitions":db.scalar(select(func.count()).select_from(CodingCompetition).where(CodingCompetition.published.is_(True))) or 0,"open_integrity_cases":db.scalar(select(func.count()).select_from(CompetitionIntegrityCase).where(CompetitionIntegrityCase.status=="open")) or 0,"data_source":"postgresql","fair_play":"automated signals require human review"}
