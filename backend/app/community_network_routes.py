import json
from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .admin_routes import full_admin
from .auth import check_rate_limit, current_user, require_csrf, require_role, verified_user
from .db import get_db
from .models import (CommunityActivityEvent, CommunityAuditLog, CommunityClubMembership, CommunityCodingClub, CommunityDeveloperConnection, CommunityEvent, CommunityEventRegistration, CommunityPeerLearningRequest, CommunityReputationEvent, CommunitySafetyReport, DeveloperPublicProfile, StudyGroup, StudyGroupMember, User, UserBlock)

router=APIRouter(prefix="/api/v1/community-network",tags=["global community"])
ADMIN={"admin","platform_admin","super_admin"}
def audit(db,user,action,entity,entity_id=None): db.add(CommunityAuditLog(actor_id=user.id if user else None,action=action,entity_type=entity,entity_id=entity_id))
def slugify(value): return "-".join("".join(c.lower() if c.isalnum() else " " for c in value).split())
def visible_profile(db,user_id): return db.scalar(select(DeveloperPublicProfile).where(DeveloperPublicProfile.user_id==user_id,DeveloperPublicProfile.visibility=="public"))
class ClubIn(BaseModel): name:str=Field(min_length=2,max_length=160); description:str=Field(default="",max_length=5000); technology:str=Field(min_length=1,max_length=80)
class PeerIn(BaseModel): topic:str=Field(min_length=2,max_length=120); goals:str=Field(default="",max_length=3000); availability:list[str]=Field(default_factory=list,max_length=20)
class EventIn(BaseModel): title:str=Field(min_length=2,max_length=180); description:str=Field(min_length=1,max_length=8000); event_type:str=Field(pattern="^(workshop|coding_session|study_group|hackathon|meetup|open_source|qa)$"); starts_at:datetime; ends_at:datetime; capacity:int|None=Field(default=None,ge=1,le=10000)
class ConnectionIn(BaseModel): recipient_id:UUID
class ReportIn(BaseModel): target_type:str=Field(min_length=2,max_length=40); target_id:UUID; reason:str=Field(min_length=3,max_length=2000)

@router.get("/hub")
def hub(user=Depends(current_user),db:Session=Depends(get_db)):
    groups=db.scalars(select(StudyGroup).join(StudyGroupMember,StudyGroupMember.group_id==StudyGroup.id).where(StudyGroupMember.user_id==user.id,StudyGroup.status=="active").limit(20)).all();clubs=db.scalars(select(CommunityCodingClub).where(CommunityCodingClub.status=="active",CommunityCodingClub.visibility=="public").order_by(CommunityCodingClub.created_at.desc()).limit(6)).all();events=db.scalars(select(CommunityEvent).where(CommunityEvent.status=="published",CommunityEvent.starts_at>datetime.now(timezone.utc)).order_by(CommunityEvent.starts_at).limit(6)).all()
    return {"joined_groups":[{"id":x.id,"slug":x.slug,"name":x.name,"visibility":x.visibility} for x in groups],"recommended_clubs":[{"id":x.id,"slug":x.slug,"name":x.name,"technology":x.technology} for x in clubs],"upcoming_events":[{"id":x.id,"slug":x.slug,"title":x.title,"starts_at":x.starts_at,"event_type":x.event_type} for x in events],"realtime_status":"configured_only_when_enabled"}
@router.get("/clubs")
def clubs(technology:str|None=None,db:Session=Depends(get_db)):
    q=select(CommunityCodingClub).where(CommunityCodingClub.status=="active",CommunityCodingClub.visibility=="public");
    if technology:q=q.where(CommunityCodingClub.technology==technology)
    return db.scalars(q.order_by(CommunityCodingClub.name)).all()
