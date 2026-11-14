"""Phase 27 cybersecurity education API.

Security labs are scoped to published, approved lab definitions and the
authenticated learner's owned records. Assessment accepts workspace IDs only;
it never accepts arbitrary URLs or external targets. Execution is delegated to
the existing isolated runner and fails closed when unavailable.
"""

import json
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .auth import current_user, require_csrf, verified_user
from .config import settings
from .db import get_db
from .models import (
    CybersecurityAuditLog,
    CybersecurityLabAttempt,
    CybersecurityLabDefinition,
    CybersecuritySecurityEvent,
    CybersecurityThreatModel,
    CybersecurityThreatModelVersion,
    IssuedCertificate,
    LearningLabWorkspace,
    User,
)
from .rbac import require_platform_admin

router = APIRouter(prefix="/api/v1/cybersecurity", tags=["cybersecurity"])


class LabIn(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    slug: str = Field(pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$", max_length=180)
    category: str = Field(default="secure_coding", max_length=60)
    difficulty: str = Field(default="beginner", max_length=30)
    language: str = Field(default="python", max_length=40)
    description_en: str = Field(min_length=1, max_length=10_000)
    description_mm: str | None = None
    objectives: list[str] = Field(default_factory=list, max_length=12)


class AttemptIn(BaseModel):
    workspace_id: UUID | None = None


class AssessmentIn(BaseModel):
    workspace_id: UUID
    evidence: str = Field(default="", max_length=5_000)


class ThreatModelIn(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    content: dict = Field(default_factory=dict)


def lab_view(row: CybersecurityLabDefinition) -> dict:
    return {"id": row.id, "title": row.title, "slug": row.slug, "category": row.category, "difficulty": row.difficulty, "language": row.language, "description_en": row.description_en, "description_mm": row.description_mm, "objectives": json.loads(row.objectives_json or "[]"), "mode": row.mode, "status": row.status}


@router.get("/dashboard")
def dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)):
    attempts = db.scalars(select(CybersecurityLabAttempt).where(CybersecurityLabAttempt.user_id == user.id).order_by(CybersecurityLabAttempt.updated_at.desc()).limit(20)).all()
    completed = sum(1 for row in attempts if row.verified)
    certificates = db.scalars(select(IssuedCertificate).where(IssuedCertificate.user_id == user.id, IssuedCertificate.revoked_at.is_(None)).order_by(IssuedCertificate.issued_at.desc()).limit(20)).all()
    return {"available_labs": db.scalar(select(func.count()).select_from(CybersecurityLabDefinition).where(CybersecurityLabDefinition.published.is_(True), CybersecurityLabDefinition.organization_id.is_(None))) or 0, "completed_labs": completed, "attempts": [{"id": row.id, "lab_id": row.lab_id, "status": row.status, "verified": row.verified, "score": row.score} for row in attempts], "security_skills": [], "certificates": [{"id": row.public_id, "title": row.title, "status": "valid"} for row in certificates], "data_source": "postgresql", "ai": {"status": "configured" if settings.ai_enabled else "not_configured"}}


@router.get("/paths")
def paths():
    return {"items": [{"slug": "security-fundamentals", "title": "Security Fundamentals", "description": "Core security concepts and safe engineering habits."}, {"slug": "web-application-security", "title": "Web Application Security", "description": "Defensive web security and OWASP-aligned practice."}, {"slug": "api-security", "title": "API Security", "description": "Authentication, authorization, validation, and safe API design."}, {"slug": "secure-software-engineering", "title": "Secure Software Engineering", "description": "Secure coding, review, testing, and remediation."}, {"slug": "defensive-security", "title": "Defensive Security Engineering", "description": "Logs, detections, triage, and incident reasoning."}], "source": "curated_catalog"}


@router.get("/paths/{slug}")
def path_detail(slug: str):
    rows = paths()["items"]
    row = next((item for item in rows if item["slug"] == slug), None)
    if not row:
        raise HTTPException(404, "Security learning path not found")
    return {**row, "labs": [], "status": "available_when_published_labs_exist"}


@router.get("/labs")
def labs(search: str | None = None, category: str | None = None, difficulty: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=50), db: Session = Depends(get_db)):
    query = select(CybersecurityLabDefinition).where(CybersecurityLabDefinition.published.is_(True), CybersecurityLabDefinition.organization_id.is_(None))
    count = select(func.count()).select_from(CybersecurityLabDefinition).where(CybersecurityLabDefinition.published.is_(True), CybersecurityLabDefinition.organization_id.is_(None))
    if search:
        query = query.where(CybersecurityLabDefinition.title.ilike(f"%{search}%")); count = count.where(CybersecurityLabDefinition.title.ilike(f"%{search}%"))
    if category:
        query = query.where(CybersecurityLabDefinition.category == category); count = count.where(CybersecurityLabDefinition.category == category)
    if difficulty:
        query = query.where(CybersecurityLabDefinition.difficulty == difficulty); count = count.where(CybersecurityLabDefinition.difficulty == difficulty)
    total = db.scalar(count) or 0
    return {"items": [lab_view(row) for row in db.scalars(query.order_by(CybersecurityLabDefinition.title).offset((page - 1) * page_size).limit(page_size)).all()], "page": page, "page_size": page_size, "total": total}


