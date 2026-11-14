from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, Header, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .auth import current_user, hash_token, new_token, now, password_hasher, require_csrf, require_role, verified_user
from .config import settings
from .db import get_db
from .models import (AuthSession, ComplianceControlDefinition, ComplianceEvidenceRecord,
    DataRetentionPolicy, OrganizationAccessReview, OrganizationAccessReviewItem,
    OrganizationIdentityProvider, OrganizationInvitation, OrganizationMembership,
    OrganizationSecurityAuditEvent, OrganizationSecurityPolicy, OrganizationSCIMMapping,
    OrganizationSCIMToken, OrganizationSSODomain, OrganizationTeam, OrganizationTeamMember,
    PrivacyDataRequest, SecurityAlertEvent, User)
from .organization_routes import check_role, org_context

router=APIRouter(prefix="/api/v1",tags=["enterprise security"])
MANAGERS={"owner","admin"}
class PolicyIn(BaseModel): require_sso:bool=False; require_mfa:bool=False; session_timeout_minutes:int=Field(default=10080,ge=15,le=43200); restrict_invitations:bool=False; allow_exports:bool=True; access_review_days:int=Field(default=90,ge=1,le=730)
class ProviderIn(BaseModel): provider_type:str=Field(pattern=r"^(oidc|saml)$"); display_name:str=Field(min_length=2,max_length=160); issuer:str=""; client_id:str=""; metadata_xml:str|None=None; certificate_pem:str|None=None
class ReviewIn(BaseModel): title:str=Field(min_length=2,max_length=180); due_at:datetime|None=None
class DecisionIn(BaseModel): decision:str=Field(pattern=r"^(approved|revoke|pending)$")
class PrivacyIn(BaseModel): request_type:str=Field(pattern=r"^(export|deletion)$")
class ScimTokenIn(BaseModel): label:str=Field(min_length=2,max_length=120)
class ScimUserIn(BaseModel): userName:str; displayName:str|None=None; active:bool=True

def provider_status():
    return {"oidc":{"enabled":settings.oidc_enabled and bool(settings.oidc_issuer and settings.oidc_client_id),"status":"configured" if settings.oidc_enabled and settings.oidc_issuer and settings.oidc_client_id else "Not Configured"},"saml":{"enabled":settings.saml_enabled and bool(settings.saml_entity_id and settings.saml_certificate),"status":"configured" if settings.saml_enabled and settings.saml_entity_id and settings.saml_certificate else "Not Configured"},"mfa":{"totp":"Not Configured","passkeys":"Not Configured" if not settings.webauthn_enabled else "Provider library required"},"scim":{"enabled":settings.scim_enabled,"status":"configured" if settings.scim_enabled else "Not Configured"}}
def security_event(db,org,user,action,outcome="success",resource="security"):
    db.add(OrganizationSecurityAuditEvent(organization_id=org.id if org else None,actor_id=user.id if user else None,action=action,resource_type=resource,outcome=outcome))
def active_membership(org_id,user_id,db):return db.scalar(select(OrganizationMembership).where(OrganizationMembership.organization_id==org_id,OrganizationMembership.user_id==user_id,OrganizationMembership.status=="active"))

@router.get("/organizations/{slug}/security")
def security_dashboard(ctx=Depends(org_context)):
    org,member,user,db=ctx; sessions=db.scalar(select(func.count()).select_from(AuthSession).where(AuthSession.user_id==user.id,AuthSession.revoked_at.is_(None),AuthSession.expires_at>now())) or 0;events=db.scalar(select(func.count()).select_from(OrganizationSecurityAuditEvent).where(OrganizationSecurityAuditEvent.organization_id==org.id)) or 0
    return {"organization":{"id":org.id,"slug":org.slug,"role":member.role},"providers":provider_status(),"active_sessions":sessions,"security_events":events,"access_reviews":db.scalar(select(func.count()).select_from(OrganizationAccessReview).where(OrganizationAccessReview.organization_id==org.id,OrganizationAccessReview.status=="open")) or 0}

