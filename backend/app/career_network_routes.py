import json
from datetime import datetime
from urllib.parse import urlparse
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .auth import check_rate_limit, current_user, require_csrf, require_role, verified_user
from .db import get_db
from .models import (CareerApplicationEvent, CareerAuditLog, CareerEmployerOrganization, CareerEmployerVerification, CareerFraudReport, CareerJobPosting, CareerProfile, CareerProfileVisibility, CareerRoleDefinition, CareerRoleSkillRequirement, CareerSavedJob, CareerTalentContactRequest, DeveloperTalentProfile, IssuedCertificate, JobApplication, SkillDefinition, StudentSkillEvidence, User)

router=APIRouter(prefix="/api/v1/career-network",tags=["career network"])
ADMIN={"admin","platform_admin","super_admin"}
def audit(db, user, action, entity, entity_id=None): db.add(CareerAuditLog(actor_id=user.id if user else None,action=action,entity_type=entity,entity_id=entity_id))
def url_ok(value):
    parsed=urlparse(value)
    return parsed.scheme in {"https","http"} and bool(parsed.netloc) and parsed.hostname not in {"localhost","127.0.0.1","::1"}
def payload_profile(row,user,db):
    return {"username":user.display_name,"display_name":user.display_name,"headline":row.headline,"bio":row.bio,"skills":json.loads(row.skills_json),"links":json.loads(row.links_json),"interests":json.loads(row.interests_json),"verified_credentials":[{"title":c.title,"issuer":c.issuer,"verification_id":c.public_id} for c in db.scalars(select(IssuedCertificate).where(IssuedCertificate.user_id==user.id,IssuedCertificate.revoked_at.is_(None))).all()] if row.credential_share else []}
class TalentIn(BaseModel):
    headline:str=Field(default="",max_length=180); bio:str=Field(default="",max_length=5000); skills:list[str]=Field(default_factory=list,max_length=40); links:list[str]=Field(default_factory=list,max_length=10); interests:list[str]=Field(default_factory=list,max_length=20)
class VisibilityIn(BaseModel): profile_public:bool=False; employer_discoverable:bool=False; contact_allowed:bool=False; resume_share:bool=False; credential_share:bool=False
class EmployerIn(BaseModel): name:str=Field(min_length=2,max_length=180); website:str|None=None
class JobIn(BaseModel): title:str=Field(min_length=2,max_length=180); description:str=Field(min_length=1,max_length=10000); technologies:list[str]=Field(default_factory=list,max_length=30); experience_level:str="entry"; work_mode:str="remote"; location:str=""; external_url:str; expires_at:datetime|None=None
class DecisionIn(BaseModel): decision:str=Field(pattern="^(approve|reject|publish|unpublish)$"); note:str=Field(default="",max_length=2000)
class ContactIn(BaseModel): message:str=Field(min_length=1,max_length=2000)
class ReportIn(BaseModel): entity_type:str=Field(min_length=2,max_length=40); entity_id:UUID; reason:str=Field(min_length=3,max_length=2000)
class ApplicationStatusIn(BaseModel): status:str=Field(pattern="^(planned|applied|under_review|interview|offer|hired|rejected|withdrawn|closed)$"); note:str=Field(default="",max_length=2000)

@router.get("/dashboard")
def dashboard(user=Depends(current_user),db:Session=Depends(get_db)):
    profile=db.scalar(select(CareerProfile).where(CareerProfile.user_id==user.id)); talent=db.scalar(select(DeveloperTalentProfile).where(DeveloperTalentProfile.user_id==user.id)); verified=db.scalar(select(func.count(StudentSkillEvidence.id)).where(StudentSkillEvidence.user_id==user.id,StudentSkillEvidence.verified.is_(True))) or 0
    return {"profile":{"exists":bool(profile),"visibility":profile.visibility if profile else "private"},"talent":{"exists":bool(talent),"discoverable":bool(talent and talent.discoverable)},"verified_skill_evidence":verified,"privacy_note":"Career indicators are evidence summaries, not hiring predictions."}