@router.get("/labs/{lab_id}")
def lab_detail(lab_id: UUID, db: Session = Depends(get_db)):
    row = db.scalar(select(CybersecurityLabDefinition).where(CybersecurityLabDefinition.id == lab_id, CybersecurityLabDefinition.published.is_(True), CybersecurityLabDefinition.organization_id.is_(None)))
    if not row:
        raise HTTPException(404, "Security lab not found")
    return {**lab_view(row), "evaluation": {"mode": "isolated_runner" if settings.runner_enabled else "not_configured", "score_source": "server_only"}}


@router.post("/labs/{lab_id}/attempts", status_code=201)
def start_attempt(lab_id: UUID, payload: AttemptIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    lab = db.scalar(select(CybersecurityLabDefinition).where(CybersecurityLabDefinition.id == lab_id, CybersecurityLabDefinition.published.is_(True), CybersecurityLabDefinition.organization_id.is_(None)))
    if not lab:
        raise HTTPException(404, "Security lab not found")
    if payload.workspace_id and not db.scalar(select(LearningLabWorkspace.id).where(LearningLabWorkspace.id == payload.workspace_id, LearningLabWorkspace.user_id == user.id)):
        raise HTTPException(404, "Owned lab workspace required")
    attempt = CybersecurityLabAttempt(lab_id=lab.id, user_id=user.id, workspace_id=payload.workspace_id)
    db.add(attempt); db.add(CybersecurityAuditLog(actor_id=user.id, action="security_lab_attempt_started", resource_type="lab_attempt", resource_id=attempt.id)); db.commit()
    return {"id": attempt.id, "status": attempt.status, "verified": False}


@router.post("/attempts/{attempt_id}/evaluate", status_code=202)
def evaluate(attempt_id: UUID, payload: AssessmentIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    attempt = db.scalar(select(CybersecurityLabAttempt).where(CybersecurityLabAttempt.id == attempt_id, CybersecurityLabAttempt.user_id == user.id))
    if not attempt:
        raise HTTPException(404, "Security lab attempt not found")
    if not attempt.workspace_id or not payload.workspace_id:
        raise HTTPException(422, "An owned lab workspace is required for evaluation")
    if payload.workspace_id != attempt.workspace_id:
        raise HTTPException(403, "Attempt workspace mismatch")
    if not settings.runner_enabled:
        attempt.status = "runner_unavailable"; db.commit()
        return {"id": attempt.id, "status": attempt.status, "verified": False, "message": "No security code was executed; the isolated runner is not configured."}
    attempt.status = "queued"; db.commit()
    # Queue metadata only. The external worker must perform hidden tests in
    # its own sandbox and write a verified result; this API never grades code.
    return {"id": attempt.id, "status": attempt.status, "verified": False, "message": "Evaluation queued for the isolated runner."}


@router.post("/assessment/targets")
def assessment_target(payload: AssessmentIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if not db.scalar(select(LearningLabWorkspace.id).where(LearningLabWorkspace.id == payload.workspace_id, LearningLabWorkspace.user_id == user.id)):
        raise HTTPException(403, "Only an owned lab workspace may be assessed")
    return {"status": "approved_lab_target", "workspace_id": payload.workspace_id, "external_targets": False, "network_mode": "isolated"}


@router.get("/threat-models")
def threat_models(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return {"items": [{"id": row.id, "title": row.title, "status": row.status, "current_version": row.current_version} for row in db.scalars(select(CybersecurityThreatModel).where(CybersecurityThreatModel.owner_id == user.id).order_by(CybersecurityThreatModel.updated_at.desc())).all()]}


@router.post("/threat-models", status_code=201)
def create_threat_model(payload: ThreatModelIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if len(json.dumps(payload.content, separators=(",", ":"))) > 100_000:
        raise HTTPException(413, "Threat model content is too large")
    model = CybersecurityThreatModel(owner_id=user.id, title=payload.title, current_version=1); db.add(model); db.flush(); db.add(CybersecurityThreatModelVersion(threat_model_id=model.id, created_by=user.id, version_number=1, content_json=json.dumps(payload.content))); db.add(CybersecurityAuditLog(actor_id=user.id, action="threat_model_created", resource_type="threat_model", resource_id=model.id)); db.commit(); return {"id": model.id, "status": model.status, "version": 1}


@router.get("/ai-tutor/status")
def ai_status(user: User = Depends(current_user)):
    return {"enabled": settings.ai_enabled, "provider": settings.ai_provider if settings.ai_enabled else "disabled", "scope": "security-lab-context-only", "automatic_scoring": False}


@router.get("/platform/operations")
def platform_operations(user: User = Depends(require_platform_admin), db: Session = Depends(get_db)):
    return {"labs": db.scalar(select(func.count()).select_from(CybersecurityLabDefinition)) or 0, "attempts": db.scalar(select(func.count()).select_from(CybersecurityLabAttempt)) or 0, "security_events": db.scalar(select(func.count()).select_from(CybersecuritySecurityEvent)) or 0, "runner": "configured" if settings.runner_enabled else "not_configured", "external_scanning": False, "public_vulnerable_targets": False, "data_source": "postgresql"}


@router.get("/instructor/labs")
def instructor_labs(user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role not in {"instructor", "admin", "platform_admin", "super_admin"}:
        raise HTTPException(403, "Instructor permission required")
    return [lab_view(row) for row in db.scalars(select(CybersecurityLabDefinition).where(CybersecurityLabDefinition.created_by == user.id).order_by(CybersecurityLabDefinition.updated_at.desc())).all()]


@router.post("/instructor/labs", status_code=201)
def instructor_create_lab(payload: LabIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if user.role not in {"instructor", "admin", "platform_admin", "super_admin"}:
        raise HTTPException(403, "Instructor permission required")
    if db.scalar(select(CybersecurityLabDefinition).where(CybersecurityLabDefinition.organization_id.is_(None), CybersecurityLabDefinition.slug == payload.slug)):
        raise HTTPException(409, "Security lab slug already exists")
    row = CybersecurityLabDefinition(created_by=user.id, title=payload.title, slug=payload.slug, category=payload.category, difficulty=payload.difficulty, language=payload.language, description_en=payload.description_en, description_mm=payload.description_mm, objectives_json=json.dumps(payload.objectives)); db.add(row); db.add(CybersecurityAuditLog(actor_id=user.id, action="security_lab_created", resource_type="lab", resource_id=row.id)); db.commit(); return {"id": row.id, "status": row.status, "published": row.published}
