"""Phase 31 monitoring, feedback, release, and continuous-improvement APIs."""
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .auth import check_rate_limit, current_user, require_csrf
from .admin_routes import full_admin
from .db import get_db
from .models import (
    ImprovementEvent, ImprovementItem, MaintenanceWindow, OperationalReview, PlatformAlertEvent,
    PlatformBackupCheck, PlatformBugAttachment, PlatformBugReport, PlatformFeatureFlag,
    PlatformIncident, PlatformOperationsAuditLog, PlatformRelease, ReleaseApproval,
    RestoreDrill, ServiceHealthCheck, StudentFeedback, StudentFeedbackResponse, User,
)

router = APIRouter(prefix="/api/v1", tags=["phase31-operations"])


class FeedbackIn(BaseModel):
    category: str = Field(min_length=2, max_length=40)
    title: str = Field(min_length=3, max_length=180)
    body: str = Field(min_length=10, max_length=10000)


class BugIn(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    description: str = Field(min_length=10, max_length=20000)
    affected_page: str = Field(default="", max_length=300)
    reproduction_steps: str = Field(default="", max_length=10000)
    expected_result: str = Field(default="", max_length=5000)
    actual_result: str = Field(default="", max_length=5000)
    severity: str = Field(default="normal", pattern="^(normal|high|critical)$")


class HealthIn(BaseModel):
    service: str = Field(min_length=2, max_length=80)
    status: str = Field(pattern="^(healthy|degraded|unavailable|not_configured)$")
    latency_ms: int | None = Field(default=None, ge=0, le=600000)
    detail: str = Field(default="", max_length=240)


class AlertIn(BaseModel):
    service: str = Field(min_length=2, max_length=80)
    severity: str = Field(pattern="^(info|warning|critical)$")
    message: str = Field(min_length=3, max_length=1000)
    dedupe_key: str = Field(min_length=3, max_length=180)


class ImprovementIn(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    description: str = Field(min_length=10, max_length=10000)
    priority: str = Field(default="normal", pattern="^(low|normal|high|urgent)$")


class ReleaseIn(BaseModel):
    version: str = Field(min_length=1, max_length=50)
    notes: str = Field(min_length=3, max_length=20000)
    environment: str = Field(pattern="^(staging|production)$")


class FlagIn(BaseModel):
    key: str = Field(pattern=r"^[a-z][a-z0-9_.-]{1,119}$")
    description: str = Field(default="", max_length=300)
    enabled: bool = False
    rollout_percent: int = Field(default=0, ge=0, le=100)


class MaintenanceIn(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    notice: str = Field(min_length=3, max_length=10000)
    starts_at: datetime
    ends_at: datetime


class BackupIn(BaseModel):
    provider: str = Field(min_length=2, max_length=80)
    status: str = Field(pattern="^(success|failed|unknown)$")
    completed_at: datetime | None = None
    retention_until: datetime | None = None
    evidence_ref: str = Field(default="", max_length=500)


class ReviewIn(BaseModel):
    period: str = Field(min_length=2, max_length=30)
    summary: str = Field(min_length=3, max_length=20000)
    metrics_json: str = Field(default="{}", max_length=20000)


def serialize(row):
    return {key: getattr(row, key) for key in row.__table__.columns.keys()}


@router.get("/status")
def public_status(db: Session = Depends(get_db)):
    """Public, intentionally minimal status; no internal topology or secrets."""
    incidents = db.scalars(select(PlatformIncident).where(PlatformIncident.status.not_in({"resolved", "closed"})).order_by(PlatformIncident.created_at.desc()).limit(20)).all()
    maintenance = db.scalars(select(MaintenanceWindow).where(MaintenanceWindow.status == "scheduled", MaintenanceWindow.ends_at >= datetime.now(timezone.utc)).order_by(MaintenanceWindow.starts_at).limit(20)).all()
    return {"services": [{"name": "CodeMaster Academy", "status": "operational" if not incidents else "incident"}], "incidents": [serialize(row) for row in incidents], "maintenance": [serialize(row) for row in maintenance]}


@router.post("/feedback", status_code=201)
def create_feedback(payload: FeedbackIn, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    check_rate_limit(f"feedback:{user.id}", limit=5, window_seconds=3600)
    row = StudentFeedback(user_id=user.id, **payload.model_dump())
    db.add(row); db.commit(); db.refresh(row)
    return serialize(row)


@router.get("/feedback/my")
def my_feedback(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [serialize(row) for row in db.scalars(select(StudentFeedback).where(StudentFeedback.user_id == user.id).order_by(StudentFeedback.created_at.desc()).limit(100)).all()]


@router.get("/feedback")
def feedback_inbox(status_filter: str | None = Query(None, alias="status"), user: User = Depends(full_admin), db: Session = Depends(get_db)):
    query = select(StudentFeedback).order_by(StudentFeedback.created_at.desc()).limit(100)
    if status_filter: query = query.where(StudentFeedback.status == status_filter)
    return [serialize(row) for row in db.scalars(query).all()]


@router.post("/feedback/{feedback_id}/responses", status_code=201)
def respond_feedback(feedback_id: UUID, body: str = Query(..., min_length=3, max_length=10000), user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(StudentFeedback, feedback_id)
    if not row: raise HTTPException(404, "Feedback not found")
    row.student_response = body; row.status = "responded"; db.add(StudentFeedbackResponse(feedback_id=row.id, responder_id=user.id, body=body)); db.commit()
    return serialize(row)


@router.post("/support/report-bug", status_code=201)
def create_bug(payload: BugIn, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    check_rate_limit(f"bug:{user.id}", limit=10, window_seconds=3600)
    row = PlatformBugReport(reporter_id=user.id, **payload.model_dump()); db.add(row); db.commit(); db.refresh(row)
    return serialize(row)


@router.get("/support/report-bug/my")
def my_bugs(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [serialize(row) for row in db.scalars(select(PlatformBugReport).where(PlatformBugReport.reporter_id == user.id).order_by(PlatformBugReport.created_at.desc()).limit(100)).all()]


@router.post("/support/report-bug/{bug_id}/attachments", status_code=202)
def register_attachment(bug_id: UUID, storage_key: str = Query(..., min_length=1, max_length=500), content_type: str = Query(..., min_length=3, max_length=120), size_bytes: int = Query(..., ge=1, le=10_000_000), user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    bug = db.get(PlatformBugReport, bug_id)
    if not bug or bug.reporter_id != user.id: raise HTTPException(404, "Bug report not found")
    if not (content_type.startswith("image/") or content_type in {"text/plain", "application/pdf"}): raise HTTPException(422, "Unsupported attachment type")
    row = PlatformBugAttachment(bug_id=bug.id, storage_key=storage_key, content_type=content_type, size_bytes=size_bytes); db.add(row); db.commit(); db.refresh(row)
    return {"id": row.id, "status": "pending_scan", "message": "Metadata registered; upload and malware scanning are storage-provider responsibilities."}


@router.get("/platform/monitoring")
def monitoring(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    latest = db.scalars(select(ServiceHealthCheck).order_by(ServiceHealthCheck.created_at.desc()).limit(100)).all()
    return {"services": [serialize(row) for row in latest], "telemetry": "not_configured", "source": "persisted_health_checks_only"}


@router.post("/platform/monitoring/checks", status_code=201)
def ingest_health(payload: HealthIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = ServiceHealthCheck(**payload.model_dump()); db.add(row); db.add(PlatformOperationsAuditLog(actor_id=user.id, action="health_check_recorded", entity_type="service", metadata_json=f'{{"service":"{payload.service}"}}')); db.commit(); db.refresh(row)
    return serialize(row)


@router.get("/platform/alerts")
def alerts(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return [serialize(row) for row in db.scalars(select(PlatformAlertEvent).order_by(PlatformAlertEvent.created_at.desc()).limit(100)).all()]


@router.post("/platform/alerts", status_code=201)
def create_alert(payload: AlertIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    existing = db.scalar(select(PlatformAlertEvent).where(PlatformAlertEvent.dedupe_key == payload.dedupe_key))
    if existing: return {**serialize(existing), "deduplicated": True}
    row = PlatformAlertEvent(**payload.model_dump()); db.add(row); db.commit(); db.refresh(row); return serialize(row)


@router.post("/platform/alerts/{alert_id}/ack", status_code=200)
def acknowledge_alert(alert_id: UUID, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(PlatformAlertEvent, alert_id)
    if not row: raise HTTPException(404, "Alert not found")
    row.status = "acknowledged"; row.acknowledged_by = user.id; db.commit(); return serialize(row)


@router.get("/platform/improvements")
def improvements(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return [serialize(row) for row in db.scalars(select(ImprovementItem).order_by(ImprovementItem.updated_at.desc()).limit(100)).all()]


@router.post("/platform/improvements", status_code=201)
def create_improvement(payload: ImprovementIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = ImprovementItem(owner_id=user.id, **payload.model_dump()); db.add(row); db.flush(); db.add(ImprovementEvent(improvement_id=row.id, actor_id=user.id, event_type="created", detail="Backlog item created")); db.commit(); db.refresh(row); return serialize(row)


@router.get("/platform/releases")
def releases(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return [serialize(row) for row in db.scalars(select(PlatformRelease).order_by(PlatformRelease.created_at.desc()).limit(100)).all()]


@router.post("/platform/releases", status_code=201)
def create_release(payload: ReleaseIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if db.scalar(select(PlatformRelease).where(PlatformRelease.version == payload.version)): raise HTTPException(409, "Release version already exists")
    row = PlatformRelease(**payload.model_dump()); db.add(row); db.commit(); db.refresh(row); return serialize(row)


@router.post("/platform/releases/{release_id}/approve")
def approve_release(release_id: UUID, decision: str = Query(..., pattern="^(approved|rejected)$"), notes: str = Query("", max_length=5000), user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(PlatformRelease, release_id)
    if not row: raise HTTPException(404, "Release not found")
    db.add(ReleaseApproval(release_id=row.id, approver_id=user.id, decision=decision, notes=notes)); row.status = decision; row.approved_by = user.id if decision == "approved" else None; db.commit(); return serialize(row)


@router.get("/platform/feature-flags")
def flags(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return [serialize(row) for row in db.scalars(select(PlatformFeatureFlag).order_by(PlatformFeatureFlag.key)).all()]


@router.post("/platform/feature-flags", status_code=201)
def create_flag(payload: FlagIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if db.scalar(select(PlatformFeatureFlag).where(PlatformFeatureFlag.key == payload.key)): raise HTTPException(409, "Feature flag already exists")
    row = PlatformFeatureFlag(**payload.model_dump()); db.add(row); db.commit(); db.refresh(row); return serialize(row)


@router.get("/feature-flags/{key}")
def evaluate_flag(key: str, db: Session = Depends(get_db)):
    row = db.scalar(select(PlatformFeatureFlag).where(PlatformFeatureFlag.key == key))
    return {"key": key, "enabled": bool(row and row.enabled), "source": "server"}


@router.get("/platform/maintenance")
def maintenance(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return [serialize(row) for row in db.scalars(select(MaintenanceWindow).order_by(MaintenanceWindow.starts_at.desc()).limit(100)).all()]


@router.post("/platform/maintenance", status_code=201)
def create_maintenance(payload: MaintenanceIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if payload.ends_at <= payload.starts_at: raise HTTPException(422, "Maintenance end must be after start")
    row = MaintenanceWindow(created_by=user.id, **payload.model_dump()); db.add(row); db.commit(); db.refresh(row); return serialize(row)


@router.get("/platform/backups")
def backups(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return {"checks": [serialize(row) for row in db.scalars(select(PlatformBackupCheck).order_by(PlatformBackupCheck.created_at.desc()).limit(100)).all()], "restore_drills": [serialize(row) for row in db.scalars(select(RestoreDrill).order_by(RestoreDrill.created_at.desc()).limit(100)).all()], "readiness": "unknown_without_restore_evidence"}


@router.post("/platform/backups/checks", status_code=201)
def record_backup(payload: BackupIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = PlatformBackupCheck(**payload.model_dump()); db.add(row); db.commit(); db.refresh(row); return serialize(row)


@router.get("/platform/reviews")
def reviews(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return [serialize(row) for row in db.scalars(select(OperationalReview).order_by(OperationalReview.created_at.desc()).limit(100)).all()]


@router.post("/platform/reviews", status_code=201)
def create_review(payload: ReviewIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = OperationalReview(owner_id=user.id, **payload.model_dump()); db.add(row); db.commit(); db.refresh(row); return serialize(row)
