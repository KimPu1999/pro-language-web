from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from .admin_routes import full_admin
from .auth import current_user, require_csrf
from .db import get_db
from .models import EngineeringIssue, IncidentEvent, MaintenanceWindow, PlatformIncident, PlatformRelease, ServiceHealthCheck, StudentFeedback, User

router = APIRouter(prefix="/api/v1/platform/operations", tags=["operations"])

class FeedbackIn(BaseModel):
    category: str = Field(min_length=2, max_length=40)
    title: str = Field(min_length=3, max_length=180)
    body: str = Field(min_length=10, max_length=10000)

class IncidentIn(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    description: str = Field(min_length=10, max_length=20000)
    severity: str = Field(default="medium", pattern="^(low|medium|high|critical)$")

class IncidentUpdate(BaseModel):
    status: str = Field(pattern="^(detected|acknowledged|investigating|mitigating|resolved|closed)$")
    notes: str = Field(default="", max_length=10000)

class IssueIn(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    description: str = Field(min_length=10, max_length=20000)
    affected_module: str = Field(default="", max_length=100)
    severity: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")

def serialize(row):
    return {key: getattr(row, key) for key in row.__table__.columns.keys()}

@router.post("/feedback", status_code=201)
def create_feedback(payload: FeedbackIn, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = StudentFeedback(user_id=user.id, **payload.model_dump())
    db.add(row); db.commit(); db.refresh(row)
    return serialize(row)

@router.get("/feedback/mine")
def my_feedback(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [serialize(row) for row in db.scalars(select(StudentFeedback).where(StudentFeedback.user_id == user.id).order_by(StudentFeedback.created_at.desc()).limit(100)).all()]

@router.get("/feedback")
def feedback_inbox(status_filter: str | None = Query(None, alias="status"), user: User = Depends(full_admin), db: Session = Depends(get_db)):
    query = select(StudentFeedback).order_by(StudentFeedback.created_at.desc())
    if status_filter: query = query.where(StudentFeedback.status == status_filter)
    return [serialize(row) for row in db.scalars(query.limit(100)).all()]

@router.post("/incidents", status_code=201)
def create_incident(payload: IncidentIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = PlatformIncident(owner_id=user.id, **payload.model_dump()); db.add(row); db.flush(); db.add(IncidentEvent(incident_id=row.id, actor_id=user.id, event_type="created", body="Incident created")); db.commit(); db.refresh(row)
    return serialize(row)

@router.get("/incidents")
def list_incidents(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return [serialize(row) for row in db.scalars(select(PlatformIncident).order_by(PlatformIncident.created_at.desc()).limit(100)).all()]

@router.patch("/incidents/{incident_id}")
def update_incident(incident_id: UUID, payload: IncidentUpdate, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(PlatformIncident, incident_id)
    if not row: raise HTTPException(404, "Incident not found")
    row.status = payload.status; row.resolution_notes = payload.notes if payload.status in {"resolved", "closed"} else row.resolution_notes
    db.add(IncidentEvent(incident_id=row.id, actor_id=user.id, event_type=payload.status, body=payload.notes or f"Status changed to {payload.status}")); db.commit(); db.refresh(row)
    return serialize(row)

@router.get("/incidents/{incident_id}")
def incident_detail(incident_id: UUID, user: User = Depends(full_admin), db: Session = Depends(get_db)):
    row = db.get(PlatformIncident, incident_id)
    if not row: raise HTTPException(404, "Incident not found")
    events = db.scalars(select(IncidentEvent).where(IncidentEvent.incident_id == row.id).order_by(IncidentEvent.created_at)).all()
    return {**serialize(row), "events": [serialize(event) for event in events]}

@router.post("/issues", status_code=201)
def create_issue(payload: IssueIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = EngineeringIssue(reporter_id=user.id, **payload.model_dump()); db.add(row); db.commit(); db.refresh(row); return serialize(row)

@router.get("/issues")
def list_issues(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return [serialize(row) for row in db.scalars(select(EngineeringIssue).order_by(EngineeringIssue.created_at.desc()).limit(100)).all()]

@router.get("/releases")
def list_releases(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return [serialize(row) for row in db.scalars(select(PlatformRelease).order_by(PlatformRelease.created_at.desc()).limit(100)).all()]

@router.get("/maintenance/current")
def current_maintenance(db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    rows = db.scalars(select(MaintenanceWindow).where(MaintenanceWindow.status == "scheduled", MaintenanceWindow.starts_at <= now, MaintenanceWindow.ends_at >= now).order_by(MaintenanceWindow.starts_at)).all()
    return [serialize(row) for row in rows]

@router.get("/health-history")
def health_history(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    rows = db.scalars(select(ServiceHealthCheck).order_by(ServiceHealthCheck.created_at.desc()).limit(100)).all()
    return [serialize(row) for row in rows]
