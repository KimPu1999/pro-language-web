import json
from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .auth import require_csrf, now, require_role
from .config import settings
from .db import get_db
from .models import (
    AIContentAuditLog, AIContentProject, AIContentQualityCheck, AIContentPublication,
    AIContentReviewDecision, AIContentReviewRequest, AIContentRevision,
    AIContentTranslation, AIGenerationJob, AILessonDraft, AIContentUsageRecord, User,
)
from .organization_routes import org_context

router = APIRouter(prefix="/api/v1", tags=["content-studio"])
CONTENT_MANAGERS = {"owner", "admin", "instructor"}
PLATFORM_ROLES = ("admin", "super_admin")


class ProjectIn(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    content_type: str = Field(pattern=r"^(course|curriculum|lesson|quiz|challenge|project|translation)$")
    metadata: dict = Field(default_factory=dict)


class GenerationIn(BaseModel):
    job_type: str = Field(pattern=r"^(course|curriculum|lesson|quiz|challenge|project|translation)$")
    inputs: dict = Field(default_factory=dict)
    idempotency_key: str = Field(min_length=8, max_length=180)


class RevisionIn(BaseModel):
    content_type: str = Field(min_length=2, max_length=40)
    snapshot: dict


class LessonDraftIn(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    content_en: str = Field(min_length=1, max_length=100000)
    content_mm: str | None = Field(default=None, max_length=100000)


class TranslationIn(BaseModel):
    source_type: str = Field(min_length=2, max_length=40)
    source_id: UUID
    language: str = Field(pattern=r"^(en|mm)$")
    content: str = Field(min_length=1, max_length=100000)


class ReviewDecisionIn(BaseModel):
    decision: str = Field(pattern=r"^(approved|rejected|changes_requested)$")
    comment: str = Field(default="", max_length=4000)


def audit(db, org, user, action, resource_type, resource_id=None, outcome="success"):
    db.add(AIContentAuditLog(organization_id=org.id if org else None, actor_id=user.id if user else None, action=action, resource_type=resource_type, resource_id=resource_id, outcome=outcome))


def project_for(ctx, project_id: UUID):
    org, member, user, db = ctx
    row = db.scalar(select(AIContentProject).where(AIContentProject.id == project_id, AIContentProject.organization_id == org.id))
    if not row: raise HTTPException(404, "Content project not found")
    if member.role not in CONTENT_MANAGERS and row.created_by != user.id: raise HTTPException(403, "Content project permission required")
    return org, member, user, db, row


@router.get("/organizations/{slug}/content-studio")
def studio_dashboard(ctx=Depends(org_context)):
    org, member, user, db = ctx
    if member.role not in CONTENT_MANAGERS: raise HTTPException(403, "Content authoring permission required")
    return {"metrics": {
        "draft_projects": db.scalar(select(func.count()).select_from(AIContentProject).where(AIContentProject.organization_id == org.id, AIContentProject.status == "draft")) or 0,
        "generation_jobs": db.scalar(select(func.count()).select_from(AIGenerationJob).where(AIGenerationJob.organization_id == org.id)) or 0,
        "pending_reviews": db.scalar(select(func.count()).select_from(AIContentReviewRequest).where(AIContentReviewRequest.project_id.in_(select(AIContentProject.id).where(AIContentProject.organization_id == org.id)), AIContentReviewRequest.status == "pending")) or 0,
        "published_revisions": db.scalar(select(func.count()).select_from(AIContentPublication).where(AIContentPublication.project_id.in_(select(AIContentProject.id).where(AIContentProject.organization_id == org.id)))) or 0,
    }, "ai": {"status": "configured" if settings.ai_enabled and settings.ai_provider != "disabled" else "Not Configured"}, "data_source": "postgresql"}


@router.get("/organizations/{slug}/content-studio/projects")
def projects(ctx=Depends(org_context), page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100)):
    org, member, user, db = ctx
    if member.role not in CONTENT_MANAGERS: raise HTTPException(403, "Content authoring permission required")
    rows = db.scalars(select(AIContentProject).where(AIContentProject.organization_id == org.id).order_by(AIContentProject.updated_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [{"id": r.id, "title": r.title, "content_type": r.content_type, "status": r.status, "created_by": r.created_by} for r in rows], "page": page, "page_size": page_size}


@router.post("/organizations/{slug}/content-studio/projects", status_code=201)
def create_project(payload: ProjectIn, ctx=Depends(org_context), _: None = Depends(require_csrf)):
    org, member, user, db = ctx
    if member.role not in CONTENT_MANAGERS: raise HTTPException(403, "Content authoring permission required")
    row = AIContentProject(organization_id=org.id, created_by=user.id, title=payload.title, content_type=payload.content_type, metadata_json=json.dumps(payload.metadata, sort_keys=True))
    db.add(row); audit(db, org, user, "content_project_created", "content_project", row.id); db.commit()
    return {"id": row.id, "status": row.status, "content_type": row.content_type}


@router.post("/organizations/{slug}/content-studio/projects/{project_id}/generate", status_code=202)
def generate(payload: GenerationIn, project_id: UUID, ctx=Depends(org_context), _: None = Depends(require_csrf)):
    org, member, user, db, project = project_for(ctx, project_id)
    if member.role not in CONTENT_MANAGERS: raise HTTPException(403, "Content authoring permission required")
    existing = db.scalar(select(AIGenerationJob).where(AIGenerationJob.organization_id == org.id, AIGenerationJob.idempotency_key == payload.idempotency_key))
    if existing: return {"id": existing.id, "status": existing.status, "idempotent": True, "provider": settings.ai_provider}
    status = "queued" if settings.ai_enabled and settings.ai_provider != "disabled" else "provider_unavailable"
    reason = None if status == "queued" else "AI provider is not configured; manual editing remains available."
    row = AIGenerationJob(organization_id=org.id, project_id=project.id, requested_by=user.id, job_type=payload.job_type, input_json=json.dumps(payload.inputs, sort_keys=True), status=status, idempotency_key=payload.idempotency_key, failure_reason=reason)
    db.add(row); audit(db, org, user, "content_generation_requested", "generation_job", row.id, "accepted" if status == "queued" else "provider_unavailable"); db.commit()
    return {"id": row.id, "status": row.status, "provider": settings.ai_provider, "message": reason or "Generation is queued for a configured worker."}


@router.get("/organizations/{slug}/content-studio/jobs")
def jobs(ctx=Depends(org_context)):
    org, member, user, db = ctx
    if member.role not in CONTENT_MANAGERS: raise HTTPException(403, "Content authoring permission required")
    rows = db.scalars(select(AIGenerationJob).where(AIGenerationJob.organization_id == org.id).order_by(AIGenerationJob.created_at.desc()).limit(100)).all()
    return [{"id": r.id, "project_id": r.project_id, "job_type": r.job_type, "status": r.status, "failure_reason": r.failure_reason} for r in rows]


@router.post("/organizations/{slug}/content-studio/projects/{project_id}/lessons", status_code=201)
def lesson_draft(payload: LessonDraftIn, project_id: UUID, ctx=Depends(org_context), _: None = Depends(require_csrf)):
    org, member, user, db, project = project_for(ctx, project_id)
    row = AILessonDraft(project_id=project.id, title=payload.title, content_en=payload.content_en, content_mm=payload.content_mm)
    db.add(row); project.status = "draft"; audit(db, org, user, "lesson_draft_saved", "lesson_draft", row.id); db.commit()
    return {"id": row.id, "status": row.status}


@router.post("/organizations/{slug}/content-studio/projects/{project_id}/translations", status_code=201)
def translation(payload: TranslationIn, project_id: UUID, ctx=Depends(org_context), _: None = Depends(require_csrf)):
    org, member, user, db, project = project_for(ctx, project_id)
    row = AIContentTranslation(project_id=project.id, source_type=payload.source_type, source_id=payload.source_id, language=payload.language, content=payload.content)
    db.add(row); audit(db, org, user, "content_translation_saved", "translation", row.id); db.commit()
    return {"id": row.id, "status": row.status, "language": row.language}


@router.post("/organizations/{slug}/content-studio/projects/{project_id}/revisions", status_code=201)
def revision(payload: RevisionIn, project_id: UUID, ctx=Depends(org_context), _: None = Depends(require_csrf)):
    org, member, user, db, project = project_for(ctx, project_id)
    latest = db.scalar(select(func.max(AIContentRevision.version_number)).where(AIContentRevision.project_id == project.id)) or 0
    row = AIContentRevision(project_id=project.id, version_number=latest + 1, content_type=payload.content_type, snapshot_json=json.dumps(payload.snapshot, sort_keys=True), created_by=user.id)
    db.add(row); audit(db, org, user, "content_revision_created", "revision", row.id); db.commit()
    return {"id": row.id, "version": row.version_number, "status": row.status}


@router.post("/organizations/{slug}/content-studio/projects/{project_id}/reviews", status_code=201)
def request_review(project_id: UUID, revision_id: UUID, ctx=Depends(org_context), _: None = Depends(require_csrf)):
    org, member, user, db, project = project_for(ctx, project_id)
    rev = db.scalar(select(AIContentRevision).where(AIContentRevision.id == revision_id, AIContentRevision.project_id == project.id, AIContentRevision.status == "draft"))
    if not rev: raise HTTPException(404, "Draft revision not found")
    row = AIContentReviewRequest(project_id=project.id, revision_id=rev.id, requested_by=user.id, expires_at=now() + timedelta(days=14))
    db.add(row); project.status = "in_review"; audit(db, org, user, "content_review_requested", "review", row.id); db.commit()
    return {"id": row.id, "status": row.status, "revision_id": row.revision_id}


@router.get("/organizations/{slug}/content-studio/reviews")
def reviews(ctx=Depends(org_context)):
    org, member, user, db = ctx
    if member.role not in CONTENT_MANAGERS: raise HTTPException(403, "Content review permission required")
    rows = db.scalars(select(AIContentReviewRequest).join(AIContentProject).where(AIContentProject.organization_id == org.id).order_by(AIContentReviewRequest.created_at.desc())).all()
    return [{"id": r.id, "project_id": r.project_id, "revision_id": r.revision_id, "requested_by": r.requested_by, "status": r.status} for r in rows]


@router.post("/organizations/{slug}/content-studio/reviews/{request_id}/decision")
def decide_review(payload: ReviewDecisionIn, request_id: UUID, ctx=Depends(org_context), _: None = Depends(require_csrf)):
    org, member, user, db = ctx
    if member.role not in {"owner", "admin", "instructor"}: raise HTTPException(403, "Content review permission required")
    row = db.scalar(select(AIContentReviewRequest).join(AIContentProject).where(AIContentReviewRequest.id == request_id, AIContentProject.organization_id == org.id))
    if not row: raise HTTPException(404, "Review request not found")
    if row.requested_by == user.id: raise HTTPException(403, "Independent review is required")
    if row.status != "pending" or (row.expires_at and row.expires_at <= now()): raise HTTPException(409, "Review is no longer actionable")
    row.reviewer_id = user.id; row.status = payload.decision; db.add(AIContentReviewDecision(request_id=row.id, reviewer_id=user.id, decision=payload.decision, comment=payload.comment))
    rev = db.get(AIContentRevision, row.revision_id); rev.status = "approved" if payload.decision == "approved" else payload.decision
    audit(db, org, user, "content_review_decided", "review", row.id); db.commit()
    return {"id": row.id, "status": row.status, "revision_status": rev.status}


@router.post("/organizations/{slug}/content-studio/projects/{project_id}/publish")
def publish(project_id: UUID, revision_id: UUID, ctx=Depends(org_context), _: None = Depends(require_csrf)):
    org, member, user, db, project = project_for(ctx, project_id)
    if member.role not in {"owner", "admin"}: raise HTTPException(403, "Administrator publishing permission required")
    revision = db.scalar(select(AIContentRevision).where(AIContentRevision.id == revision_id, AIContentRevision.project_id == project.id, AIContentRevision.status == "approved"))
    if not revision: raise HTTPException(409, "Only an approved revision can be published")
    if db.scalar(select(AIContentPublication).where(AIContentPublication.project_id == project.id, AIContentPublication.revision_id == revision.id)): return {"status": "published", "idempotent": True}
    row = AIContentPublication(project_id=project.id, revision_id=revision.id, published_by=user.id, status="published")
    db.add(row); project.status = "published"; audit(db, org, user, "content_revision_published", "publication", row.id); db.commit()
    return {"id": row.id, "status": row.status, "revision_id": revision.id}


@router.get("/organizations/{slug}/content-studio/quality")
def quality(ctx=Depends(org_context)):
    org, member, user, db = ctx
    if member.role not in CONTENT_MANAGERS: raise HTTPException(403, "Content quality permission required")
    rows = db.scalars(select(AIContentQualityCheck).join(AIContentProject).where(AIContentProject.organization_id == org.id).order_by(AIContentQualityCheck.created_at.desc()).limit(100)).all()
    return [{"id": r.id, "project_id": r.project_id, "check_type": r.check_type, "status": r.status, "details": r.details} for r in rows]


@router.get("/organizations/{slug}/content-studio/usage")
def usage(ctx=Depends(org_context)):
    org, member, user, db = ctx
    if member.role not in CONTENT_MANAGERS: raise HTTPException(403, "Content usage permission required")
    rows = db.scalars(select(AIContentUsageRecord).where(AIContentUsageRecord.organization_id == org.id).order_by(AIContentUsageRecord.created_at.desc()).limit(100)).all()
    return {"provider_status": "configured" if settings.ai_enabled and settings.ai_provider != "disabled" else "Not Configured", "items": [{"provider": r.provider, "input_tokens": r.input_tokens, "output_tokens": r.output_tokens, "estimated_cost": r.estimated_cost, "status": r.status} for r in rows]}


@router.get("/platform/content-studio")
def platform_content(user: User = Depends(require_role(*PLATFORM_ROLES)), db: Session = Depends(get_db)):
    return {"metrics": {"projects": db.scalar(select(func.count()).select_from(AIContentProject)) or 0, "jobs": db.scalar(select(func.count()).select_from(AIGenerationJob)) or 0, "pending_reviews": db.scalar(select(func.count()).select_from(AIContentReviewRequest).where(AIContentReviewRequest.status == "pending")) or 0, "quality_issues": db.scalar(select(func.count()).select_from(AIContentQualityCheck).where(AIContentQualityCheck.status == "FAIL")) or 0}, "ai_status": "configured" if settings.ai_enabled and settings.ai_provider != "disabled" else "Not Configured", "data_source": "postgresql"}
