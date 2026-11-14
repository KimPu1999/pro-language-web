import re
from datetime import datetime,timezone
from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException,Query,status
from pydantic import BaseModel,Field
from sqlalchemy import func,select
from sqlalchemy.orm import Session
from .auth import current_user,require_csrf,require_role
from .config import settings
from .db import get_db
from .models import User,LiveClass,LiveClassSession,LiveClassRegistration,LiveClassWaitlist,LiveClassAttendance,LiveClassPresenceEvent,LiveClassChatMessage,LiveClassQuestion
router=APIRouter(prefix="/api/v1/live-classes",tags=["live-classes"])
class ClassIn(BaseModel):title:str=Field(min_length=3,max_length=200);description_en:str=Field(min_length=1,max_length=20000);description_mm:str|None=None;difficulty:str="beginner";capacity:int=Field(default=30,ge=1,le=1000)
class SessionIn(BaseModel):starts_at:datetime;ends_at:datetime;timezone:str="UTC"
class MessageIn(BaseModel):body:str=Field(min_length=1,max_length=2000)
def out(x):return {"id":str(x.id),"title":x.title,"slug":x.slug,"description_en":x.description_en,"description_mm":x.description_mm,"difficulty":x.difficulty,"capacity":x.capacity,"status":x.status}
def membership(session_id,user,db):
 s=db.get(LiveClassSession,session_id)
 if not s:raise HTTPException(404,"Session not found")
 reg=db.scalar(select(LiveClassRegistration).where(LiveClassRegistration.session_id==s.id,LiveClassRegistration.user_id==user.id,LiveClassRegistration.status=="registered"))
 if not reg and user.role not in {"admin","super_admin","instructor"}:raise HTTPException(403,"Class registration required")
 return s
