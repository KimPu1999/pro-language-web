"""Phase 26 cloud-lab facade over the existing isolated learning-lab service.

This module deliberately exposes simulation status for Docker, CI/CD,
Kubernetes, and deployment practice. It never executes student commands in
the API process and never talks to a host Docker socket or cluster-admin API.
"""

import json
import re
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .auth import current_user, now, require_csrf, verified_user
from .config import settings
from .db import get_db
from .models import (
    LearningLab,
    LearningLabAuditLog,
    LearningLabProgress,
    LearningLabRun,
    LearningLabSnapshot,
    LearningLabVersion,
    LearningLabWorkspace,
    LearningLabWorkspaceFile,
    User,
)
from .rbac import require_platform_admin

router = APIRouter(prefix="/api/v1/cloud-labs", tags=["cloud labs"])
SAFE_PATH = re.compile(r"^[A-Za-z0-9_./-]+$")
ACTIVE_STATUSES = {"in_progress", "running", "suspended", "stopped"}
TRANSITIONS = {
    "start": {"in_progress", "stopped", "suspended"},
    "stop": {"in_progress", "running", "suspended"},
    "suspend": {"in_progress", "running"},
    "resume": {"suspended", "stopped"},
    "delete": ACTIVE_STATUSES,
}


class WorkspaceFileIn(BaseModel):
    path: str = Field(min_length=1, max_length=240)
    source_code: str = Field(max_length=100_000)
    language: str = Field(min_length=1, max_length=40)


class LifecycleIn(BaseModel):
    action: str = Field(pattern="^(start|stop|suspend|resume|delete)$")


def owned_workspace(db: Session, workspace_id: UUID, user: User) -> LearningLabWorkspace:
    row = db.scalar(
        select(LearningLabWorkspace).where(
            LearningLabWorkspace.id == workspace_id,
            LearningLabWorkspace.user_id == user.id,
        )
    )
    if not row:
        raise HTTPException(404, "Workspace not found")
    return row


def workspace_view(db: Session, row: LearningLabWorkspace) -> dict:
    files = db.scalars(
        select(LearningLabWorkspaceFile)
        .where(LearningLabWorkspaceFile.workspace_id == row.id)
        .order_by(LearningLabWorkspaceFile.path)
    ).all()
    used_bytes = sum(len((item.source_code or "").encode()) for item in files)
    return {
        "id": row.id,
        "lab_id": row.lab_id,
        "status": row.status,
        "files": [
            {"id": item.id, "path": item.path, "language": item.language, "source_code": item.source_code}
            for item in files
        ],
        "quota": {"storage_bytes": used_bytes, "storage_limit_bytes": 5_000_000, "max_runtime_minutes": 30},
        "execution": {
            "mode": "isolated_runner" if settings.runner_enabled else "simulation",
            "status": "configured" if settings.runner_enabled else "not_configured",
            "detail": "Commands are queued for a separately isolated runner."
            if settings.runner_enabled
            else "No student command was executed; the isolated runner is not configured.",
        },
    }


@router.get("/catalog")
def cloud_catalog(
    search: str | None = None,
    category: str | None = None,
    difficulty: str | None = None,
    technology: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
):
    query = select(LearningLab).where(LearningLab.published.is_(True), LearningLab.organization_id.is_(None))
    count_query = select(func.count()).select_from(LearningLab).where(LearningLab.published.is_(True), LearningLab.organization_id.is_(None))
    if search:
        query = query.where(LearningLab.title.ilike(f"%{search}%"))
    if category:
        query = query.where(LearningLab.category == category)
    if difficulty:
        query = query.where(LearningLab.difficulty == difficulty)
    if technology:
        query = query.where(LearningLab.language == technology)
    if search:
        count_query = count_query.where(LearningLab.title.ilike(f"%{search}%"))
    if category:
        count_query = count_query.where(LearningLab.category == category)
    if difficulty:
        count_query = count_query.where(LearningLab.difficulty == difficulty)
    if technology:
        count_query = count_query.where(LearningLab.language == technology)
    total = db.scalar(count_query) or 0
    rows = db.scalars(query.order_by(LearningLab.title).offset((page - 1) * page_size).limit(page_size)).all()
    return {
        "items": [
            {"id": row.id, "title": row.title, "slug": row.slug, "description_en": row.description_en,
             "description_mm": row.description_mm, "category": row.category, "difficulty": row.difficulty,
             "technology": row.language, "estimated_minutes": row.estimated_minutes,
             "execution_mode": "isolated_runner" if settings.runner_enabled else "simulation"}
            for row in rows
        ],
        "page": page,
        "page_size": page_size,
        "total": total,
    }


