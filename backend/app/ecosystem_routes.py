import hashlib,hmac,json
from datetime import datetime,timezone
from uuid import UUID
from fastapi import APIRouter,Depends,Header,HTTPException,Request
from pydantic import BaseModel,Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from .auth import current_user,require_csrf,require_role,verified_user
from .rbac import PLATFORM_ADMIN_ROLES
from .config import settings
from .db import get_db
from .models import (CodeReviewFeedback,CodeReviewRequest,CollaborationRequest,ContributionRecord,
    DeveloperEcosystemAuditLog,DeveloperPublicProfile,GithubConnection,GithubWebhookEvent,
    OpenSourceOpportunity,OpenSourceProject,OpenSourceProjectMember,User)

router=APIRouter(prefix="/api/v1",tags=["developer ecosystem"]);ADMIN=PLATFORM_ADMIN_ROLES
class ProfileIn(BaseModel):username:str=Field(pattern=r"^[a-zA-Z0-9_-]{3,80}$");headline:str="";bio:str="";visibility:str="private";show_contributions:bool=False
class ReviewIn(BaseModel):body:str=Field(min_length=1,max_length=5000);project_id:UUID|None=None;contribution_id:UUID|None=None
class CollaborationIn(BaseModel):message:str=Field(default="",max_length=3000)
class ProjectIn(BaseModel):github_owner:str=Field(min_length=1,max_length=120);github_repo:str=Field(min_length=1,max_length=180);name:str=Field(min_length=1,max_length=180);description:str="";guidelines_url:str|None=None
def utcnow():return datetime.now(timezone.utc)
def github_status():return {"enabled":settings.github_enabled and bool(settings.github_app_id or settings.github_client_id),"provider":"github_app" if settings.github_enabled else "disabled","message":"GitHub is configured." if settings.github_enabled else "Not Configured: GitHub credentials are not available."}

@router.get("/developers")
def developer_hub(user:User=Depends(current_user),db:Session=Depends(get_db)):
    connection=db.scalar(select(GithubConnection).where(GithubConnection.user_id==user.id)); contributions=db.scalars(select(ContributionRecord).where(ContributionRecord.user_id==user.id,ContributionRecord.verified.is_(True)).order_by(ContributionRecord.occurred_at.desc()).limit(20)).all();reviews=db.scalars(select(CodeReviewRequest).where(CodeReviewRequest.requester_id==user.id).order_by(CodeReviewRequest.created_at.desc()).limit(10)).all()
    return {"github":github_status()|{"connected":bool(connection and connection.status=="active"),"login":connection.github_login if connection else None},"contributions":contributions,"reviews":reviews,"projects":db.scalars(select(OpenSourceProject).where(OpenSourceProject.status=="approved",OpenSourceProject.public.is_(True)).limit(10)).all()}
@router.get("/github/status")
def github_connection_status(user:User=Depends(current_user),db:Session=Depends(get_db)):
    row=db.scalar(select(GithubConnection).where(GithubConnection.user_id==user.id));return github_status()|{"connected":bool(row and row.status=="active"),"login":row.github_login if row else None,"expires_at":row.token_expires_at if row else None}
@router.get("/github/connect")
def github_connect(user:User=Depends(current_user)):
    if not settings.github_enabled or not settings.github_client_id: return {"status":"unavailable",**github_status()}
    return {"status":"not_implemented","message":"OAuth authorization URL generation requires the configured deployment callback and PKCE state store."}