@router.get("/organizations/{slug}/security/sso")
def sso_status(ctx=Depends(org_context)):
    org,_,_,db=ctx;providers=db.scalars(select(OrganizationIdentityProvider).where(OrganizationIdentityProvider.organization_id==org.id)).all();domains=db.scalars(select(OrganizationSSODomain).where(OrganizationSSODomain.organization_id==org.id)).all();return {"providers":[{"id":p.id,"type":p.provider_type,"display_name":p.display_name,"status":p.status,"issuer":p.issuer} for p in providers],"domains":[{"domain":d.domain,"verified":d.verified} for d in domains],"configuration":provider_status()}
@router.post("/organizations/{slug}/security/sso")
def stage_sso(payload:ProviderIn,ctx=Depends(org_context),_:None=Depends(require_csrf)):
    org,member,user,db=ctx;check_role(ctx,MANAGERS)
    if payload.provider_type=="oidc" and not provider_status()["oidc"]["enabled"]:raise HTTPException(503,"OIDC is Not Configured; no provider connection was attempted")
    if payload.provider_type=="saml" and not provider_status()["saml"]["enabled"]:raise HTTPException(503,"SAML is Not Configured; no provider connection was attempted")
    row=OrganizationIdentityProvider(organization_id=org.id,provider_type=payload.provider_type,display_name=payload.display_name,issuer=payload.issuer,client_id=payload.client_id,metadata_xml=payload.metadata_xml,certificate_pem=payload.certificate_pem,status="staged");db.add(row);security_event(db,org,user,"sso_provider_staged",resource="identity_provider");db.commit();return {"id":row.id,"status":"staged","message":"Provider staged; protocol validation is required before activation."}

@router.get("/settings/security/mfa")
def mfa_status(user:User=Depends(current_user),db:Session=Depends(get_db)):
    from .models import UserMFAMethod
    methods=db.scalars(select(UserMFAMethod).where(UserMFAMethod.user_id==user.id,UserMFAMethod.status=="active")).all();return {"configured":False,"status":"Not Configured","methods":[{"id":m.id,"type":m.method_type,"verified":bool(m.verified_at)} for m in methods],"message":"TOTP and passkey libraries/provider configuration are not installed or enabled."}
@router.post("/settings/security/mfa/enroll")
def enroll_mfa(user:User=Depends(verified_user),_:None=Depends(require_csrf)):
    raise HTTPException(503,"MFA enrollment is Not Configured; no secret was generated")
@router.get("/settings/security/sessions")
def sessions(user:User=Depends(current_user),db:Session=Depends(get_db)):
    rows=db.scalars(select(AuthSession).where(AuthSession.user_id==user.id).order_by(AuthSession.created_at.desc())).all();return [{"id":r.id,"created_at":r.created_at,"expires_at":r.expires_at,"revoked":bool(r.revoked_at),"current":False} for r in rows]
