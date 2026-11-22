"""Public contact form and protected contact inbox."""
from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.orm import Session
from .admin_routes import full_admin
from .auth import check_rate_limit, require_csrf
from .db import get_db
from .models import ContactMessage, User
router = APIRouter(tags=["contact"])
class ContactMessageIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: str = Field(min_length=5, max_length=320)
    subject: str = Field(min_length=3, max_length=180)
    message: str = Field(min_length=10, max_length=5000)
    website: str = Field(default="", max_length=200)
    @field_validator("email")
    @classmethod
    def valid_email(cls, value: str) -> str:
        value = value.strip().lower()
        if value.count("@") != 1 or "." not in value.rsplit("@", 1)[1]: raise ValueError("Enter a valid email address")
        return value
class ContactStatusIn(BaseModel):
    status: str = Field(pattern="^(new|resolved|archived)$")
def serialize(row: ContactMessage): return {key: getattr(row, key) for key in row.__table__.columns.keys()}
@router.post("/api/v1/contact", status_code=201)
def submit_contact(payload: ContactMessageIn, request: Request, db: Session = Depends(get_db)):
    if payload.website.strip(): return {"status": "accepted"}
    client = request.client.host if request.client else "unknown"
    check_rate_limit(f"contact:{client}", limit=5, window_seconds=3600)
    row = ContactMessage(name=payload.name.strip(), email=payload.email, subject=payload.subject.strip(), message=payload.message.strip())
    db.add(row); db.commit(); db.refresh(row)
    return {"status": "received", "id": str(row.id)}
@router.get("/api/v1/admin/contact-messages")
def list_contact_messages(status_filter: str|None = Query(None, alias="status"), user: User = Depends(full_admin), db: Session = Depends(get_db)):
    query = select(ContactMessage).order_by(ContactMessage.created_at.desc()).limit(200)
    if status_filter: query = query.where(ContactMessage.status == status_filter)
    return [serialize(row) for row in db.scalars(query).all()]
@router.patch("/api/v1/admin/contact-messages/{message_id}")
def update_contact_message(message_id: UUID, payload: ContactStatusIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(ContactMessage, message_id)
    if not row: raise HTTPException(404, "Contact message not found")
    row.status = payload.status; row.resolved_at = datetime.now(timezone.utc) if payload.status == "resolved" else None; row.resolved_by = user.id if payload.status == "resolved" else None
    db.commit(); db.refresh(row)
    return serialize(row)
