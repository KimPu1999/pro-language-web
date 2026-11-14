import base64, json
from datetime import timedelta
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .auth import SESSION_COOKIE, current_user, now, require_csrf, require_role, verified_user
from .config import settings
from .db import SessionLocal, get_db
from .models import (CollaborationAuditLog, CollaborationChatMessage, CollaborationDocument,
    CollaborationDocumentUpdate, CollaborationExecutionJob, CollaborationInvitation,
    CollaborationPairRoleEvent, CollaborationPairSession, CollaborationPresenceEvent,
    CollaborationRecordingConsent, CollaborationRoom, CollaborationRoomMember,
    CollaborationSession, CollaborationSnapshot, OrganizationMembership, User)

router = APIRouter(prefix="/api/v1", tags=["realtime-collaboration"])
ROOM_ROLES = {"owner", "instructor", "member", "viewer"}

class RoomIn(BaseModel):
    name: str = Field(min_length=2, max_length=180)
    description: str = Field(default="", max_length=5000)
    organization_id: UUID | None = None
    visibility: str = Field(default="private", pattern="^(private|team|instructor)$")
class MemberIn(BaseModel):
    user_id: UUID
    role: str = Field(default="member", pattern="^(instructor|member|viewer)$")
class ChatIn(BaseModel):
    body: str = Field(min_length=1, max_length=4000)
class DocumentIn(BaseModel):
    path: str = Field(pattern=r"^[A-Za-z0-9_./-]+$", max_length=240)
    language: str = Field(min_length=1, max_length=40)
class SnapshotIn(BaseModel):
    document_id: UUID
class RunIn(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=180)
class RoleIn(BaseModel):
    user_id: UUID

def audit(db, actor, room_id, action, metadata=None):
    db.add(CollaborationAuditLog(actor_id=actor.id if actor else None, room_id=room_id, action=action, metadata_json=json.dumps(metadata or {})))

def membership(db, room_id, user_id):
    return db.scalar(select(CollaborationRoomMember).where(CollaborationRoomMember.room_id == room_id, CollaborationRoomMember.user_id == user_id, CollaborationRoomMember.status == "active"))

def room_access(db, room_id, user):
    room = db.get(CollaborationRoom, room_id)
    member = membership(db, room_id, user.id) if room else None
    if not room or room.status != "active" or not member:
        raise HTTPException(403, "Active room membership required")
    return room, member

def org_member(db, organization_id, user_id):
    return db.scalar(select(OrganizationMembership).where(OrganizationMembership.organization_id == organization_id, OrganizationMembership.user_id == user_id, OrganizationMembership.status == "active"))

@router.get("/collaboration/dashboard")
def dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)):
    ids = select(CollaborationRoomMember.room_id).where(CollaborationRoomMember.user_id == user.id, CollaborationRoomMember.status == "active")
    rooms = db.scalars(select(CollaborationRoom).where(CollaborationRoom.id.in_(ids), CollaborationRoom.status == "active").order_by(CollaborationRoom.updated_at.desc()).limit(50)).all()
    return {"items": [{"id": r.id, "name": r.name, "description": r.description, "visibility": r.visibility, "organization_id": r.organization_id} for r in rooms], "realtime_status": "configured" if settings.collaboration_enabled else "Not Configured", "data_source": "postgresql"}

@router.get("/collaboration/rooms")
def rooms(user: User = Depends(current_user), db: Session = Depends(get_db), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=50)):
    ids = select(CollaborationRoomMember.room_id).where(CollaborationRoomMember.user_id == user.id, CollaborationRoomMember.status == "active")
    rows = db.scalars(select(CollaborationRoom).where(CollaborationRoom.id.in_(ids), CollaborationRoom.status == "active").order_by(CollaborationRoom.name).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [{"id": r.id, "name": r.name, "visibility": r.visibility, "organization_id": r.organization_id} for r in rows], "page": page, "page_size": page_size}