@router.get("/modes")
def lab_modes():
    return {
        "git": {"mode": "isolated_workspace", "available": True},
        "github": {"mode": "integration" if settings.github_enabled else "simulation", "available": settings.github_enabled},
        "docker": {"mode": "simulation", "available": True, "host_socket_exposed": False, "privileged_execution": False},
        "cicd": {"mode": "simulation", "available": True, "untrusted_pipeline_execution": False},
        "kubernetes": {"mode": "simulation", "available": True, "cluster_admin_exposed": False},
        "deployment": {"mode": "simulation", "available": True, "public_previews": False},
        "ai": {"mode": "provider" if settings.ai_enabled else "unavailable", "available": settings.ai_enabled},
    }


@router.get("/platform/operations")
def cloud_operations(user: User = Depends(require_platform_admin), db: Session = Depends(get_db)):
    return {
        "workspace_count": db.scalar(select(func.count()).select_from(LearningLabWorkspace)) or 0,
        "failed_runs": db.scalar(select(func.count()).select_from(LearningLabRun).where(LearningLabRun.status.in_(["failed", "runner_unavailable"]))) or 0,
        "runner": {"status": "configured" if settings.runner_enabled else "not_configured", "host_socket_exposed": False},
        "security": {"docker_mode": "simulation", "kubernetes_mode": "simulation", "public_previews": False},
        "data_source": "postgresql",
    }


@router.get("/{lab_id}")
def cloud_lab_detail(lab_id: UUID, db: Session = Depends(get_db)):
    row = db.scalar(select(LearningLab).where(LearningLab.id == lab_id, LearningLab.published.is_(True), LearningLab.organization_id.is_(None)))
    if not row:
        raise HTTPException(404, "Cloud lab not found")
    return {"id": row.id, "title": row.title, "slug": row.slug, "description_en": row.description_en, "description_mm": row.description_mm, "category": row.category, "difficulty": row.difficulty, "technology": row.language, "estimated_minutes": row.estimated_minutes, "objectives": ["Complete the guided task", "Validate the result server-side"], "execution_mode": "isolated_runner" if settings.runner_enabled else "simulation"}


@router.post("/{lab_id}/workspaces", status_code=201)
def create_cloud_workspace(lab_id: UUID, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    lab = db.scalar(select(LearningLab).where(LearningLab.id == lab_id, LearningLab.published.is_(True), LearningLab.organization_id.is_(None)))
    if not lab:
        raise HTTPException(404, "Cloud lab not found")
    existing = db.scalar(select(LearningLabWorkspace).where(LearningLabWorkspace.lab_id == lab.id, LearningLabWorkspace.user_id == user.id, LearningLabWorkspace.status != "deleted"))
    if existing:
        return {"id": existing.id, "status": existing.status, "idempotent": True}
    version = db.scalar(select(LearningLabVersion).where(LearningLabVersion.lab_id == lab.id, LearningLabVersion.status == "published").order_by(LearningLabVersion.version_number.desc()))
    if not version:
        raise HTTPException(409, "This lab has no published version")
    row = LearningLabWorkspace(lab_id=lab.id, user_id=user.id, version_id=version.id)
    db.add(row)
    db.add(LearningLabProgress(lab_id=lab.id, user_id=user.id, started=True))
    db.add(LearningLabAuditLog(actor_id=user.id, action="cloud_workspace_created", resource_id=row.id))
    db.commit()
    return {"id": row.id, "status": row.status}


@router.get("/dashboard")
def cloud_dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)):
    workspaces = db.scalars(
        select(LearningLabWorkspace)
        .where(LearningLabWorkspace.user_id == user.id)
        .order_by(LearningLabWorkspace.updated_at.desc())
        .limit(20)
    ).all()
    progress = db.scalars(select(LearningLabProgress).where(LearningLabProgress.user_id == user.id)).all()
    return {
        "active_workspaces": [workspace_view(db, row) for row in workspaces if row.status in ACTIVE_STATUSES],
        "recent_workspaces": [workspace_view(db, row) for row in workspaces],
        "completed_labs": sum(1 for item in progress if item.completed),
        "progress": {"started": sum(1 for item in progress if item.started), "completed": sum(1 for item in progress if item.completed)},
        "resource_usage": {"workspace_count": len(workspaces), "storage_bytes": sum(workspace_view(db, item)["quota"]["storage_bytes"] for item in workspaces)},
        "execution_mode": "isolated_runner" if settings.runner_enabled else "simulation",
    }


