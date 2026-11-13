import hashlib, json, secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .auth import current_user, hash_token, new_token, require_csrf, require_role, verified_user
from .db import get_db
from .models import (CodingCompetition, CompetitionParticipant, CompetitionRanking, DeveloperTeam,
    DeveloperTeamInvitation, DeveloperTeamMember, HackathonEvent, HackathonRegistration,
    HackathonSubmission, HackathonTeam, TeamActivityEvent, TeamProject, TeamProjectTask, User)

router=APIRouter(prefix="/api/v1",tags=["collaboration"])
ADMIN={"admin","super_admin"}
class TeamIn(BaseModel): name:str=Field(min_length=2,max_length=160); description:str=Field(default="",max_length=10000); visibility:str="private"
class InviteIn(BaseModel): email:str|None=None; user_id:UUID|None=None
class RoleIn(BaseModel): role:str=Field(pattern="^(owner|admin|member|viewer)$")
class ProjectIn(BaseModel): title:str=Field(min_length=1,max_length=180); description:str=Field(default="",max_length=10000); repository_url:str|None=None
class TaskIn(BaseModel): title:str=Field(min_length=1,max_length=180); description:str=""; priority:str="normal"; status:str="todo"; assigned_to:UUID|None=None
class HackathonIn(BaseModel): title:str=Field(min_length=3,max_length=180); slug:str=Field(pattern=r"^[a-z0-9-]+$"); description:str=""; rules:str=""; registration_starts_at:datetime; registration_ends_at:datetime; starts_at:datetime; ends_at:datetime; max_team_size:int=Field(default=4,ge=1,le=20); status:str="draft"
class SubmissionIn(BaseModel): title:str=Field(min_length=1,max_length=180); description:str=""; github_url:str|None=None; demo_url:str|None=None; team_id:UUID|None=None
def now():return datetime.now(timezone.utc)
def member(db,team_id,user_id):return db.scalar(select(DeveloperTeamMember).where(DeveloperTeamMember.team_id==team_id,DeveloperTeamMember.user_id==user_id))
def can_manage(row):return row and row.role in {"owner","admin"}
def team_or_404(db,team_id):
    row=db.get(DeveloperTeam,team_id)
    if not row or row.status!="active":raise HTTPException(404,"Team not found")
    return row
def slugify(name):return "-".join("".join(c.lower() if c.isalnum() else " " for c in name).split())

@router.get("/teams")
def teams(user:User=Depends(current_user),db:Session=Depends(get_db)):
    ids=select(DeveloperTeamMember.team_id).where(DeveloperTeamMember.user_id==user.id);return db.scalars(select(DeveloperTeam).where(DeveloperTeam.status=="active",DeveloperTeam.id.in_(ids)).order_by(DeveloperTeam.name)).all()
