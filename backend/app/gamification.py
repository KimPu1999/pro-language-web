from datetime import datetime, timezone
from uuid import UUID
import secrets
from sqlalchemy import select
from sqlalchemy.orm import Session
from .models import XPEvent, StudentXPBalance, XPLevelDefinition, LearningStreak, StreakActivityDay, CertificateTemplate, IssuedCertificate, User

XP_RULES={"lesson_completed":10,"challenge_accepted":30,"course_completed":100,"project_approved":150,"roadmap_completed":300}
def award_verified_event(db:Session,user_id:UUID,event_type:str,idempotency_key:str,source_id:UUID|None=None,activity_day:str|None=None,timezone_name:str="UTC"):
    amount=XP_RULES.get(event_type)
    if amount is None: raise ValueError("Unsupported verified event")
    existing=db.scalar(select(XPEvent).where(XPEvent.user_id==user_id,XPEvent.idempotency_key==idempotency_key))
    if existing:return existing
    event=XPEvent(user_id=user_id,event_type=event_type,source_id=source_id,idempotency_key=idempotency_key,amount=amount);db.add(event)
    balance=db.scalar(select(StudentXPBalance).where(StudentXPBalance.user_id==user_id)) or StudentXPBalance(user_id=user_id);balance.total_xp=(balance.total_xp or 0)+amount
    levels=db.scalars(select(XPLevelDefinition).order_by(XPLevelDefinition.required_xp)).all();balance.current_level=max([x.level for x in levels if x.required_xp<=balance.total_xp] or [1]);db.add(balance)
    if activity_day:
        day=db.scalar(select(StreakActivityDay).where(StreakActivityDay.user_id==user_id,StreakActivityDay.activity_day==activity_day))
        if not day: db.add(StreakActivityDay(user_id=user_id,activity_day=activity_day,source_type=event_type,source_id=source_id));streak=db.scalar(select(LearningStreak).where(LearningStreak.user_id==user_id)) or LearningStreak(user_id=user_id,timezone=timezone_name);streak.current_streak=streak.current_streak+1 if streak.last_activity_day and streak.last_activity_day!=activity_day else max(streak.current_streak,1);streak.longest_streak=max(streak.longest_streak,streak.current_streak);streak.last_activity_day=activity_day;db.add(streak)
    return event
def issue_certificate(db:Session,user:User,template_id:UUID,achievement_type:str,resource_id:UUID|None,title:str,policy_version:int=1):
    existing=db.scalar(select(IssuedCertificate).where(IssuedCertificate.user_id==user.id,IssuedCertificate.achievement_type==achievement_type,IssuedCertificate.resource_id==resource_id,IssuedCertificate.revoked_at.is_(None)))
    if existing:return existing
    template=db.get(CertificateTemplate,template_id)
    if not template or not template.active: raise ValueError("Certificate template unavailable")
    row=IssuedCertificate(public_id=secrets.token_urlsafe(24),user_id=user.id,template_id=template.id,achievement_type=achievement_type,resource_id=resource_id,title=title,student_name=user.display_name,issuer=template.issuer,policy_version=policy_version);db.add(row);return row