@router.post("/clubs",status_code=201)
def create_club(body:ClubIn,user=Depends(verified_user),_=Depends(require_csrf),db:Session=Depends(get_db)):
    slug=f"{slugify(body.name)}-{str(user.id)[:8]}";row=CommunityCodingClub(owner_id=user.id,name=body.name,slug=slug,description=body.description,technology=body.technology);db.add(row);db.flush();db.add(CommunityClubMembership(club_id=row.id,user_id=user.id,role="owner"));audit(db,user,"club_created","club",row.id);db.commit();return {"id":row.id,"slug":row.slug,"status":row.status}
@router.post("/clubs/{club_id}/join")
def join_club(club_id:UUID,user=Depends(verified_user),_=Depends(require_csrf),db:Session=Depends(get_db)):
    club=db.scalar(select(CommunityCodingClub).where(CommunityCodingClub.id==club_id,CommunityCodingClub.status=="active",CommunityCodingClub.visibility=="public"));
    if not club:raise HTTPException(404,"Public club not found")
    if db.scalar(select(CommunityClubMembership).where(CommunityClubMembership.club_id==club_id,CommunityClubMembership.user_id==user.id)):raise HTTPException(409,"Already a club member")
    db.add(CommunityClubMembership(club_id=club_id,user_id=user.id));audit(db,user,"club_joined","club",club_id);db.commit();return {"status":"joined"}
@router.get("/developers")
def developers(search:str|None=None,limit:int=Query(20,ge=1,le=50),db:Session=Depends(get_db)):
    q=select(DeveloperPublicProfile,User).join(User,User.id==DeveloperPublicProfile.user_id).where(DeveloperPublicProfile.visibility=="public",User.account_status=="active");rows=db.execute(q.limit(limit)).all();return [{"user_id":u.id,"username":p.username,"headline":p.headline,"bio":p.bio} for p,u in rows if not search or search.lower() in (p.username+" "+p.headline+" "+p.bio).lower()]
@router.post("/connections",status_code=201)
def connect(body:ConnectionIn,user=Depends(verified_user),_=Depends(require_csrf),db:Session=Depends(get_db)):
    check_rate_limit(f"community-connect:{user.id}",20,3600)
    if body.recipient_id==user.id or not visible_profile(db,body.recipient_id):raise HTTPException(404,"Developer is not available for networking")
    if db.scalar(select(UserBlock).where(UserBlock.user_id==body.recipient_id,UserBlock.blocked_user_id==user.id)):raise HTTPException(403,"Connection unavailable")
    row=CommunityDeveloperConnection(requester_id=user.id,recipient_id=body.recipient_id);db.add(row);audit(db,user,"connection_requested","connection",row.id)
    try:db.commit()
    except Exception:db.rollback();raise HTTPException(409,"Connection already requested")
    return {"id":row.id,"status":row.status}
@router.post("/peer-learning",status_code=201)
def peer(body:PeerIn,user=Depends(verified_user),_=Depends(require_csrf),db:Session=Depends(get_db)):
    check_rate_limit(f"peer-request:{user.id}",10,3600);row=CommunityPeerLearningRequest(requester_id=user.id,topic=body.topic,goals=body.goals,availability_json=json.dumps(body.availability));db.add(row);audit(db,user,"peer_learning_requested","peer_request",row.id);db.commit();return {"id":row.id,"status":row.status}
@router.get("/peer-learning")
def peer_list(user=Depends(current_user),db:Session=Depends(get_db)): return db.scalars(select(CommunityPeerLearningRequest).where(CommunityPeerLearningRequest.status=="open",CommunityPeerLearningRequest.requester_id!=user.id).order_by(CommunityPeerLearningRequest.created_at.desc()).limit(50)).all()
@router.get("/events")
def events(db:Session=Depends(get_db)): return db.scalars(select(CommunityEvent).where(CommunityEvent.status=="published").order_by(CommunityEvent.starts_at).limit(100)).all()
@router.post("/events",status_code=201)
def create_event(body:EventIn,user=Depends(verified_user),_=Depends(require_csrf),db:Session=Depends(get_db)):
    if body.ends_at<=body.starts_at:raise HTTPException(422,"Event end must be after start")
    row=CommunityEvent(organizer_id=user.id,title=body.title,slug=f"{slugify(body.title)}-{str(user.id)[:8]}",description=body.description,event_type=body.event_type,starts_at=body.starts_at,ends_at=body.ends_at,capacity=body.capacity);db.add(row);audit(db,user,"event_created","event",row.id);db.commit();return {"id":row.id,"slug":row.slug,"status":row.status}