@router.post("/teams",status_code=201)
def create_team(payload:TeamIn,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    slug=slugify(payload.name); existing=db.scalar(select(DeveloperTeam).where(DeveloperTeam.slug==slug));
    if existing:slug=f"{slug}-{str(user.id)[:8]}"
    row=DeveloperTeam(owner_id=user.id,name=payload.name,slug=slug,description=payload.description,visibility=payload.visibility if payload.visibility in {"private","public"} else "private");db.add(row);db.flush();db.add(DeveloperTeamMember(team_id=row.id,user_id=user.id,role="owner"));db.add(TeamActivityEvent(team_id=row.id,actor_id=user.id,event_type="team_created"));db.commit();return {"id":row.id,"slug":row.slug,"name":row.name}
@router.get("/teams/invitations")
def invitations(user:User=Depends(current_user),db:Session=Depends(get_db)):
    return db.scalars(select(DeveloperTeamInvitation).where(DeveloperTeamInvitation.invited_user_id==user.id,DeveloperTeamInvitation.status=="pending",DeveloperTeamInvitation.expires_at>now())).all()
@router.post("/teams/invitations/{invitation_id}/accept")
def accept_invitation(invitation_id:UUID,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    inv=db.scalar(select(DeveloperTeamInvitation).where(DeveloperTeamInvitation.id==invitation_id,DeveloperTeamInvitation.invited_user_id==user.id,DeveloperTeamInvitation.status=="pending",DeveloperTeamInvitation.expires_at>now()))
    if not inv:raise HTTPException(404,"Invitation not found or expired")
    if not member(db,inv.team_id,user.id):db.add(DeveloperTeamMember(team_id=inv.team_id,user_id=user.id,role="member"))
    inv.status="accepted";db.add(TeamActivityEvent(team_id=inv.team_id,actor_id=user.id,event_type="invitation_accepted"));db.commit();return {"status":"accepted"}
@router.get("/teams/{team_id}")
def team_detail(team_id:UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):
    team=team_or_404(db,team_id); me=member(db,team_id,user.id)
    if not me and team.visibility!="public":raise HTTPException(403,"Team membership required")
    members=db.scalars(select(DeveloperTeamMember).where(DeveloperTeamMember.team_id==team.id)).all();projects=db.scalars(select(TeamProject).where(TeamProject.team_id==team.id)).all()
    return {"id":team.id,"name":team.name,"slug":team.slug,"description":team.description,"visibility":team.visibility,"role":me.role if me else None,"members":members,"projects":projects}
@router.post("/teams/{team_id}/invite")
def invite(team_id:UUID,payload:InviteIn,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    team=team_or_404(db,team_id); me=member(db,team_id,user.id)
    if not can_manage(me):raise HTTPException(403,"Team admin permission required")
    invited=db.get(User,payload.user_id) if payload.user_id else (db.scalar(select(User).where(User.email_normalized==payload.email.strip().lower())) if payload.email else None)
    if not invited or member(db,team_id,invited.id):raise HTTPException(400,"Supported user identity is required and must not already be a member")
    if db.scalar(select(DeveloperTeamInvitation).where(DeveloperTeamInvitation.team_id==team_id,DeveloperTeamInvitation.invited_user_id==invited.id,DeveloperTeamInvitation.status=="pending")):raise HTTPException(409,"Invitation already pending")
    raw=new_token();row=DeveloperTeamInvitation(team_id=team_id,invited_user_id=invited.id,token_hash=hash_token(raw),expires_at=now()+timedelta(days=3));db.add(row);db.commit();return {"id":row.id,"status":"pending","delivery":"notification service required"}
@router.patch("/teams/{team_id}/members/{user_id}")
def change_role(team_id:UUID,user_id:UUID,payload:RoleIn,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    actor=member(db,team_id,user.id); target=member(db,team_id,user_id);team=team_or_404(db,team_id)
    if not actor or actor.role!="owner" or not target:raise HTTPException(403,"Team owner permission required")
    if target.role=="owner" and payload.role!="owner" and db.scalar(select(func.count()).where(DeveloperTeamMember.team_id==team_id,DeveloperTeamMember.role=="owner"))<=1:raise HTTPException(409,"Transfer ownership before removing the final owner")
    target.role=payload.role
    if payload.role=="owner":team.owner_id=user_id;actor.role="admin"
    db.commit();return {"status":"updated","role":target.role}
@router.delete("/teams/{team_id}/members/{user_id}")
def remove_member(team_id:UUID,user_id:UUID,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    actor=member(db,team_id,user.id);target=member(db,team_id,user_id)
    if not actor or not can_manage(actor) or not target:raise HTTPException(403,"Team admin permission required")
    if target.role=="owner" and db.scalar(select(func.count()).where(DeveloperTeamMember.team_id==team_id,DeveloperTeamMember.role=="owner"))<=1:raise HTTPException(409,"Transfer ownership before removing the final owner")
    db.delete(target);db.commit();return {"status":"removed"}
@router.post("/teams/{team_id}/projects",status_code=201)
def project(team_id:UUID,payload:ProjectIn,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    team_or_404(db,team_id);m=member(db,team_id,user.id)
    if not can_manage(m):raise HTTPException(403,"Team admin permission required")
    row=TeamProject(team_id=team_id,created_by=user.id,title=payload.title,description=payload.description,repository_url=payload.repository_url);db.add(row);db.commit();return {"id":row.id,"status":row.status}
@router.post("/teams/projects/{project_id}/tasks",status_code=201)
def task(project_id:UUID,payload:TaskIn,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    project=db.get(TeamProject,project_id);m=member(db,project.team_id,user.id) if project else None
    if not project or not m or not can_manage(m):raise HTTPException(403,"Team project permission required")
    row=TeamProjectTask(project_id=project.id,**payload.model_dump());db.add(row);db.commit();return {"id":row.id,"status":row.status}
@router.get("/teams/{team_id}/code/status")
def code_status(team_id:UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):
    team_or_404(db,team_id)
    if not member(db,team_id,user.id):raise HTTPException(403,"Team membership required")
    return {"status":"unavailable","message":"CRDT/WebSocket collaboration service is not configured. No shared editing session was started."}

@router.get("/hackathons")
def hackathons(db:Session=Depends(get_db)):return db.scalars(select(HackathonEvent).where(HackathonEvent.status=="published").order_by(HackathonEvent.starts_at)).all()
@router.get("/hackathons/{slug}")
def hackathon(slug:str,db:Session=Depends(get_db)):
    row=db.scalar(select(HackathonEvent).where(HackathonEvent.slug==slug,HackathonEvent.status=="published"));
    if not row:raise HTTPException(404,"Hackathon not found")
    return row
@router.post("/hackathons/{event_id}/register")
def register_hackathon(event_id:UUID,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    event=db.scalar(select(HackathonEvent).where(HackathonEvent.id==event_id,HackathonEvent.status=="published"));t=now()
    if not event or not(event.registration_starts_at<=t<=event.registration_ends_at):raise HTTPException(409,"Hackathon registration is closed")
    if db.scalar(select(HackathonRegistration).where(HackathonRegistration.event_id==event.id,HackathonRegistration.user_id==user.id)):raise HTTPException(409,"Already registered")
    db.add(HackathonRegistration(event_id=event.id,user_id=user.id));db.commit();return {"status":"registered"}
@router.post("/hackathons/{event_id}/submissions",status_code=201)
def hackathon_submit(event_id:UUID,payload:SubmissionIn,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    event=db.scalar(select(HackathonEvent).where(HackathonEvent.id==event_id,HackathonEvent.status=="published"));t=now()
    if not event or not(event.starts_at<=t<=event.ends_at):raise HTTPException(409,"Hackathon submission window is closed")
    registered=db.scalar(select(HackathonRegistration).where(HackathonRegistration.event_id==event.id,HackathonRegistration.user_id==user.id,HackathonRegistration.status=="registered"))
    if not registered:raise HTTPException(403,"Hackathon registration required")
    row=HackathonSubmission(event_id=event.id,submitted_by=user.id,team_id=payload.team_id,title=payload.title,description=payload.description,github_url=payload.github_url,demo_url=payload.demo_url);db.add(row);db.commit();return {"id":row.id,"status":row.status}
@router.get("/competitions")
def competitions(db:Session=Depends(get_db)):return db.scalars(select(CodingCompetition).where(CodingCompetition.published.is_(True)).order_by(CodingCompetition.starts_at)).all()
@router.get("/competitions/{slug}")
def competition(slug:str,db:Session=Depends(get_db)):
    row=db.scalar(select(CodingCompetition).where(CodingCompetition.slug==slug,CodingCompetition.published.is_(True)))
    if not row:raise HTTPException(404,"Competition not found")
    return row
@router.get("/competitions/{competition_id}/leaderboard")
def leaderboard(competition_id:UUID,db:Session=Depends(get_db)):
    rows=db.scalars(select(CompetitionRanking).where(CompetitionRanking.competition_id==competition_id,CompetitionRanking.verified.is_(True)).order_by(CompetitionRanking.total_score.desc(),CompetitionRanking.penalty_seconds,CompetitionRanking.solved_count.desc())).all();return {"status":"verified_only","items":rows}
@router.post("/competitions/{competition_id}/register")
def register_competition(competition_id:UUID,user:User=Depends(verified_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.scalar(select(CodingCompetition).where(CodingCompetition.id==competition_id,CodingCompetition.published.is_(True)))
    if not row or now()>=row.ends_at:raise HTTPException(409,"Competition is unavailable")
    if db.scalar(select(CompetitionParticipant).where(CompetitionParticipant.competition_id==row.id,CompetitionParticipant.user_id==user.id)):raise HTTPException(409,"Already registered")
    db.add(CompetitionParticipant(competition_id=row.id,user_id=user.id));db.commit();return {"status":"registered"}
@router.get("/platform/collaboration/status")
def collaboration_status(user:User=Depends(require_role("admin","super_admin"))):return {"websocket_crdt":"not_configured","runner":"configured_separately","message":"Real-time collaboration is disabled until an authenticated CRDT gateway is deployed."}