@router.get("/workspaces/{workspace_id}")
def get_cloud_workspace(workspace_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    return workspace_view(db, owned_workspace(db, workspace_id, user))


@router.patch("/workspaces/{workspace_id}/lifecycle")
def lifecycle(workspace_id: UUID, payload: LifecycleIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = owned_workspace(db, workspace_id, user)
    if row.status not in TRANSITIONS[payload.action]:
        raise HTTPException(409, f"Cannot {payload.action} a workspace in {row.status} state")
    if payload.action == "delete":
        row.status = "deleted"
    elif payload.action == "start" or payload.action == "resume":
        row.status = "running"
    elif payload.action == "stop":
        row.status = "stopped"
    else:
        row.status = "suspended"
    db.add(LearningLabAuditLog(actor_id=user.id, action=f"workspace_{payload.action}", resource_id=row.id))
    db.commit()
    return {"id": row.id, "status": row.status, "execution_mode": "isolated_runner" if settings.runner_enabled else "simulation"}


@router.put("/workspaces/{workspace_id}/files")
def save_cloud_file(workspace_id: UUID, payload: WorkspaceFileIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = owned_workspace(db, workspace_id, user)
    if not SAFE_PATH.fullmatch(payload.path) or payload.path.startswith("/") or ".." in payload.path.split("/"):
        raise HTTPException(422, "Unsafe file path")
    existing = db.scalar(select(LearningLabWorkspaceFile).where(LearningLabWorkspaceFile.workspace_id == row.id, LearningLabWorkspaceFile.path == payload.path))
    if not existing:
        existing = LearningLabWorkspaceFile(workspace_id=row.id, **payload.model_dump())
        db.add(existing)
    else:
        existing.source_code = payload.source_code
        existing.language = payload.language
    used = sum(len((item.source_code or "").encode()) for item in db.scalars(select(LearningLabWorkspaceFile).where(LearningLabWorkspaceFile.workspace_id == row.id)).all()) + len(payload.source_code.encode())
    if used > 5_000_000:
        db.rollback()
        raise HTTPException(413, "Workspace storage quota exceeded")
    db.commit()
    return {"id": existing.id, "path": existing.path, "status": "saved"}


@router.post("/workspaces/{workspace_id}/snapshots", status_code=201)
def create_snapshot(workspace_id: UUID, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = owned_workspace(db, workspace_id, user)
    files = db.scalars(select(LearningLabWorkspaceFile).where(LearningLabWorkspaceFile.workspace_id == row.id)).all()
    snapshot = LearningLabSnapshot(workspace_id=row.id, created_by=user.id, files_json=json.dumps([{"path": item.path, "language": item.language, "source_code": item.source_code} for item in files]))
    db.add(snapshot)
    db.add(LearningLabAuditLog(actor_id=user.id, action="workspace_snapshot_created", resource_id=row.id))
    db.commit()
    return {"id": snapshot.id, "status": "saved", "file_count": len(files)}


