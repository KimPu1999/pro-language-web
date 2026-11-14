"""Phase 32 capacity and scalability evidence APIs.

These endpoints record measurements and policies; they never scale paid
infrastructure directly. Any real autoscaler must be a separately authorized
deployment integration.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from .admin_routes import full_admin
from .auth import require_csrf
from .config import settings
from .db import get_db
from .models import (
    PlatformAICapacityMetric, PlatformCdnMetric, PlatformCostRecord,
    PlatformDatabasePerformance, PlatformFailoverEvent, PlatformQueueMetric,
    PlatformRecoveryDrill, PlatformRunnerCapacity, PlatformScalingEvent,
    PlatformScalingPolicy, PlatformScalabilityAuditLog, User,
)

router = APIRouter(prefix="/api/v1/platform/scalability", tags=["scalability"])


class SnapshotIn(BaseModel):
    service: str = Field(min_length=2, max_length=80)
    metric: str = Field(min_length=2, max_length=80)
    value: float
    unit: str = Field(min_length=1, max_length=30)
    source: str = Field(min_length=2, max_length=120)


class PolicyIn(BaseModel):
    service: str = Field(min_length=2, max_length=80)
    min_capacity: int = Field(ge=0, le=100000)
    max_capacity: int = Field(ge=0, le=100000)
    scale_out_threshold: float = Field(ge=0)
    scale_in_threshold: float = Field(ge=0)
    cooldown_seconds: int = Field(ge=30, le=86400)
    enabled: bool = False
    approval_required: bool = True


class ScalingEventIn(BaseModel):
    service: str = Field(min_length=2, max_length=80)
    action: str = Field(pattern="^(scale_out|scale_in|pause|resume)$")
    requested_capacity: int | None = Field(default=None, ge=0, le=100000)
    reason: str = Field(min_length=3, max_length=2000)


class RecoveryIn(BaseModel):
    scenario: str = Field(min_length=3, max_length=120)
    status: str = Field(pattern="^(planned|passed|failed|not_tested)$")
    rpo_minutes: int | None = Field(default=None, ge=0)
    rto_minutes: int | None = Field(default=None, ge=0)
    evidence_ref: str = Field(default="", max_length=500)


def serialize(row):
    return {key: getattr(row, key) for key in row.__table__.columns.keys()}


def audit(db: Session, user: User, action: str, entity_type: str, entity_id):
    db.add(PlatformScalabilityAuditLog(actor_id=user.id, action=action, entity_type=entity_type, entity_id=entity_id))


@router.get("")
def scalability_dashboard(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return {
        "telemetry": "not_configured",
        "measurement_source": "persisted_evidence_only",
        "api": {"instances": "not_tested", "pool_size": settings.db_pool_size, "pool_max_overflow": settings.db_max_overflow, "health_checks": "available"},
        "database": {"read_replicas": "not_configured", "pool_pre_ping": True, "query_metrics": "not_tested"},
        "redis": {"status": "not_tested", "url_configured": bool(settings.redis_url), "queue": settings.runner_queue_name},
        "runner": {"status": "configured" if settings.runner_enabled else "not_configured", "capacity": "not_tested"},
        "ai": {"status": "configured" if settings.ai_enabled and settings.ai_provider != "disabled" else "not_configured", "capacity": "not_tested"},
        "cdn": {"status": "not_configured", "cache_metrics": "not_tested"},
        "costs": "not_configured",
        "policies": db.query(PlatformScalingPolicy).count(),
    }


@router.get("/database")
def database_performance(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return {"status": "measured" if db.query(PlatformDatabasePerformance).count() else "not_tested", "items": [serialize(row) for row in db.scalars(select(PlatformDatabasePerformance).order_by(PlatformDatabasePerformance.observed_at.desc()).limit(100)).all()], "read_replicas": "not_configured"}


@router.get("/workers")
def worker_metrics(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return {"status": "measured" if db.query(PlatformQueueMetric).count() else "not_tested", "items": [serialize(row) for row in db.scalars(select(PlatformQueueMetric).order_by(PlatformQueueMetric.observed_at.desc()).limit(100)).all()], "redis_scaling": "not_tested"}


@router.get("/runners")
def runner_capacity(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return {"status": "measured" if db.query(PlatformRunnerCapacity).count() else "not_tested", "items": [serialize(row) for row in db.scalars(select(PlatformRunnerCapacity).order_by(PlatformRunnerCapacity.observed_at.desc()).limit(100)).all()], "host_socket_exposed": False, "autoscaling": "policy_only"}


@router.get("/cdn")
def cdn_metrics(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return {"status": "measured" if db.query(PlatformCdnMetric).count() else "not_configured", "items": [serialize(row) for row in db.scalars(select(PlatformCdnMetric).order_by(PlatformCdnMetric.observed_at.desc()).limit(100)).all()], "private_content_cache": False}


@router.get("/ai")
def ai_capacity(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return {"status": "measured" if db.query(PlatformAICapacityMetric).count() else "not_configured", "items": [serialize(row) for row in db.scalars(select(PlatformAICapacityMetric).order_by(PlatformAICapacityMetric.observed_at.desc()).limit(100)).all()], "provider": settings.ai_provider if settings.ai_enabled else "disabled", "admission_control": "provider_gated"}


@router.get("/costs")
def costs(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return {"status": "measured" if db.query(PlatformCostRecord).count() else "not_configured", "actuals": [serialize(row) for row in db.scalars(select(PlatformCostRecord).where(PlatformCostRecord.cost_type == "actual").order_by(PlatformCostRecord.created_at.desc()).limit(100)).all()], "estimates": [serialize(row) for row in db.scalars(select(PlatformCostRecord).where(PlatformCostRecord.cost_type == "estimate").order_by(PlatformCostRecord.created_at.desc()).limit(100)).all()]}


@router.get("/policies")
def policies(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return [serialize(row) for row in db.scalars(select(PlatformScalingPolicy).order_by(PlatformScalingPolicy.service)).all()]


@router.post("/policies", status_code=201)
def create_policy(payload: PolicyIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if payload.max_capacity < payload.min_capacity: raise HTTPException(422, "Maximum capacity must be at least minimum capacity")
    if db.scalar(select(PlatformScalingPolicy).where(PlatformScalingPolicy.service == payload.service)): raise HTTPException(409, "Scaling policy already exists")
    values = payload.model_dump()
    values.update(approval_required=True, enabled=False)
    row = PlatformScalingPolicy(**values); db.add(row); db.flush(); audit(db, user, "policy_created", "scaling_policy", row.id); db.commit(); db.refresh(row); return serialize(row)


@router.get("/events")
def scaling_events(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return [serialize(row) for row in db.scalars(select(PlatformScalingEvent).order_by(PlatformScalingEvent.created_at.desc()).limit(100)).all()]


@router.post("/events", status_code=202)
def create_scaling_event(payload: ScalingEventIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = PlatformScalingEvent(service=payload.service, action=payload.action, requested_capacity=payload.requested_capacity, reason=payload.reason, actor_id=user.id, status="planned")
    db.add(row); db.flush(); audit(db, user, "event_recorded", "scaling_event", row.id); db.commit(); db.refresh(row); return {**serialize(row), "message": "Recorded as planned; no infrastructure was changed."}


@router.get("/recovery")
def recovery(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return {"status": "measured" if db.query(PlatformRecoveryDrill).count() else "not_tested", "drills": [serialize(row) for row in db.scalars(select(PlatformRecoveryDrill).order_by(PlatformRecoveryDrill.created_at.desc()).limit(100)).all()], "failover_events": [serialize(row) for row in db.scalars(select(PlatformFailoverEvent).order_by(PlatformFailoverEvent.created_at.desc()).limit(100)).all()]}


@router.post("/recovery", status_code=201)
def record_recovery(payload: RecoveryIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = PlatformRecoveryDrill(**payload.model_dump()); db.add(row); db.flush(); audit(db, user, "recovery_recorded", "recovery_drill", row.id); db.commit(); db.refresh(row); return serialize(row)

