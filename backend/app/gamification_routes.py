from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Response, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .auth import current_user, require_csrf
from .certificate_service import certificate_payload
from .db import get_db
from .models import AchievementDefinition, IssuedCertificate, CertificateRevocation, LeaderboardPreference, StudentAchievement, StudentXPBalance, LearningStreak, User
from .admin_routes import full_admin
router=APIRouter(prefix="/api/v1/gamification",tags=["gamification"])
class PreferenceIn(BaseModel): opted_in: bool=False; display_name: str|None=Field(default=None,max_length=120)
def public_certificate(row): return certificate_payload(row, include_recipient=True)
@router.get("/certificates")
def certificates(user:User=Depends(current_user),db:Session=Depends(get_db)): return {"items":[public_certificate(x) for x in db.scalars(select(IssuedCertificate).where(IssuedCertificate.user_id==user.id,IssuedCertificate.revoked_at.is_(None)).order_by(IssuedCertificate.issued_at.desc())).all()]}
@router.get("/certificates/{certificate_id}/pdf")
def certificate_pdf(certificate_id:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
    row=db.scalar(select(IssuedCertificate).where(IssuedCertificate.public_id==certificate_id, IssuedCertificate.user_id==user.id))
    if not row: raise HTTPException(404,"Certificate not found")
    from .certificate_routes import _pdf_response
    return _pdf_response(row)
@router.get("/certificates/verify/{certificate_id}")
def verify_certificate(certificate_id:str,db:Session=Depends(get_db)):
    row=db.scalar(select(IssuedCertificate).where(IssuedCertificate.public_id==certificate_id));
    if not row:return {"status":"not_found","certificate_id":certificate_id}
    return public_certificate(row)
@router.get("/summary")
def summary(user:User=Depends(current_user),db:Session=Depends(get_db)):
    balance=db.scalar(select(StudentXPBalance).where(StudentXPBalance.user_id==user.id)); streak=db.scalar(select(LearningStreak).where(LearningStreak.user_id==user.id)); earned=db.scalar(select(func.count(StudentAchievement.id)).where(StudentAchievement.user_id==user.id)) or 0
    return {"total_xp":balance.total_xp if balance else 0,"level":balance.current_level if balance else 1,"current_streak":streak.current_streak if streak else 0,"longest_streak":streak.longest_streak if streak else 0,"badges":earned}
@router.get("/achievements")
def achievements(user:User=Depends(current_user),db:Session=Depends(get_db)):
    earned={row.achievement_id:row.awarded_at for row in db.scalars(select(StudentAchievement).where(StudentAchievement.user_id==user.id)).all()}
    definitions=db.scalars(select(AchievementDefinition).order_by(AchievementDefinition.created_at)).all()
    return {"items":[{"id":row.id,"slug":row.slug,"title":row.title,"description":row.description,"threshold":row.threshold,"earned":row.id in earned,"awarded_at":earned.get(row.id)} for row in definitions]}
@router.get("/leaderboard")
def leaderboard(period:str=Query("all_time",pattern="^(weekly|monthly|all_time)$"),page:int=Query(1,ge=1),page_size:int=Query(20,ge=1,le=50),db:Session=Depends(get_db)):
    rows=db.execute(select(User.display_name,StudentXPBalance.total_xp).join(StudentXPBalance,StudentXPBalance.user_id==User.id).join(LeaderboardPreference,LeaderboardPreference.user_id==User.id).where(LeaderboardPreference.opted_in.is_(True)).order_by(StudentXPBalance.total_xp.desc()).offset((page-1)*page_size).limit(page_size)).all()
    return {"period":period,"items":[{"display_name":x[0],"xp":x[1],"rank":(page-1)*page_size+i+1} for i,x in enumerate(rows)]}
@router.get("/leaderboard/preferences")
def get_preference(user:User=Depends(current_user),db:Session=Depends(get_db)):
    row=db.scalar(select(LeaderboardPreference).where(LeaderboardPreference.user_id==user.id));return {"opted_in":row.opted_in,"display_name":row.display_name} if row else {"opted_in":False,"display_name":None}
@router.put("/leaderboard/preferences")
def save_preference(payload:PreferenceIn,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.scalar(select(LeaderboardPreference).where(LeaderboardPreference.user_id==user.id)) or LeaderboardPreference(user_id=user.id);row.opted_in=payload.opted_in;row.display_name=payload.display_name or user.display_name;db.add(row);db.commit();return {"opted_in":row.opted_in,"display_name":row.display_name}
@router.post("/admin/certificates/{certificate_id}/revoke")
def revoke(certificate_id:str,reason:str=Query(...,min_length=3,max_length=500),user:User=Depends(full_admin),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.scalar(select(IssuedCertificate).where(IssuedCertificate.public_id==certificate_id));
    if not row:raise HTTPException(404,"Certificate not found")
    if not row.revoked_at:row.revoked_at=datetime.now(timezone.utc);db.add(CertificateRevocation(certificate_id=row.id,revoked_by=user.id,reason=reason));db.commit()
    return public_certificate(row)