@router.get("/talent-profile")
def get_talent(user=Depends(current_user),db:Session=Depends(get_db)):
    return db.scalar(select(DeveloperTalentProfile).where(DeveloperTalentProfile.user_id==user.id)) or {"visibility":"private","discoverable":False,"contact_allowed":False}
@router.put("/talent-profile")
def save_talent(body:TalentIn,user=Depends(verified_user),_=Depends(require_csrf),db:Session=Depends(get_db)):
    if any(not url_ok(x) for x in body.links): raise HTTPException(422,"Links must be valid external URLs")
    row=db.scalar(select(DeveloperTalentProfile).where(DeveloperTalentProfile.user_id==user.id)) or DeveloperTalentProfile(user_id=user.id)
    row.headline=body.headline;row.bio=body.bio;row.skills_json=json.dumps(body.skills);row.links_json=json.dumps(body.links);row.interests_json=json.dumps(body.interests);db.add(row);audit(db,user,"talent_profile_updated","talent_profile",row.id);db.commit();return row
@router.get("/visibility")
def get_visibility(user=Depends(current_user),db:Session=Depends(get_db)):
    return db.scalar(select(CareerProfileVisibility).where(CareerProfileVisibility.user_id==user.id)) or {"profile_public":False,"employer_discoverable":False,"contact_allowed":False,"resume_share":False,"credential_share":False}