@router.post("/settings/security/sessions/{session_id}/revoke")
def revoke_session(session_id:UUID,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.scalar(select(AuthSession).where(AuthSession.id==session_id,AuthSession.user_id==user.id));
    if not row:raise HTTPException(404,"Session not found")
    row.revoked_at=now();db.commit();return {"status":"revoked"}

@router.get("/organizations/{slug}/security/policies")
def get_policy(ctx=Depends(org_context)):
    org,_,_,db=ctx;row=db.scalar(select(OrganizationSecurityPolicy).where(OrganizationSecurityPolicy.organization_id==org.id));return row or {"organization_id":org.id,"require_sso":False,"require_mfa":False,"session_timeout_minutes":10080,"restrict_invitations":False,"allow_exports":True,"access_review_days":90}
@router.put("/organizations/{slug}/security/policies")
def update_policy(payload:PolicyIn,ctx=Depends(org_context),_:None=Depends(require_csrf)):
    org,member,user,db=ctx;check_role(ctx,MANAGERS);row=db.scalar(select(OrganizationSecurityPolicy).where(OrganizationSecurityPolicy.organization_id==org.id)) or OrganizationSecurityPolicy(organization_id=org.id);[setattr(row,k,v) for k,v in payload.model_dump().items()];db.add(row);security_event(db,org,user,"security_policy_updated");db.commit();return row
@router.get("/organizations/{slug}/security/audit-logs")
def audit_logs(ctx=Depends(org_context),page:int=Query(1,ge=1),page_size:int=Query(50,ge=1,le=100)):
    org,member,user,db=ctx;check_role(ctx,MANAGERS);return db.scalars(select(OrganizationSecurityAuditEvent).where(OrganizationSecurityAuditEvent.organization_id==org.id).order_by(OrganizationSecurityAuditEvent.created_at.desc()).offset((page-1)*page_size).limit(page_size)).all()

@router.get("/organizations/{slug}/security/access-reviews")
def access_reviews(ctx=Depends(org_context)):
    org,_,_,db=ctx;return db.scalars(select(OrganizationAccessReview).where(OrganizationAccessReview.organization_id==org.id).order_by(OrganizationAccessReview.created_at.desc())).all()
@router.post("/organizations/{slug}/security/access-reviews",status_code=201)
def create_access_review(payload:ReviewIn,ctx=Depends(org_context),_:None=Depends(require_csrf)):
    org,member,user,db=ctx;check_role(ctx,MANAGERS);review=OrganizationAccessReview(organization_id=org.id,created_by=user.id,title=payload.title,due_at=payload.due_at);db.add(review);db.flush();members=db.scalars(select(OrganizationMembership).where(OrganizationMembership.organization_id==org.id,OrganizationMembership.status=="active")).all();db.add_all([OrganizationAccessReviewItem(review_id=review.id,membership_id=m.id) for m in members]);security_event(db,org,user,"access_review_created",resource="access_review");db.commit();return {"id":review.id,"items":len(members),"status":review.status}
@router.post("/organizations/{slug}/security/access-reviews/{review_id}/items/{item_id}")
def decide_review(review_id:UUID,item_id:UUID,payload:DecisionIn,ctx=Depends(org_context),_:None=Depends(require_csrf)):
    org,member,user,db=ctx;check_role(ctx,MANAGERS);review=db.scalar(select(OrganizationAccessReview).where(OrganizationAccessReview.id==review_id,OrganizationAccessReview.organization_id==org.id));item=db.scalar(select(OrganizationAccessReviewItem).where(OrganizationAccessReviewItem.id==item_id,OrganizationAccessReviewItem.review_id==review_id))
    if not review or not item:raise HTTPException(404,"Access review item not found")
    item.decision=payload.decision;item.decided_by=user.id;item.decided_at=now();db.commit();return {"status":item.decision}

@router.get("/organizations/{slug}/security/data-retention")
def retention(ctx=Depends(org_context)):
    org,_,_,db=ctx;return db.scalar(select(DataRetentionPolicy).where(DataRetentionPolicy.organization_id==org.id)) or {"organization_id":org.id,"audit_days":365,"session_days":90,"deleted_data_days":30,"legal_hold":False}
@router.put("/organizations/{slug}/security/data-retention")
def update_retention(payload:dict,ctx=Depends(org_context),_:None=Depends(require_csrf)):
    org,member,user,db=ctx;check_role(ctx,MANAGERS);row=db.scalar(select(DataRetentionPolicy).where(DataRetentionPolicy.organization_id==org.id)) or DataRetentionPolicy(organization_id=org.id);row.audit_days=max(1,min(int(payload.get("audit_days",365)),3650));row.session_days=max(1,min(int(payload.get("session_days",90)),3650));row.deleted_data_days=max(1,min(int(payload.get("deleted_data_days",30)),3650));row.legal_hold=bool(payload.get("legal_hold",False));db.add(row);security_event(db,org,user,"retention_policy_updated",resource="retention");db.commit();return row
@router.post("/privacy/requests",status_code=201)
def privacy_request(payload:PrivacyIn,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=PrivacyDataRequest(user_id=user.id,request_type=payload.request_type);db.add(row);db.commit();return {"id":row.id,"status":row.status}
@router.get("/privacy/requests")
def privacy_requests(user:User=Depends(current_user),db:Session=Depends(get_db)):return db.scalars(select(PrivacyDataRequest).where(PrivacyDataRequest.user_id==user.id).order_by(PrivacyDataRequest.created_at.desc())).all()

@router.get("/platform/compliance")
def compliance(user:User=Depends(require_role("admin","platform_admin","super_admin")),db:Session=Depends(get_db)):
    return {"certification":"Not claimed","controls":db.scalars(select(ComplianceControlDefinition).order_by(ComplianceControlDefinition.framework,ComplianceControlDefinition.control_key)).all(),"evidence_count":db.scalar(select(func.count()).select_from(ComplianceEvidenceRecord)) or 0}
@router.post("/platform/compliance/controls",status_code=201)
def add_control(payload:dict,user:User=Depends(require_role("admin","platform_admin","super_admin")),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=ComplianceControlDefinition(framework=str(payload.get("framework","internal"))[:60],control_key=str(payload.get("control_key","control"))[:80],title=str(payload.get("title","Control"))[:240],description=str(payload.get("description","")));db.add(row);db.commit();return {"id":row.id,"status":row.status}

def scim_context(organization_id:UUID,authorization:str|None=Header(None),db:Session=Depends(get_db)):
    if not settings.scim_enabled:raise HTTPException(503,"SCIM is Not Configured")
    if not authorization or not authorization.lower().startswith("bearer "):raise HTTPException(401,"SCIM bearer token required")
    row=db.scalar(select(OrganizationSCIMToken).where(OrganizationSCIMToken.organization_id==organization_id,OrganizationSCIMToken.token_hash==hash_token(authorization[7:].strip()),OrganizationSCIMToken.revoked_at.is_(None)))
    if not row or (row.expires_at and row.expires_at<=now()):raise HTTPException(401,"Invalid SCIM credentials")
    row.last_used_at=now();return organization_id,db
@router.post("/organizations/{slug}/security/scim/tokens",status_code=201)
def create_scim_token(payload:ScimTokenIn,ctx=Depends(org_context),_:None=Depends(require_csrf)):
    org,member,user,db=ctx;check_role(ctx,MANAGERS);raw=new_token();row=OrganizationSCIMToken(organization_id=org.id,token_hash=hash_token(raw),label=payload.label);db.add(row);security_event(db,org,user,"scim_token_created",resource="scim_token");db.commit();return {"id":row.id,"token":raw,"warning":"Store this token now; it will not be shown again."}
@router.get("/scim/v2/organizations/{organization_id}/Users")
def scim_users(organization_id:UUID,ctx=Depends(scim_context)):
    org_id,db=ctx;rows=db.execute(select(OrganizationSCIMMapping,User).join(User,User.id==OrganizationSCIMMapping.user_id).where(OrganizationSCIMMapping.organization_id==org_id,OrganizationSCIMMapping.active.is_(True))).all();return {"schemas":["urn:ietf:params:scim:api:messages:2.0:ListResponse"],"totalResults":len(rows),"Resources":[{"id":str(m.external_id),"userName":u.email,"displayName":u.display_name,"active":m.active} for m,u in rows]}
@router.post("/scim/v2/organizations/{organization_id}/Users",status_code=201)
def scim_create(organization_id:UUID,payload:ScimUserIn,ctx=Depends(scim_context)):
    org_id,db=ctx;email=payload.userName.strip().lower();existing=db.scalar(select(User).where(User.email_normalized==email))
    if existing:raise HTTPException(409,"SCIM will not merge an existing global account without explicit linking")
    user=User(email=email,email_normalized=email,password_hash=password_hasher.hash(new_token()),display_name=payload.displayName or email,role="student",account_status="active");db.add(user);db.flush();mapping=OrganizationSCIMMapping(organization_id=org_id,external_id=str(user.id),user_id=user.id,active=payload.active);db.add(mapping);db.commit();return {"id":str(mapping.external_id),"userName":user.email,"active":mapping.active}
@router.patch("/scim/v2/organizations/{organization_id}/Users/{external_id}")
def scim_patch(organization_id:UUID,external_id:str,payload:dict,ctx=Depends(scim_context)):
    org_id,db=ctx;mapping=db.scalar(select(OrganizationSCIMMapping).where(OrganizationSCIMMapping.organization_id==org_id,OrganizationSCIMMapping.external_id==external_id));
    if not mapping:raise HTTPException(404,"SCIM user not found")
    if "active" in payload:mapping.active=bool(payload["active"])
    db.commit();return {"id":mapping.external_id,"active":mapping.active}
@router.get("/scim/v2/organizations/{organization_id}/Groups")
def scim_groups(organization_id:UUID,ctx=Depends(scim_context)):
    org_id,db=ctx;rows=db.scalars(select(OrganizationTeam).where(OrganizationTeam.organization_id==org_id,OrganizationTeam.status=="active")).all();return {"totalResults":len(rows),"Resources":[{"id":str(t.id),"displayName":t.name} for t in rows]}