@router.get("")
def catalog(search:str|None=None,page:int=Query(1,ge=1),page_size:int=Query(12,ge=1,le=50),db:Session=Depends(get_db)):
 q=select(LiveClass).where(LiveClass.published.is_(True));count=select(func.count()).select_from(LiveClass).where(LiveClass.published.is_(True))
 if search:q=q.where(LiveClass.title.ilike(f"%{search}%"));count=count.where(LiveClass.title.ilike(f"%{search}%"))
 total=db.scalar(count) or 0;return {"items":[out(x) for x in db.scalars(q.order_by(LiveClass.title).offset((page-1)*page_size).limit(page_size)).all()],"total":total,"page":page,"pages":(total+page_size-1)//page_size if total else 0}
@router.get("/{class_id}")
def detail(class_id:UUID,db:Session=Depends(get_db)):
 x=db.scalar(select(LiveClass).where(LiveClass.id==class_id,LiveClass.published.is_(True)))
 if not x:raise HTTPException(404,"Live class not found")
 sessions=db.scalars(select(LiveClassSession).where(LiveClassSession.class_id==x.id).order_by(LiveClassSession.starts_at)).all();return {**out(x),"sessions":[{"id":str(s.id),"starts_at":s.starts_at,"ends_at":s.ends_at,"timezone":s.timezone,"status":s.status} for s in sessions]}
@router.post("/{session_id}/register")
def register(session_id:UUID,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
 s=membership(session_id,user,db) if False else db.get(LiveClassSession,session_id)
 if not s:raise HTTPException(404,"Session not found")
 if db.scalar(select(LiveClassRegistration).where(LiveClassRegistration.session_id==s.id,LiveClassRegistration.user_id==user.id)):return {"status":"registered"}
 cls=db.get(LiveClass,s.class_id);count=db.scalar(select(func.count(LiveClassRegistration.id)).where(LiveClassRegistration.session_id==s.id,LiveClassRegistration.status=="registered")) or 0
 if count>=cls.capacity:pos=(db.scalar(select(func.count(LiveClassWaitlist.id)).where(LiveClassWaitlist.session_id==s.id))+1);db.add(LiveClassWaitlist(session_id=s.id,user_id=user.id,position=pos));db.commit();return {"status":"waitlisted","position":pos}
 db.add(LiveClassRegistration(session_id=s.id,user_id=user.id));db.commit();return {"status":"registered"}
@router.delete("/{session_id}/register")
def cancel(session_id:UUID,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
 x=db.scalar(select(LiveClassRegistration).where(LiveClassRegistration.session_id==session_id,LiveClassRegistration.user_id==user.id));
 if x:db.delete(x);db.commit()
 return {"status":"cancelled"}
@router.post("/{session_id}/room-token")
def room_token(session_id:UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):
 membership(session_id,user,db)
 if not settings.video_enabled or settings.video_provider=="disabled":return {"status":"unavailable","message":"Video provider is not configured."}
 raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE,"The configured video provider adapter is unavailable; room access is disabled.")
@router.post("/{session_id}/presence")
def presence(session_id:UUID,event_type:str,event_key:str=Query(...,min_length=1,max_length=120),user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
 s=membership(session_id,user,db)
 if not db.scalar(select(LiveClassPresenceEvent).where(LiveClassPresenceEvent.session_id==s.id,LiveClassPresenceEvent.user_id==user.id,LiveClassPresenceEvent.event_key==event_key)):
  db.add(LiveClassPresenceEvent(session_id=s.id,user_id=user.id,event_key=event_key,event_type=event_type));a=db.scalar(select(LiveClassAttendance).where(LiveClassAttendance.session_id==s.id,LiveClassAttendance.user_id==user.id)) or LiveClassAttendance(session_id=s.id,user_id=user.id);a.joined_at=a.joined_at or datetime.now(timezone.utc);a.left_at=datetime.now(timezone.utc) if event_type=="leave" else None;db.add(a);db.commit()
 return {"status":"accepted"}
@router.post("/{session_id}/chat")
def chat(session_id:UUID,p:MessageIn,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
 s=membership(session_id,user,db);x=LiveClassChatMessage(session_id=s.id,user_id=user.id,body=p.body.strip());db.add(x);db.commit();return {"id":str(x.id),"body":x.body,"created_at":x.created_at}
@router.get("/{session_id}/chat")
def chat_list(session_id:UUID,user:User=Depends(current_user),db:Session=Depends(get_db)):s=membership(session_id,user,db);return db.scalars(select(LiveClassChatMessage).where(LiveClassChatMessage.session_id==s.id,LiveClassChatMessage.status=="visible").order_by(LiveClassChatMessage.created_at).limit(100)).all()
@router.post("/{session_id}/questions")
def question(session_id:UUID,p:MessageIn,user:User=Depends(current_user),_:None=Depends(require_csrf),db:Session=Depends(get_db)):s=membership(session_id,user,db);x=LiveClassQuestion(session_id=s.id,user_id=user.id,body=p.body);db.add(x);db.commit();return {"id":str(x.id),"body":x.body}
@router.post("/admin",status_code=201)
def create(p:ClassIn,user:User=Depends(require_role("instructor","admin","super_admin")),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
 slug=re.sub(r"[^a-z0-9]+","-",p.title.lower()).strip("-")+f"-{str(user.id)[:8]}";x=LiveClass(created_by=user.id,title=p.title,slug=slug,description_en=p.description_en,description_mm=p.description_mm,difficulty=p.difficulty,capacity=p.capacity);db.add(x);db.commit();return out(x)
@router.post("/admin/{class_id}/sessions",status_code=201)
def schedule(class_id:UUID,p:SessionIn,user:User=Depends(require_role("instructor","admin","super_admin")),_:None=Depends(require_csrf),db:Session=Depends(get_db)):
 x=db.get(LiveClass,class_id)
 if not x or (user.role=="instructor" and x.created_by!=user.id):raise HTTPException(403,"Instructor ownership required")
 if p.starts_at.tzinfo is None or p.ends_at.tzinfo is None or p.ends_at<=p.starts_at:raise HTTPException(422,"Valid timezone-aware schedule required")
 s=LiveClassSession(class_id=x.id,starts_at=p.starts_at.astimezone(timezone.utc),ends_at=p.ends_at.astimezone(timezone.utc),timezone=p.timezone);db.add(s);db.commit();return {"id":str(s.id),"starts_at":s.starts_at}