@router.post("/collaboration/rooms", status_code=201)
def create_room(payload: RoomIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if payload.organization_id and not org_member(db, payload.organization_id, user.id):
        raise HTTPException(403, "Organization membership required")
    room = CollaborationRoom(owner_id=user.id, **payload.model_dump()); db.add(room); db.flush()
    db.add(CollaborationRoomMember(room_id=room.id, user_id=user.id, role="owner")); audit(db, user, room.id, "room_created"); db.commit()
    return {"id": room.id, "status": room.status, "realtime_status": "configured" if settings.collaboration_enabled else "Not Configured"}

@router.get("/collaboration/rooms/{room_id}")
def room_detail(room_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    room, me = room_access(db, room_id, user); members = db.scalars(select(CollaborationRoomMember).where(CollaborationRoomMember.room_id == room.id, CollaborationRoomMember.status == "active")).all()
    docs = db.scalars(select(CollaborationDocument).where(CollaborationDocument.room_id == room.id).order_by(CollaborationDocument.path)).all()
    return {"id": room.id, "name": room.name, "description": room.description, "visibility": room.visibility, "role": me.role, "members": [{"user_id": m.user_id, "role": m.role} for m in members], "documents": [{"id": d.id, "path": d.path, "language": d.language, "version": d.version} for d in docs], "realtime_status": "configured" if settings.collaboration_enabled else "Not Configured"}

@router.post("/collaboration/rooms/{room_id}/members")
def add_member(room_id: UUID, payload: MemberIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    room, me = room_access(db, room_id, user)
    if me.role not in {"owner", "instructor"} or not db.get(User, payload.user_id): raise HTTPException(403, "Room owner permission required")
    if membership(db, room.id, payload.user_id): raise HTTPException(409, "User is already a room member")
    row = CollaborationRoomMember(room_id=room.id, user_id=payload.user_id, role=payload.role); db.add(row); audit(db, user, room.id, "member_added", {"user_id": str(payload.user_id)}); db.commit(); return {"id": row.id, "status": "active"}

@router.post("/collaboration/rooms/{room_id}/documents", status_code=201)
def create_document(room_id: UUID, payload: DocumentIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    room, _ = room_access(db, room_id, user)
    if ".." in payload.path.split("/") or payload.path.startswith("/"): raise HTTPException(422, "Unsafe document path")
    if db.scalar(select(CollaborationDocument).where(CollaborationDocument.room_id == room.id, CollaborationDocument.path == payload.path)): raise HTTPException(409, "Document already exists")
    doc = CollaborationDocument(room_id=room.id, **payload.model_dump()); db.add(doc); audit(db, user, room.id, "document_created", {"path": payload.path}); db.commit(); return {"id": doc.id, "path": doc.path, "version": doc.version}

@router.post("/collaboration/rooms/{room_id}/snapshots", status_code=201)
def snapshot(room_id: UUID, payload: SnapshotIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    room, _ = room_access(db, room_id, user); doc = db.scalar(select(CollaborationDocument).where(CollaborationDocument.id == payload.document_id, CollaborationDocument.room_id == room.id))
    if not doc: raise HTTPException(404, "Document not found")
    row = CollaborationSnapshot(document_id=doc.id, created_by=user.id, version=doc.version, state_bytes=doc.state_bytes); db.add(row); audit(db, user, room.id, "snapshot_created", {"document_id": str(doc.id)}); db.commit(); return {"id": row.id, "version": row.version}

@router.get("/collaboration/rooms/{room_id}/chat")
def chat_history(room_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db), limit: int = Query(50, ge=1, le=100)):
    room_access(db, room_id, user); rows = db.scalars(select(CollaborationChatMessage).where(CollaborationChatMessage.room_id == room_id, CollaborationChatMessage.removed_at.is_(None)).order_by(CollaborationChatMessage.created_at.desc()).limit(limit)).all()
    return {"items": [{"id": x.id, "sender_id": x.sender_id, "body": x.body, "created_at": x.created_at} for x in reversed(rows)]}

@router.post("/collaboration/rooms/{room_id}/chat", status_code=201)
def send_chat(room_id: UUID, payload: ChatIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    room_access(db, room_id, user); row = CollaborationChatMessage(room_id=room_id, sender_id=user.id, body=payload.body.strip()); db.add(row); db.commit(); return {"id": row.id, "status": "sent"}

@router.post("/collaboration/rooms/{room_id}/pair", status_code=201)
def pair(room_id: UUID, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    room, _ = room_access(db, room_id, user); if_existing = db.scalar(select(CollaborationPairSession).where(CollaborationPairSession.room_id == room.id, CollaborationPairSession.status == "active"));
    if if_existing: return {"id": if_existing.id, "driver_id": if_existing.driver_id, "navigator_id": if_existing.navigator_id, "idempotent": True}
    row = CollaborationPairSession(room_id=room.id, driver_id=user.id); db.add(row); audit(db, user, room.id, "pair_session_created"); db.commit(); return {"id": row.id, "driver_id": row.driver_id, "navigator_id": row.navigator_id}

@router.post("/collaboration/pair/{pair_id}/switch")
def switch_pair(pair_id: UUID, payload: RoleIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(CollaborationPairSession, pair_id)
    if not row: raise HTTPException(404, "Pair session not found")
    _, me = room_access(db, row.room_id, user)
    if me.role not in {"owner", "instructor"} and user.id not in {row.driver_id, row.navigator_id}: raise HTTPException(403, "Pair role change is not authorized")
    if not membership(db, row.room_id, payload.user_id): raise HTTPException(403, "Target must be a room member")
    previous = row.driver_id; row.driver_id, row.navigator_id = payload.user_id, previous; db.add(CollaborationPairRoleEvent(pair_session_id=row.id, actor_id=user.id, from_user_id=previous, to_user_id=payload.user_id)); db.commit(); return {"driver_id": row.driver_id, "navigator_id": row.navigator_id}

@router.post("/collaboration/rooms/{room_id}/run", status_code=202)
def shared_run(room_id: UUID, payload: RunIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    room, _ = room_access(db, room_id, user); existing = db.scalar(select(CollaborationExecutionJob).where(CollaborationExecutionJob.room_id == room.id, CollaborationExecutionJob.idempotency_key == payload.idempotency_key))
    if existing: return {"id": existing.id, "status": existing.status, "idempotent": True}
    enabled = settings.runner_enabled; row = CollaborationExecutionJob(room_id=room.id, requested_by=user.id, idempotency_key=payload.idempotency_key, status="queued" if enabled else "runner_unavailable", failure_reason=None if enabled else "Secure runner is not configured; no code was executed."); db.add(row); db.commit(); return {"id": row.id, "status": row.status, "message": row.failure_reason or "Queued for isolated runner."}

@router.post("/collaboration/sessions/{session_id}/consent")
def recording_consent(session_id: UUID, consented: bool, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    session = db.get(CollaborationSession, session_id)
    if not session or not membership(db, session.room_id, user.id): raise HTTPException(403, "Session membership required")
    row = db.scalar(select(CollaborationRecordingConsent).where(CollaborationRecordingConsent.session_id == session.id, CollaborationRecordingConsent.user_id == user.id))
    if not row: row = CollaborationRecordingConsent(session_id=session.id, user_id=user.id); db.add(row)
    row.consented = consented; row.withdrawn_at = None if consented else now(); db.commit(); return {"consented": row.consented}

@router.get("/platform/collaboration")
def platform_status(user: User = Depends(require_role("admin", "platform_admin", "super_admin")), db: Session = Depends(get_db)):
    rooms = db.scalar(select(func.count()).select_from(CollaborationRoom).where(CollaborationRoom.status == "active")) or 0
    return {"rooms": rooms, "websocket_crdt": "configured" if settings.collaboration_enabled else "Not Configured", "runner": "configured" if settings.runner_enabled else "Not Configured", "recordings": "disabled_by_default", "data_source": "postgresql"}

@router.websocket("/ws/collaboration/{room_id}")
async def collaboration_socket(websocket: WebSocket, room_id: UUID):
    origin = websocket.headers.get("origin")
    if origin and origin not in settings.cors_origin_list: await websocket.close(code=4403); return
    if not settings.collaboration_enabled: await websocket.close(code=1013, reason="Realtime collaboration is not configured"); return
    db = SessionLocal()
    try:
        raw = websocket.cookies.get(SESSION_COOKIE); user = current_user(db, raw)
        room = db.get(CollaborationRoom, room_id); member = membership(db, room_id, user.id)
        if not room or room.status != "active" or not member: await websocket.close(code=4403); return
        await websocket.accept()
        while True:
            message = await websocket.receive_json()
            if len(json.dumps(message)) > settings.collaboration_max_message_bytes: await websocket.send_json({"type":"error","message":"Message too large"}); continue
            kind = message.get("type")
            if kind == "presence":
                db.add(CollaborationPresenceEvent(room_id=room_id, user_id=user.id, event_type="presence", payload_json=json.dumps(message.get("payload", {})))); db.commit(); await websocket.send_json({"type":"presence","user_id":str(user.id),"payload":message.get("payload", {})})
            elif kind == "chat":
                body = str(message.get("body", ""));
                if not body or len(body) > 4000: await websocket.send_json({"type":"error","message":"Invalid chat message"}); continue
                db.add(CollaborationChatMessage(room_id=room_id, sender_id=user.id, body=body)); db.commit(); await websocket.send_json({"type":"chat","user_id":str(user.id),"body":body})
            elif kind == "crdt_update":
                encoded = message.get("update"); document_id = message.get("document_id")
                try: update = base64.b64decode(encoded, validate=True); doc_id = UUID(str(document_id))
                except Exception: await websocket.send_json({"type":"error","message":"Invalid CRDT update"}); continue
                if len(update) > settings.collaboration_max_message_bytes: await websocket.send_json({"type":"error","message":"CRDT update too large"}); continue
                doc = db.scalar(select(CollaborationDocument).where(CollaborationDocument.id == doc_id, CollaborationDocument.room_id == room_id));
                if not doc: await websocket.send_json({"type":"error","message":"Document not found"}); continue
                doc.version += 1; doc.state_bytes = update; db.add(CollaborationDocumentUpdate(document_id=doc.id, actor_id=user.id, sequence=doc.version, update_bytes=update)); db.commit(); await websocket.send_json({"type":"crdt_ack","document_id":str(doc.id),"version":doc.version})
            else: await websocket.send_json({"type":"error","message":"Unsupported collaboration event"})
    except (WebSocketDisconnect, HTTPException):
        try: await websocket.close()
        except Exception: pass
    finally: db.close()