@router.put("/visibility")
def save_visibility(body:VisibilityIn,user=Depends(verified_user),_=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.scalar(select(CareerProfileVisibility).where(CareerProfileVisibility.user_id==user.id)) or CareerProfileVisibility(user_id=user.id)
    for k,v in body.model_dump().items(): setattr(row,k,v)
    talent=db.scalar(select(DeveloperTalentProfile).where(DeveloperTalentProfile.user_id==user.id)) or DeveloperTalentProfile(user_id=user.id);talent.visibility="public" if body.profile_public else "private";talent.discoverable=body.employer_discoverable;talent.contact_allowed=body.contact_allowed;talent.resume_share=body.resume_share;talent.credential_share=body.credential_share;db.add_all([row,talent]);audit(db,user,"career_visibility_updated","career_profile",row.id);db.commit();return row
@router.get("/profiles/{username}")
def public_profile(username:str,db:Session=Depends(get_db)):
    user=db.scalar(select(User).where(User.display_name==username,User.account_status=="active")); talent=db.scalar(select(DeveloperTalentProfile).where(DeveloperTalentProfile.user_id==user.id)) if user else None
    if not user or not talent or talent.visibility!="public": raise HTTPException(404,"Developer profile not found")
    return payload_profile(talent,user,db)
@router.get("/skill-gap")
def skill_gap(role_slug:str|None=None,user=Depends(verified_user),db:Session=Depends(get_db)):
    role=db.scalar(select(CareerRoleDefinition).where(CareerRoleDefinition.slug==role_slug,CareerRoleDefinition.status=="published")) if role_slug else db.scalar(select(CareerRoleDefinition).where(CareerRoleDefinition.status=="published").order_by(CareerRoleDefinition.title))
    if not role:return {"role":None,"matched":[],"missing":[],"evidence_based":True}
    req=db.scalars(select(CareerRoleSkillRequirement,SkillDefinition).join(SkillDefinition,SkillDefinition.id==CareerRoleSkillRequirement.skill_id).where(CareerRoleSkillRequirement.role_id==role.id)).all(); evidence=db.scalars(select(StudentSkillEvidence).where(StudentSkillEvidence.user_id==user.id,StudentSkillEvidence.verified.is_(True))).all(); skill_ids={x.skill_id for x in evidence}; matched=[{"skill":skill.name,"slug":skill.slug,"required_level":r.required_level} for r,skill in req if r.skill_id in skill_ids]; missing=[{"skill":skill.name,"slug":skill.slug,"required_level":r.required_level} for r,skill in req if r.required and r.skill_id not in skill_ids]
    return {"role":{"slug":role.slug,"title":role.title},"matched":matched,"missing":missing,"evidence_based":True,"disclaimer":"This is a learning gap view, not a hiring prediction."}

@router.get("/jobs")
def jobs(search:str|None=None,experience_level:str|None=None,limit:int=Query(20,ge=1,le=50),offset:int=Query(0,ge=0),db:Session=Depends(get_db)):
    q=select(CareerJobPosting).join(CareerEmployerOrganization).where(CareerJobPosting.status=="published",CareerEmployerOrganization.verification_status=="verified")
    if search:q=q.where(CareerJobPosting.title.ilike(f"%{search}%"))
    if experience_level:q=q.where(CareerJobPosting.experience_level==experience_level)
    rows=db.scalars(q.order_by(CareerJobPosting.created_at.desc()).offset(offset).limit(limit)).all();return [{"id":x.id,"title":x.title,"description":x.description,"technologies":json.loads(x.technologies_json),"experience_level":x.experience_level,"work_mode":x.work_mode,"location":x.location,"external_url":x.external_url,"expires_at":x.expires_at} for x in rows]
@router.post("/jobs/{job_id}/save",status_code=201)
def save_job(job_id:UUID,user=Depends(verified_user),_=Depends(require_csrf),db:Session=Depends(get_db)):
    if not db.scalar(select(CareerJobPosting).where(CareerJobPosting.id==job_id,CareerJobPosting.status=="published")):raise HTTPException(404,"Published job not found")
    row=CareerSavedJob(user_id=user.id,job_id=job_id);db.add(row)
    try:db.commit()
    except Exception:db.rollback();raise HTTPException(409,"Job already saved")
    return {"saved":True}
@router.patch("/applications/{application_id}/status")
def application_status(application_id:UUID,body:ApplicationStatusIn,user=Depends(verified_user),_=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.scalar(select(JobApplication).where(JobApplication.id==application_id,JobApplication.user_id==user.id))
    if not row: raise HTTPException(404,"Application not found")
    allowed={"planned":{"applied","withdrawn","closed"},"applied":{"under_review","interview","offer","rejected","withdrawn","closed"},"under_review":{"interview","offer","rejected","withdrawn","closed"},"interview":{"offer","hired","rejected","withdrawn","closed"},"offer":{"hired","rejected","withdrawn","closed"},"hired":{"closed"},"rejected":{"closed"},"withdrawn":{"closed"},"closed":set()}
    if body.status!=row.status and body.status not in allowed.get(row.status,set()): raise HTTPException(409,"Invalid application status transition")
    old=row.status;row.status=body.status;db.add(CareerApplicationEvent(application_id=row.id,actor_id=user.id,from_status=old,to_status=body.status,note=body.note));audit(db,user,"application_status_changed","application",row.id);db.commit();return {"id":row.id,"status":row.status}
@router.post("/employer/organizations",status_code=201)
def create_employer(body:EmployerIn,user=Depends(verified_user),_=Depends(require_csrf),db:Session=Depends(get_db)):
    if body.website and not url_ok(body.website):raise HTTPException(422,"Website must be an external URL")
    row=CareerEmployerOrganization(owner_id=user.id,name=body.name,website=body.website);db.add(row);db.flush();db.add(CareerEmployerVerification(employer_id=row.id,evidence="Awaiting platform review"));audit(db,user,"employer_created","employer",row.id);db.commit();return {"id":row.id,"verification_status":row.verification_status}
@router.post("/employer/jobs",status_code=201)
def create_job(body:JobIn,employer=Depends(verified_user),_=Depends(require_csrf),db:Session=Depends(get_db)):
    if not url_ok(body.external_url):raise HTTPException(422,"Job link must be an external URL")
    org=db.scalar(select(CareerEmployerOrganization).where(CareerEmployerOrganization.owner_id==employer.id));
    if not org or org.verification_status!="verified":raise HTTPException(403,"Verified employer organization required")
    row=CareerJobPosting(employer_id=org.id,created_by=employer.id,title=body.title,description=body.description,technologies_json=json.dumps(body.technologies),experience_level=body.experience_level,work_mode=body.work_mode,location=body.location,external_url=body.external_url,expires_at=body.expires_at,status="pending");db.add(row);audit(db,employer,"job_submitted","job",row.id);db.commit();return {"id":row.id,"status":row.status}
@router.get("/employer/talent")
def talent(search:str|None=None,user=Depends(verified_user),db:Session=Depends(get_db)):
    org=db.scalar(select(CareerEmployerOrganization).where(CareerEmployerOrganization.owner_id==user.id,CareerEmployerOrganization.verification_status=="verified"));
    if not org:raise HTTPException(403,"Verified employer organization required")
    q=select(DeveloperTalentProfile,User).join(User,User.id==DeveloperTalentProfile.user_id).where(DeveloperTalentProfile.discoverable.is_(True),DeveloperTalentProfile.visibility=="public")
    rows=db.execute(q).all();return [{"user_id":u.id,"display_name":u.display_name,"headline":p.headline,"skills":json.loads(p.skills_json),"contact_allowed":p.contact_allowed} for p,u in rows if not search or search.lower() in (p.headline+" "+p.skills_json).lower()]
@router.post("/employer/talent/{talent_id}/contact",status_code=201)
def contact(talent_id:UUID,body:ContactIn,user=Depends(verified_user),_=Depends(require_csrf),db:Session=Depends(get_db)):
    check_rate_limit(f"career-contact:{user.id}",5,3600);org=db.scalar(select(CareerEmployerOrganization).where(CareerEmployerOrganization.owner_id==user.id,CareerEmployerOrganization.verification_status=="verified"));p=db.scalar(select(DeveloperTalentProfile).where(DeveloperTalentProfile.user_id==talent_id,DeveloperTalentProfile.discoverable.is_(True),DeveloperTalentProfile.contact_allowed.is_(True)))
    if not org or not p:raise HTTPException(404,"Talent contact is unavailable")
    row=CareerTalentContactRequest(employer_id=org.id,talent_user_id=talent_id,sender_id=user.id,message=body.message);db.add(row);audit(db,user,"talent_contact_requested","talent",talent_id);db.commit();return {"id":row.id,"status":row.status}
@router.post("/platform/employers/{employer_id}/decision")
def employer_decision(employer_id:UUID,body:DecisionIn,user=Depends(require_role(*ADMIN)),_=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(CareerEmployerOrganization,employer_id)
    if not row:raise HTTPException(404,"Employer not found")
    row.verification_status="verified" if body.decision=="approve" else "rejected";db.add(CareerEmployerVerification(employer_id=row.id,reviewer_id=user.id,status=row.verification_status,note=body.note));audit(db,user,"employer_decision","employer",row.id);db.commit();return {"id":row.id,"verification_status":row.verification_status}
@router.post("/platform/jobs/{job_id}/decision")
def job_decision(job_id:UUID,body:DecisionIn,user=Depends(require_role(*ADMIN)),_=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(CareerJobPosting,job_id)
    if not row:raise HTTPException(404,"Job not found")
    row.status="published" if body.decision=="publish" else "rejected" if body.decision=="reject" else "draft";audit(db,user,"job_decision","job",row.id);db.commit();return {"id":row.id,"status":row.status}
@router.get("/platform/overview")
def platform_overview(user=Depends(require_role(*ADMIN)),db:Session=Depends(get_db)):
    return {"employers_pending":db.scalar(select(func.count(CareerEmployerOrganization.id)).where(CareerEmployerOrganization.verification_status=="pending")) or 0,"jobs_pending":db.scalar(select(func.count(CareerJobPosting.id)).where(CareerJobPosting.status=="pending")) or 0,"discoverable_talent":db.scalar(select(func.count(DeveloperTalentProfile.id)).where(DeveloperTalentProfile.discoverable.is_(True),DeveloperTalentProfile.visibility=="public")) or 0,"note":"Counts are operational records; no hiring outcomes are inferred."}
@router.post("/reports",status_code=201)
def report(body:ReportIn,user=Depends(verified_user),_=Depends(require_csrf),db:Session=Depends(get_db)):
    check_rate_limit(f"career-report:{user.id}",5,3600);row=CareerFraudReport(reporter_id=user.id,entity_type=body.entity_type,entity_id=body.entity_id,reason=body.reason);db.add(row);audit(db,user,"fraud_report_created","report",row.id);db.commit();return {"id":row.id,"status":row.status}