@router.delete("/github/disconnect")
def github_disconnect(user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.scalar(select(GithubConnection).where(GithubConnection.user_id==user.id))
    if row:row.status="revoked";row.encrypted_access_token=None;db.commit()
    return {"status":"disconnected"}
@router.get("/developers/contributions")
def contributions(user:User=Depends(current_user),db:Session=Depends(get_db)):return {"items":db.scalars(select(ContributionRecord).where(ContributionRecord.user_id==user.id,ContributionRecord.verified.is_(True)).order_by(ContributionRecord.occurred_at.desc())).all(),"definitions":{"verified":"Only server-synced GitHub evidence with verification records.","merged":"Pull requests whose synchronized GitHub state is merged."}}
@router.get("/open-source/projects")
def projects(db:Session=Depends(get_db)):return db.scalars(select(OpenSourceProject).where(OpenSourceProject.status=="approved",OpenSourceProject.public.is_(True)).order_by(OpenSourceProject.name)).all()
@router.get("/open-source/opportunities")
def opportunities(db:Session=Depends(get_db)):return db.scalars(select(OpenSourceOpportunity).join(OpenSourceProject).where(OpenSourceOpportunity.status=="open",OpenSourceProject.status=="approved",OpenSourceProject.public.is_(True)).order_by(OpenSourceOpportunity.created_at.desc())).all()
@router.post("/open-source/projects",status_code=201)
def register_project(payload:ProjectIn,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    if not settings.github_enabled:raise HTTPException(503,"GitHub integration is not configured; repository ownership cannot be verified")
    connection=db.scalar(select(GithubConnection).where(GithubConnection.user_id==user.id,GithubConnection.status=="active"))
    if not connection:raise HTTPException(403,"Connect GitHub before registering a repository")
    if db.scalar(select(OpenSourceProject).where(OpenSourceProject.github_owner==payload.github_owner,OpenSourceProject.github_repo==payload.github_repo)):raise HTTPException(409,"Repository already registered")
    row=OpenSourceProject(registered_by=user.id,github_owner=payload.github_owner,github_repo=payload.github_repo,name=payload.name,description=payload.description,guidelines_url=payload.guidelines_url,status="pending");db.add(row);db.commit();return {"id":row.id,"status":row.status}
@router.post("/open-source/projects/{project_id}/collaboration",status_code=201)
def collaboration(project_id:UUID,payload:CollaborationIn,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    project=db.scalar(select(OpenSourceProject).where(OpenSourceProject.id==project_id,OpenSourceProject.status=="approved",OpenSourceProject.public.is_(True)))
    if not project:raise HTTPException(404,"Open-source project not found")
    db.add(CollaborationRequest(project_id=project.id,requester_id=user.id,message=payload.message));db.commit();return {"status":"requested"}
@router.post("/developers/reviews",status_code=201)
def review_request(payload:ReviewIn,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    if not payload.project_id and not payload.contribution_id:raise HTTPException(422,"A project or verified contribution is required")
    row=CodeReviewRequest(requester_id=user.id,project_id=payload.project_id,contribution_id=payload.contribution_id,body=payload.body);db.add(row);db.commit();return {"id":row.id,"status":row.status}
@router.get("/developers/reviews")
def reviews(user:User=Depends(current_user),db:Session=Depends(get_db)):return db.scalars(select(CodeReviewRequest).where((CodeReviewRequest.requester_id==user.id)|(CodeReviewRequest.reviewer_id==user.id)).order_by(CodeReviewRequest.created_at.desc())).all()
@router.get("/developers/{username}")
def public_profile(username:str,db:Session=Depends(get_db)):
    row=db.scalar(select(DeveloperPublicProfile).where(DeveloperPublicProfile.username==username,DeveloperPublicProfile.visibility=="public"))
    if not row:raise HTTPException(404,"Developer profile not found")
    data={"username":row.username,"headline":row.headline,"bio":row.bio}
    if row.show_contributions:data["contributions"]=db.scalars(select(ContributionRecord).where(ContributionRecord.user_id==row.user_id,ContributionRecord.verified.is_(True))).all()
    return data
@router.put("/profile/developer")
def save_profile(payload:ProfileIn,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.scalar(select(DeveloperPublicProfile).where(DeveloperPublicProfile.user_id==user.id)) or DeveloperPublicProfile(user_id=user.id,username=payload.username);row.username=payload.username;row.headline=payload.headline;row.bio=payload.bio;row.visibility=payload.visibility if payload.visibility in {"private","public"} else "private";row.show_contributions=payload.show_contributions;db.add(row);db.commit();return {"username":row.username,"visibility":row.visibility}
@router.post("/github/webhooks")
async def github_webhook(request:Request,x_github_event:str|None=Header(None),x_hub_signature_256:str|None=Header(None),x_github_delivery:str|None=Header(None),db:Session=Depends(get_db)):
    body=await request.body()
    if not settings.github_webhook_secret:raise HTTPException(503,"GitHub webhook integration is not configured")
    if not x_github_delivery or not x_hub_signature_256:raise HTTPException(401,"Webhook signature required")
    expected="sha256="+hmac.new(settings.github_webhook_secret.encode(),body,hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected,x_hub_signature_256):raise HTTPException(401,"Invalid webhook signature")
    if db.scalar(select(GithubWebhookEvent).where(GithubWebhookEvent.delivery_id==x_github_delivery)):return {"status":"duplicate_acknowledged"}
    row=GithubWebhookEvent(delivery_id=x_github_delivery,event_name=x_github_event or "unknown",payload_hash=hashlib.sha256(body).hexdigest(),status="received");db.add(row);db.commit();return {"status":"accepted"}
@router.get("/platform/developer-ecosystem/status")
def ecosystem_status(user:User=Depends(require_role("admin","platform_admin","super_admin"))):return {"github":github_status(),"webhooks":"configured" if settings.github_webhook_secret else "not_configured","sync":"not_configured"}
