from datetime import datetime, timedelta
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .auth import current_user, hash_token, new_token, normalize_email, require_csrf, require_role, verified_user, now
from .db import get_db
from .mailer import mailer
from .models import (Course, Enrollment, LessonProgress, Organization, OrganizationAssessment,
    OrganizationAssessmentAttempt, OrganizationAuditLog, OrganizationCourse,
    OrganizationInvitation, OrganizationMembership, OrganizationReportExport,
    OrganizationSecurityEvent, OrganizationSetting, OrganizationSkillSnapshot,
    OrganizationTeam, OrganizationTeamMember, OrganizationTrainingAssignment,
    OrganizationTrainingItem, OrganizationTrainingProgram, User)

router=APIRouter(prefix="/api/v1",tags=["organizations"])
ORG_ROLES={"owner","admin","instructor","team_manager","learner","viewer"}
MANAGERS={"owner","admin"}; TRAINING_MANAGERS={"owner","admin","instructor","team_manager"}
class OrganizationIn(BaseModel): name:str=Field(min_length=2,max_length=180); slug:str=Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",max_length=180); description:str=Field(default="",max_length=5000)
class MemberIn(BaseModel): user_id:UUID; role:str="learner"
class InvitationIn(BaseModel): email:str; role:str="learner"
class TeamIn(BaseModel): name:str=Field(min_length=2,max_length=160); slug:str=Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",max_length=160); manager_id:UUID|None=None
class ProgramIn(BaseModel): name:str=Field(min_length=2,max_length=180); slug:str=Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$",max_length=180); description:str=""; status:str="draft"
class ItemIn(BaseModel): course_id:UUID|None=None; lesson_id:UUID|None=None; position:int=Field(ge=0); required:bool=True; due_days:int|None=Field(default=None,ge=0)
class AssignmentIn(BaseModel): user_id:UUID|None=None; team_id:UUID|None=None; due_at:datetime|None=None
class AssessmentIn(BaseModel): title:str=Field(min_length=2,max_length=180); assessment_type:str=Field(pattern=r"^(multiple_choice|coding|sql|project|skill)$"); attempt_limit:int=Field(default=1,ge=1,le=20); time_limit_minutes:int|None=Field(default=None,ge=1)
class SettingsIn(BaseModel): timezone:str=Field(default="UTC",max_length=80); default_language:str=Field(default="en",pattern=r"^(en|mm)$"); branding_json:str="{}"; policy_json:str="{}"
class SupportIn(BaseModel): reason:str=Field(min_length=10,max_length=2000); scope_json:str="{}"; expires_at:datetime

def org_context(slug:str,user:User=Depends(current_user),db:Session=Depends(get_db)):
    org=db.scalar(select(Organization).where(Organization.slug==slug,Organization.status=="active"))
    membership=db.scalar(select(OrganizationMembership).where(OrganizationMembership.organization_id==org.id if org else None,OrganizationMembership.user_id==user.id,OrganizationMembership.status=="active")) if org else None
    if not org or not membership: raise HTTPException(403,"Active organization membership required")
    return org,membership,user,db
def check_role(ctx,roles):
    if ctx[1].role not in roles: raise HTTPException(403,"Organization permission required")
def audit(db,org,user,action,entity,entity_id=None): db.add(OrganizationAuditLog(organization_id=org.id,actor_id=user.id,action=action,entity_type=entity,entity_id=entity_id))
def safe_csv(value:str)->str: return "'"+value if value[:1] in {"=","+","-","@"} else value

@router.get("/organizations")
def organizations(user:User=Depends(current_user),db:Session=Depends(get_db)):
    rows=db.execute(select(Organization,OrganizationMembership.role).join(OrganizationMembership,OrganizationMembership.organization_id==Organization.id).where(OrganizationMembership.user_id==user.id,OrganizationMembership.status=="active",Organization.status=="active")).all()
    return [{"id":o.id,"name":o.name,"slug":o.slug,"description":o.description,"role":role,"status":o.status} for o,role in rows]

