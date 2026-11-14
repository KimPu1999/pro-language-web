from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Response, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .auth import current_user, require_csrf
from .db import get_db
from .models import IssuedCertificate, CertificateRevocation, LeaderboardPreference, StudentAchievement, StudentXPBalance, LearningStreak, User
from .admin_routes import full_admin
router=APIRouter(prefix="/api/v1/gamification",tags=["gamification"])
class PreferenceIn(BaseModel): opted_in: bool=False; display_name: str|None=Field(default=None,max_length=120)
def public_certificate(row): return {"certificate_id":row.public_id,"title":row.title,"student_name":row.student_name,"issuer":row.issuer,"issued_at":row.issued_at,"status":"revoked" if row.revoked_at else "valid","verification_url":f"/verify/{row.public_id}"}
@router.get("/certificates")
def certificates(user:User=Depends(current_user),db:Session=Depends(get_db)): return {"items":[public_certificate(x) for x in db.scalars(select(IssuedCertificate).where(IssuedCertificate.user_id==user.id,IssuedCertificate.revoked_at.is_(None)).order_by(IssuedCertificate.issued_at.desc())).all()]}
@router.get("/certificates/{certificate_id}/pdf")
def certificate_pdf(certificate_id:str,db:Session=Depends(get_db)):
    row=db.scalar(select(IssuedCertificate).where(IssuedCertificate.public_id==certificate_id));
    if not row: raise HTTPException(404,"Certificate not found")
    body=f"CodeMaster Academy\\n{row.title}\\nAwarded to {row.student_name}\\nIssued {row.issued_at.date()}\\nCertificate ID {row.public_id}\\nVerify /verify/{row.public_id}"
    stream="BT /F1 18 Tf 72 500 Td ("+body.replace("\\n", ") Tj 0 -32 Td (").replace("(","\\(").replace(")","\\)")+") Tj ET"
    pdf=f"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n3 0 obj<</Type/Page/Parent 2 0 R/MediaBox[0 0 842 595]/Resources<</Font<</F1 4 0 R>>>>/Contents 5 0 R>>endobj\n4 0 obj<</Type/Font/Subtype/Type1/BaseFont/Helvetica>>endobj\n5 0 obj<</Length {len(stream.encode())}>>stream\n{stream}\nendstream endobj\ntrailer<</Root 1 0 R>>\n%%EOF".encode()
    return Response(pdf,media_type="application/pdf",headers={"Content-Disposition":f'attachment; filename="certificate-{row.public_id}.pdf"'})
@router.get("/certificates/verify/{certificate_id}")
def verify_certificate(certificate_id:str,db:Session=Depends(get_db)):
    row=db.scalar(select(IssuedCertificate).where(IssuedCertificate.public_id==certificate_id));
    if not row:return {"status":"not_found","certificate_id":certificate_id}
    return public_certificate(row)
@router.get("/summary")
def summary(user:User=Depends(current_user),db:Session=Depends(get_db)):
    balance=db.scalar(select(StudentXPBalance).where(StudentXPBalance.user_id==user.id)); streak=db.scalar(select(LearningStreak).where(LearningStreak.user_id==user.id)); earned=db.scalar(select(func.count(StudentAchievement.id)).where(StudentAchievement.user_id==user.id)) or 0
    return {"total_xp":balance.total_xp if balance else 0,"level":balance.current_level if balance else 1,"current_streak":streak.current_streak if streak else 0,"longest_streak":streak.longest_streak if streak else 0,"badges":earned}
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