@router.post("/events/{event_id}/publish")
def publish_event(event_id:UUID,user=Depends(require_role(*ADMIN)),_=Depends(require_csrf),db:Session=Depends(get_db)):
    row=db.get(CommunityEvent,event_id)
    if not row:raise HTTPException(404,"Event not found")
    row.status="published";audit(db,user,"event_published","event",row.id);db.commit();return {"status":row.status}
@router.post("/events/{event_id}/register")
def register_event(event_id:UUID,user=Depends(verified_user),_=Depends(require_csrf),db:Session=Depends(get_db)):
    event=db.scalar(select(CommunityEvent).where(CommunityEvent.id==event_id,CommunityEvent.status=="published"));
    if not event:raise HTTPException(404,"Event not found")
    if db.scalar(select(CommunityEventRegistration).where(CommunityEventRegistration.event_id==event_id,CommunityEventRegistration.user_id==user.id)):raise HTTPException(409,"Already registered")
    count=db.scalar(select(func.count()).select_from(CommunityEventRegistration).where(CommunityEventRegistration.event_id==event_id,CommunityEventRegistration.status=="registered")) or 0;status="registered" if event.capacity is None or count<event.capacity else "waitlisted";row=CommunityEventRegistration(event_id=event_id,user_id=user.id,status=status);db.add(row);audit(db,user,"event_registered","event",event_id);db.commit();return {"status":status}
@router.get("/feed")
def feed(user=Depends(current_user),db:Session=Depends(get_db)):
    blocked=select(UserBlock.blocked_user_id).where(UserBlock.user_id==user.id);rows=db.scalars(select(CommunityActivityEvent).where(CommunityActivityEvent.visibility=="public",~CommunityActivityEvent.actor_id.in_(blocked)).order_by(CommunityActivityEvent.created_at.desc()).limit(50)).all();return rows
@router.get("/reputation")
def reputation(user=Depends(current_user),db:Session=Depends(get_db)): return {"verified_points":db.scalar(select(func.coalesce(func.sum(CommunityReputationEvent.points),0)).where(CommunityReputationEvent.user_id==user.id,CommunityReputationEvent.verified.is_(True))) or 0,"source":"verified community contributions only"}
@router.post("/reports",status_code=201)
def report(body:ReportIn,user=Depends(verified_user),_=Depends(require_csrf),db:Session=Depends(get_db)):
    check_rate_limit(f"community-report:{user.id}",10,3600);row=CommunitySafetyReport(reporter_id=user.id,target_type=body.target_type,target_id=body.target_id,reason=body.reason);db.add(row);audit(db,user,"safety_report_created","report",row.id);db.commit();return {"id":row.id,"status":row.status}
@router.get("/moderation")
def moderation(user=Depends(full_admin),db:Session=Depends(get_db)):return db.scalars(select(CommunitySafetyReport).where(CommunitySafetyReport.status=="open").order_by(CommunitySafetyReport.created_at)).all()
@router.get("/analytics")
def analytics(user=Depends(full_admin),db:Session=Depends(get_db)):
    return {"active_clubs":db.scalar(select(func.count()).select_from(CommunityCodingClub).where(CommunityCodingClub.status=="active")) or 0,"published_events":db.scalar(select(func.count()).select_from(CommunityEvent).where(CommunityEvent.status=="published")) or 0,"event_registrations":db.scalar(select(func.count()).select_from(CommunityEventRegistration)) or 0,"open_reports":db.scalar(select(func.count()).select_from(CommunitySafetyReport).where(CommunitySafetyReport.status=="open")) or 0,"data_source":"postgresql","privacy":"aggregate operational counts"}