@router.post("/organizations",status_code=201)
def create_organization(payload:OrganizationIn,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    if db.scalar(select(Organization).where(Organization.slug==payload.slug)): raise HTTPException(409,"Organization slug is already in use")
    org=Organization(name=payload.name.strip(),slug=payload.slug,description=payload.description,owner_id=user.id);db.add(org);db.flush();db.add(OrganizationMembership(organization_id=org.id,user_id=user.id,role="owner"));db.add(OrganizationSetting(organization_id=org.id));audit(db,org,user,"organization_created","organization",org.id);db.commit();return {"id":org.id,"slug":org.slug,"role":"owner"}

@router.get("/organizations/{slug}/dashboard")
def dashboard(ctx=Depends(org_context)):
    org,member,user,db=ctx; members=db.scalar(select(func.count()).select_from(OrganizationMembership).where(OrganizationMembership.organization_id==org.id,OrganizationMembership.status=="active")) or 0; programs=db.scalar(select(func.count()).select_from(OrganizationTrainingProgram).where(OrganizationTrainingProgram.organization_id==org.id,OrganizationTrainingProgram.status.in_(["published","assigned","in_progress"]))) or 0; assignments=db.scalar(select(func.count()).select_from(OrganizationTrainingAssignment).where(OrganizationTrainingAssignment.organization_id==org.id)) or 0
    return {"organization":{"id":org.id,"name":org.name,"slug":org.slug,"role":member.role},"metrics":{"active_members":members,"active_programs":programs,"assignments":assignments},"privacy_note":"Metrics are tenant-scoped."}

@router.get("/organizations/{slug}/members")
def members(ctx=Depends(org_context),search:str|None=None,page:int=Query(1,ge=1),page_size:int=Query(25,ge=1,le=100)):
    org,_,_,db=ctx;q=select(OrganizationMembership,User).join(User,User.id==OrganizationMembership.user_id).where(OrganizationMembership.organization_id==org.id,OrganizationMembership.status=="active")
    if search:q=q.where(User.display_name.ilike(f"%{search}%"))
    rows=db.execute(q.order_by(User.display_name).offset((page-1)*page_size).limit(page_size)).all();return {"items":[{"id":m.id,"user_id":u.id,"name":u.display_name,"email":u.email,"role":m.role,"status":m.status} for m,u in rows],"page":page,"page_size":page_size}

@router.post("/organizations/{slug}/members")
def add_member(payload:MemberIn,ctx=Depends(org_context),_:None=Depends(require_csrf)):
    org,member,user,db=ctx;check_role(ctx,MANAGERS)
    if payload.role not in ORG_ROLES or payload.role=="owner":raise HTTPException(422,"Invalid organization role")
    target=db.get(User,payload.user_id)
    if not target:raise HTTPException(404,"User not found")
    if db.scalar(select(OrganizationMembership).where(OrganizationMembership.organization_id==org.id,OrganizationMembership.user_id==target.id)):raise HTTPException(409,"User is already a member")
    row=OrganizationMembership(organization_id=org.id,user_id=target.id,role=payload.role);db.add(row);audit(db,org,user,"member_added","membership",row.id);db.commit();return {"id":row.id,"role":row.role}

@router.patch("/organizations/{slug}/members/{user_id}")
def change_member(user_id:UUID,payload:MemberIn,ctx=Depends(org_context),_:None=Depends(require_csrf)):
    org,member,user,db=ctx;check_role(ctx,{"owner"})
    row=db.scalar(select(OrganizationMembership).where(OrganizationMembership.organization_id==org.id,OrganizationMembership.user_id==user_id,OrganizationMembership.status=="active"))
    if not row or payload.role not in ORG_ROLES:raise HTTPException(404,"Membership not found")
    if row.role=="owner" and payload.role!="owner" and (db.scalar(select(func.count()).select_from(OrganizationMembership).where(OrganizationMembership.organization_id==org.id,OrganizationMembership.role=="owner",OrganizationMembership.status=="active")) or 0)<=1:raise HTTPException(409,"Transfer ownership before removing the final owner")
    row.role=payload.role;audit(db,org,user,"member_role_changed","membership",row.id);db.commit();return {"status":"updated","role":row.role}

@router.delete("/organizations/{slug}/members/{user_id}")
def remove_member(user_id:UUID,ctx=Depends(org_context),_:None=Depends(require_csrf)):
    org,member,user,db=ctx;check_role(ctx,MANAGERS);row=db.scalar(select(OrganizationMembership).where(OrganizationMembership.organization_id==org.id,OrganizationMembership.user_id==user_id,OrganizationMembership.status=="active"))
    if not row:raise HTTPException(404,"Membership not found")
    if row.role=="owner" and (db.scalar(select(func.count()).select_from(OrganizationMembership).where(OrganizationMembership.organization_id==org.id,OrganizationMembership.role=="owner",OrganizationMembership.status=="active")) or 0)<=1:raise HTTPException(409,"The final organization owner cannot be removed")
    row.status="removed";audit(db,org,user,"member_removed","membership",row.id);db.commit();return {"status":"removed"}

@router.post("/organizations/{slug}/invitations",status_code=201)
def invite(payload:InvitationIn,ctx=Depends(org_context),_:None=Depends(require_csrf)):
    org,member,user,db=ctx;check_role(ctx,MANAGERS);email=normalize_email(payload.email)
    if payload.role not in ORG_ROLES or payload.role=="owner":raise HTTPException(422,"Invalid invitation role")
    if db.scalar(select(OrganizationMembership).join(User,User.id==OrganizationMembership.user_id).where(OrganizationMembership.organization_id==org.id,User.email_normalized==email,OrganizationMembership.status=="active")):raise HTTPException(409,"User is already a member")
    if db.scalar(select(OrganizationInvitation).where(OrganizationInvitation.organization_id==org.id,OrganizationInvitation.email==email,OrganizationInvitation.status=="pending",OrganizationInvitation.expires_at>now())):raise HTTPException(409,"Invitation already pending")
    raw=new_token();row=OrganizationInvitation(organization_id=org.id,email=email,role=payload.role,token_hash=hash_token(raw),expires_at=now()+timedelta(days=3));db.add(row);audit(db,org,user,"invitation_created","invitation",row.id);db.commit();mailer.send(email,"CodeMaster organization invitation",f"Accept this invitation with token {raw}");return {"id":row.id,"status":"pending","delivery":"mailer"}

@router.post("/organizations/invitations/accept")
def accept_invitation(token:str,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.scalar(select(OrganizationInvitation).where(OrganizationInvitation.token_hash==hash_token(token),OrganizationInvitation.status=="pending",OrganizationInvitation.expires_at>now(),OrganizationInvitation.email==user.email_normalized))
    if not row:raise HTTPException(400,"Invitation is invalid, expired, or not addressed to this account")
    if db.scalar(select(OrganizationMembership).where(OrganizationMembership.organization_id==row.organization_id,OrganizationMembership.user_id==user.id)):raise HTTPException(409,"Membership already exists")
    db.add(OrganizationMembership(organization_id=row.organization_id,user_id=user.id,role=row.role));row.status="accepted";row.accepted_at=now();db.commit();return {"status":"accepted","organization_id":row.organization_id}

@router.get("/organizations/{slug}/teams")
def teams(ctx=Depends(org_context)):
    org,_,_,db=ctx;rows=db.scalars(select(OrganizationTeam).where(OrganizationTeam.organization_id==org.id,OrganizationTeam.status=="active").order_by(OrganizationTeam.name)).all();return rows
@router.post("/organizations/{slug}/teams",status_code=201)
def create_team(payload:TeamIn,ctx=Depends(org_context),_:None=Depends(require_csrf)):
    org,member,user,db=ctx;check_role(ctx,MANAGERS|{"team_manager"})
    if db.scalar(select(OrganizationTeam).where(OrganizationTeam.organization_id==org.id,OrganizationTeam.slug==payload.slug)):raise HTTPException(409,"Team slug is already in use")
    if payload.manager_id and not db.scalar(select(OrganizationMembership).where(OrganizationMembership.organization_id==org.id,OrganizationMembership.user_id==payload.manager_id,OrganizationMembership.status=="active")):raise HTTPException(400,"Team manager must be an organization member")
    row=OrganizationTeam(organization_id=org.id,name=payload.name,slug=payload.slug,manager_id=payload.manager_id or user.id);db.add(row);db.flush();db.add(OrganizationTeamMember(team_id=row.id,user_id=payload.manager_id or user.id));db.commit();return {"id":row.id,"slug":row.slug}

@router.get("/organizations/{slug}/courses")
def org_courses(ctx=Depends(org_context)):
    org,_,_,db=ctx;rows=db.execute(select(OrganizationCourse,Course).join(Course,Course.id==OrganizationCourse.course_id).where(OrganizationCourse.organization_id==org.id,OrganizationCourse.status=="active")).all();return [{"id":link.id,"course_id":course.id,"title":course.title,"slug":course.slug,"visibility":link.visibility} for link,course in rows]
@router.post("/organizations/{slug}/courses",status_code=201)
def add_course(course_id:UUID,ctx=Depends(org_context),_:None=Depends(require_csrf)):
    org,member,user,db=ctx;check_role(ctx,MANAGERS|{"instructor"});course=db.get(Course,course_id)
    if not course:raise HTTPException(404,"Course not found")
    if db.scalar(select(OrganizationCourse).where(OrganizationCourse.organization_id==org.id,OrganizationCourse.course_id==course.id)):raise HTTPException(409,"Course is already assigned")
    row=OrganizationCourse(organization_id=org.id,course_id=course.id,visibility="private");db.add(row);audit(db,org,user,"course_added","course",course.id);db.commit();return {"id":row.id,"status":"active"}

@router.get("/organizations/{slug}/training")
def training(ctx=Depends(org_context)):
    org,_,_,db=ctx;return db.scalars(select(OrganizationTrainingProgram).where(OrganizationTrainingProgram.organization_id==org.id).order_by(OrganizationTrainingProgram.created_at.desc())).all()
@router.post("/organizations/{slug}/training",status_code=201)
def create_training(payload:ProgramIn,ctx=Depends(org_context),_:None=Depends(require_csrf)):
    org,member,user,db=ctx;check_role(ctx,TRAINING_MANAGERS)
    if db.scalar(select(OrganizationTrainingProgram).where(OrganizationTrainingProgram.organization_id==org.id,OrganizationTrainingProgram.slug==payload.slug)):raise HTTPException(409,"Training slug is already in use")
    if payload.status not in {"draft","published","archived"}:raise HTTPException(422,"Invalid training status")
    row=OrganizationTrainingProgram(organization_id=org.id,created_by=user.id,name=payload.name,slug=payload.slug,description=payload.description,status=payload.status);db.add(row);audit(db,org,user,"training_created","training",row.id);db.commit();return {"id":row.id,"status":row.status}
@router.post("/organizations/{slug}/training/{program_id}/items",status_code=201)
def add_training_item(program_id:UUID,payload:ItemIn,ctx=Depends(org_context),_:None=Depends(require_csrf)):
    org,member,user,db=ctx;check_role(ctx,TRAINING_MANAGERS);program=db.scalar(select(OrganizationTrainingProgram).where(OrganizationTrainingProgram.id==program_id,OrganizationTrainingProgram.organization_id==org.id))
    if not program or (payload.course_id is None and payload.lesson_id is None):raise HTTPException(400,"A course or lesson is required")
    row=OrganizationTrainingItem(program_id=program.id,**payload.model_dump());db.add(row);db.commit();return {"id":row.id,"position":row.position}
@router.post("/organizations/{slug}/training/{program_id}/assignments",status_code=201)
def assign_training(program_id:UUID,payload:AssignmentIn,ctx=Depends(org_context),_:None=Depends(require_csrf)):
    org,member,user,db=ctx;check_role(ctx,TRAINING_MANAGERS);program=db.scalar(select(OrganizationTrainingProgram).where(OrganizationTrainingProgram.id==program_id,OrganizationTrainingProgram.organization_id==org.id))
    if not program or (payload.user_id is None)==(payload.team_id is None):raise HTTPException(400,"Assign exactly one learner or team")
    if payload.user_id and not db.scalar(select(OrganizationMembership).where(OrganizationMembership.organization_id==org.id,OrganizationMembership.user_id==payload.user_id,OrganizationMembership.status=="active")):raise HTTPException(400,"Learner must be an active organization member")
    if payload.team_id and not db.scalar(select(OrganizationTeam).where(OrganizationTeam.id==payload.team_id,OrganizationTeam.organization_id==org.id,OrganizationTeam.status=="active")):raise HTTPException(400,"Team must belong to this organization")
    target=str(payload.user_id or payload.team_id);key=f"{program.id}:{target}"
    if db.scalar(select(OrganizationTrainingAssignment).where(OrganizationTrainingAssignment.assignment_key==key)):raise HTTPException(409,"Training is already assigned")
    row=OrganizationTrainingAssignment(organization_id=org.id,program_id=program.id,user_id=payload.user_id,team_id=payload.team_id,assignment_key=key,due_at=payload.due_at);db.add(row);db.commit();return {"id":row.id,"status":row.status}

@router.get("/organizations/{slug}/assessments")
def assessments(ctx=Depends(org_context)):
    org,_,_,db=ctx;return db.scalars(select(OrganizationAssessment).where(OrganizationAssessment.organization_id==org.id).order_by(OrganizationAssessment.created_at.desc())).all()
@router.post("/organizations/{slug}/assessments",status_code=201)
def create_assessment(payload:AssessmentIn,ctx=Depends(org_context),_:None=Depends(require_csrf)):
    org,member,user,db=ctx;check_role(ctx,TRAINING_MANAGERS);row=OrganizationAssessment(organization_id=org.id,created_by=user.id,title=payload.title,assessment_type=payload.assessment_type,attempt_limit=payload.attempt_limit,time_limit_minutes=payload.time_limit_minutes);db.add(row);db.commit();return {"id":row.id,"status":row.status}
@router.post("/organizations/{slug}/assessments/{assessment_id}/attempts",status_code=201)
def attempt_assessment(assessment_id:UUID,ctx=Depends(org_context),_:None=Depends(require_csrf)):
    org,member,user,db=ctx;assessment=db.scalar(select(OrganizationAssessment).where(OrganizationAssessment.id==assessment_id,OrganizationAssessment.organization_id==org.id,OrganizationAssessment.status=="published"))
    if not assessment:raise HTTPException(404,"Published assessment not found")
    count=db.scalar(select(func.count()).select_from(OrganizationAssessmentAttempt).where(OrganizationAssessmentAttempt.assessment_id==assessment.id,OrganizationAssessmentAttempt.user_id==user.id)) or 0
    if count>=assessment.attempt_limit:raise HTTPException(409,"Assessment attempt limit reached")
    row=OrganizationAssessmentAttempt(assessment_id=assessment.id,organization_id=org.id,user_id=user.id,attempt_number=count+1,status="submitted",verified=False);db.add(row);db.commit();return {"id":row.id,"status":"submitted","verified":False}

@router.get("/organizations/{slug}/courses/{course_id}")
def private_course(course_id:UUID,ctx=Depends(org_context)):
    org,_,_,db=ctx;row=db.execute(select(OrganizationCourse,Course).join(Course,Course.id==OrganizationCourse.course_id).where(OrganizationCourse.organization_id==org.id,OrganizationCourse.course_id==course_id,OrganizationCourse.status=="active")).first()
    if not row:raise HTTPException(404,"Organization course not found")
    link,course=row;return {"id":course.id,"title":course.title,"slug":course.slug,"description":course.description,"visibility":link.visibility,"published":course.published}

@router.get("/organizations/{slug}/analytics")
def analytics(ctx=Depends(org_context)):
    org,_,_,db=ctx;members=db.scalar(select(func.count()).select_from(OrganizationMembership).where(OrganizationMembership.organization_id==org.id,OrganizationMembership.status=="active")) or 0
    if members<5:return {"suppressed":True,"reason":"Metrics are hidden for organizations with fewer than 5 active members.","members":members}
    assignments=db.scalar(select(func.count()).select_from(OrganizationTrainingAssignment).where(OrganizationTrainingAssignment.organization_id==org.id)) or 0;completed=db.scalar(select(func.count()).select_from(OrganizationTrainingAssignment).where(OrganizationTrainingAssignment.organization_id==org.id,OrganizationTrainingAssignment.status=="completed")) or 0
    return {"suppressed":False,"members":members,"assignments":assignments,"completed_assignments":completed,"completion_rate":round(completed/assignments*100,2) if assignments else 0}

@router.get("/organizations/{slug}/settings")
def settings_view(ctx=Depends(org_context)):
    org,_,_,db=ctx;return db.scalar(select(OrganizationSetting).where(OrganizationSetting.organization_id==org.id))
@router.put("/organizations/{slug}/settings")
def update_settings(payload:SettingsIn,ctx=Depends(org_context),_:None=Depends(require_csrf)):
    org,member,user,db=ctx;check_role(ctx,MANAGERS);row=db.scalar(select(OrganizationSetting).where(OrganizationSetting.organization_id==org.id));row.timezone=payload.timezone;row.default_language=payload.default_language;row.branding_json=payload.branding_json;row.policy_json=payload.policy_json;audit(db,org,user,"settings_updated","settings",row.id);db.commit();return row

@router.post("/organizations/{slug}/reports/export",status_code=202)
def export_report(report_type:str=Query(...,pattern=r"^[a-z0-9_-]{2,60}$"),ctx=Depends(org_context),_:None=Depends(require_csrf)):
    org,member,user,db=ctx;check_role(ctx,MANAGERS);row=OrganizationReportExport(organization_id=org.id,requested_by=user.id,report_type=safe_csv(report_type),status="queued");db.add(row);audit(db,org,user,"report_export_requested","report",row.id);db.commit();return {"id":row.id,"status":"queued","message":"Export is queued for tenant-scoped processing."}

@router.get("/platform/organizations")
def platform_organizations(user:User=Depends(require_role("admin","platform_admin","super_admin")),db:Session=Depends(get_db)):
    rows=db.execute(select(Organization,func.count(OrganizationMembership.id)).outerjoin(OrganizationMembership,OrganizationMembership.organization_id==Organization.id).group_by(Organization.id).order_by(Organization.created_at.desc())).all();return [{"id":o.id,"name":o.name,"slug":o.slug,"status":o.status,"owner_id":o.owner_id,"member_count":count} for o,count in rows]
@router.patch("/platform/organizations/{organization_id}/status")
def platform_status(organization_id:UUID,status_value:str=Query(...,pattern=r"^(active|suspended)$"),user:User=Depends(require_role("admin","platform_admin","super_admin")),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    org=db.get(Organization,organization_id)
    if not org:raise HTTPException(404,"Organization not found")
    org.status=status_value;db.add(OrganizationSecurityEvent(organization_id=org.id,actor_id=user.id,event_type="organization_status_changed",severity="warning" if status_value=="suspended" else "info"));db.commit();return {"status":org.status}
@router.post("/platform/organizations/{organization_id}/support-access",status_code=201)
def support_access(organization_id:UUID,payload:SupportIn,user:User=Depends(require_role("admin","platform_admin","super_admin")),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    org=db.get(Organization,organization_id)
    if not org:raise HTTPException(404,"Organization not found")
    row=OrganizationSupportAccess(organization_id=org.id,requested_by=user.id,approved_by=user.id,reason=payload.reason,scope_json=payload.scope_json,expires_at=payload.expires_at,status="active");db.add(row);db.commit();return {"id":row.id,"status":row.status,"scope":payload.scope_json}
