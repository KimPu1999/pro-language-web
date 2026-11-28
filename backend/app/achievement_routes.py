"""Public and admin APIs for verified learning achievements."""

import json
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .achievement_service import ALLOWED_RULE_TYPES, award_payload, award_verified_achievements, definition_payload, evaluate_definition
from .admin_routes import audit, full_admin
from .auth import check_rate_limit, current_user, require_csrf
from .db import get_db
from .models import AchievementAuditEvent, AchievementDefinition, AchievementRuleVersion, AchievementAwardEvidence, StudentAchievement, User

router = APIRouter(prefix="/api/v1", tags=["verified achievements"])


class AchievementIn(BaseModel):
    code: str = Field(min_length=3, max_length=100, pattern=r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
    title: str = Field(min_length=2, max_length=160)
    title_mm: str | None = Field(default=None, max_length=160)
    description: str = Field(min_length=1, max_length=10000)
    description_mm: str | None = Field(default=None, max_length=10000)
    criteria: str = Field(default="", max_length=10000)
    criteria_mm: str | None = Field(default=None, max_length=10000)
    category: str = Field(default="learning", pattern=r"^(learning|course|quiz|project|path|capstone)$")
    rule_type: str = Field(pattern=r"^(lesson_completion_count|course_verified_completion|quiz_passed|approved_project_count|learning_path_completion|capstone_approved)$")
    rule: dict = Field(default_factory=dict)
    badge_image_url: str | None = Field(default=None, max_length=500)
    icon_name: str = Field(default="Award", max_length=50, pattern=r"^[A-Za-z0-9-]+$")
    tier: str = Field(default="standard", pattern=r"^(standard|bronze|silver|gold|platinum)$")
    related_course_id: UUID | None = None
    related_path_id: UUID | None = None
    threshold: int = Field(default=1, ge=1, le=100000)
    display_order: int = Field(default=0, ge=0, le=100000)
    visibility: str = Field(default="public", pattern=r"^(public|private)$")


def _definition(db: Session, value: str) -> AchievementDefinition | None:
    try:
        parsed = UUID(value)
        return db.get(AchievementDefinition, parsed)
    except (ValueError, TypeError):
        return db.scalar(select(AchievementDefinition).where(AchievementDefinition.slug == value))


def _validate_rule(payload: AchievementIn):
    if payload.rule_type not in ALLOWED_RULE_TYPES:
        raise HTTPException(422, "Unsupported achievement rule")
    if not isinstance(payload.rule, dict):
        raise HTTPException(422, "Achievement rule must be an object")
    if payload.badge_image_url and (not payload.badge_image_url.startswith("/") or payload.badge_image_url.startswith("//") or not payload.badge_image_url.lower().split("?", 1)[0].endswith((".png", ".jpg", ".jpeg", ".webp"))):
        raise HTTPException(422, "Badge images must be approved internal PNG, JPEG, or WebP assets")
    for key in ("course_id", "path_id", "lesson_id", "project_id"):
        if key in payload.rule:
            try:
                UUID(str(payload.rule[key]))
            except (TypeError, ValueError):
                raise HTTPException(422, f"Invalid rule reference: {key}")


def _award_summary(db: Session, award: StudentAchievement):
    definition = db.get(AchievementDefinition, award.achievement_id)
    user = db.get(User, award.user_id)
    return {
        "award_id": str(award.public_id),
        "status": "revoked" if award.revoked_at or award.status == "revoked" else award.status,
        "awarded_at": award.awarded_at,
        "criteria_version": award.criteria_version,
        "student": {"id": str(user.id), "display_name": user.display_name} if user else None,
        "achievement": definition_payload(definition) if definition else None,
    }


@router.get("/me/achievements")
def my_achievements(locale: str = Query("en", pattern="^(en|my)$"), user: User = Depends(current_user), db: Session = Depends(get_db)):
    definitions = db.scalars(select(AchievementDefinition).where(AchievementDefinition.status == "published", AchievementDefinition.visibility == "public").order_by(AchievementDefinition.display_order, AchievementDefinition.created_at)).all()
    awards = db.scalars(select(StudentAchievement).where(StudentAchievement.user_id == user.id).order_by(StudentAchievement.awarded_at.desc())).all()
    award_by_definition = {award.achievement_id: award for award in awards}
    items = []
    in_progress = 0
    eligible = 0
    for definition in definitions:
        award = award_by_definition.get(definition.id)
        if award:
            state = "revoked" if award.revoked_at or award.status == "revoked" else "earned"
            progress = {"current": 1, "target": 1, "available": True}
        else:
            progress = evaluate_definition(db, user.id, definition)
            current = progress.get("current")
            target = progress.get("target", 1)
            if not progress.get("available"):
                state = "unavailable"
            elif current is None or current == 0:
                state = "not_started"
            elif current >= target:
                state = "eligible"
                eligible += 1
            else:
                state = "in_progress"
                in_progress += 1
        items.append({**definition_payload(definition, locale), "state": state, "progress": {"current": progress.get("current"), "target": progress.get("target"), "remaining": max(0, progress.get("target", 1) - (progress.get("current") or 0)) if progress.get("current") is not None else None, "available": progress.get("available", True), "unavailable_reason": progress.get("unavailable_reason")}, "award": award_payload(db, award, locale, include_evidence=True) if award else None})
    earned = [award_payload(db, award, locale, include_evidence=True) for award in awards if award.status == "active" and not award.revoked_at]
    return {"metrics": {"published_definitions": len(definitions), "earned_badges": len(earned), "eligible_badges": eligible, "in_progress_badges": in_progress, "recent_awards": earned[:5]}, "items": items, "source": "verified_platform_records"}


@router.get("/achievements")
def public_achievements(locale: str = Query("en", pattern="^(en|my)$"), db: Session = Depends(get_db)):
    rows = db.scalars(select(AchievementDefinition).where(AchievementDefinition.status == "published", AchievementDefinition.visibility == "public").order_by(AchievementDefinition.display_order, AchievementDefinition.created_at)).all()
    return {"items": [definition_payload(row, locale) for row in rows], "source": "published_achievement_definitions"}


@router.get("/achievements/verify/{public_id}")
def verify_achievement(public_id: str, db: Session = Depends(get_db)):
    check_rate_limit(f"achievement-verify:{public_id}", 30, 60)
    award = db.scalar(select(StudentAchievement).where(StudentAchievement.public_id == public_id))
    if not award:
        return {"status": "not_found", "award_id": public_id}
    definition = db.get(AchievementDefinition, award.achievement_id)
    if not definition or definition.status not in {"published", "archived"}:
        return {"status": "not_found", "award_id": public_id}
    return {"status": "revoked" if award.revoked_at or award.status == "revoked" else "valid", "award_id": award.public_id, "title": definition.title, "issuer": "Learn-Coding", "awarded_at": award.awarded_at, "criteria_version": award.criteria_version}


@router.get("/achievements/{achievement_id}")
def achievement_detail(achievement_id: str, locale: str = Query("en", pattern="^(en|my)$"), db: Session = Depends(get_db)):
    row = _definition(db, achievement_id)
    if not row or row.status != "published" or row.visibility != "public":
        raise HTTPException(404, "Published achievement not found")
    return definition_payload(row, locale)


@router.get("/admin/achievements")
def admin_achievements(status: str = Query("all", pattern="^(all|draft|in_review|approved|published|archived)$"), search: str = Query("", max_length=100), page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100), user: User = Depends(full_admin), db: Session = Depends(get_db)):
    query = select(AchievementDefinition).order_by(AchievementDefinition.display_order, AchievementDefinition.created_at.desc())
    count_query = select(func.count()).select_from(AchievementDefinition)
    if status != "all":
        query = query.where(AchievementDefinition.status == status)
        count_query = count_query.where(AchievementDefinition.status == status)
    if search.strip():
        pattern = f"%{search.strip()}%"
        condition = AchievementDefinition.title.ilike(pattern) | AchievementDefinition.slug.ilike(pattern)
        query = query.where(condition)
        count_query = count_query.where(condition)
    total = db.scalar(count_query) or 0
    rows = db.scalars(query.offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [definition_payload(row, include_private=True) for row in rows], "page": page, "page_size": page_size, "total": total}


@router.get("/admin/achievement-awards")
def admin_awards(search: str = Query("", max_length=100), status: str = Query("all", pattern="^(all|active|revoked)$"), page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100), user: User = Depends(full_admin), db: Session = Depends(get_db)):
    query = select(StudentAchievement).order_by(StudentAchievement.awarded_at.desc())
    if status != "all":
        query = query.where(StudentAchievement.status == status)
    rows = db.scalars(query.offset((page - 1) * page_size).limit(page_size)).all()
    if search.strip():
        needle = search.strip().lower()
        rows = [row for row in rows if (db.get(User, row.user_id) and needle in db.get(User, row.user_id).display_name.lower()) or (db.get(AchievementDefinition, row.achievement_id) and needle in db.get(AchievementDefinition, row.achievement_id).title.lower())]
    return {"items": [_award_summary(db, row) for row in rows], "page": page, "page_size": page_size}


@router.post("/admin/achievements", status_code=201)
def create_achievement(payload: AchievementIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    _validate_rule(payload)
    if db.scalar(select(AchievementDefinition.id).where(AchievementDefinition.slug == payload.code)):
        raise HTTPException(409, "Achievement code already exists")
    row = AchievementDefinition(slug=payload.code, title=payload.title, title_mm=payload.title_mm, description=payload.description, description_mm=payload.description_mm, criteria_description=payload.criteria, criteria_description_mm=payload.criteria_mm, category=payload.category, threshold=payload.threshold, rule_type=payload.rule_type, rule_json=json.dumps(payload.rule, separators=(",", ":")), badge_image_url=payload.badge_image_url, icon_name=payload.icon_name, tier=payload.tier, related_course_id=payload.related_course_id, related_path_id=payload.related_path_id, visibility=payload.visibility, display_order=payload.display_order, created_by=user.id, status="draft")
    db.add(row)
    db.flush()
    db.add(AchievementRuleVersion(achievement_id=row.id, version=1, rule_type=row.rule_type, rule_json=row.rule_json, status="draft", created_by=user.id))
    audit(db, user, "achievement_definition_created", "achievement_definition", row.id)
    db.commit()
    return definition_payload(row, include_private=True)


@router.get("/admin/achievements/{achievement_id}")
def admin_achievement_detail(achievement_id: UUID, user: User = Depends(full_admin), db: Session = Depends(get_db)):
    row = db.get(AchievementDefinition, achievement_id)
    if not row:
        raise HTTPException(404, "Achievement not found")
    return definition_payload(row, include_private=True)


@router.patch("/admin/achievements/{achievement_id}")
def update_achievement(achievement_id: UUID, payload: AchievementIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    _validate_rule(payload)
    row = db.get(AchievementDefinition, achievement_id)
    if not row:
        raise HTTPException(404, "Achievement not found")
    if row.status in {"published", "archived"}:
        raise HTTPException(409, "Published or archived achievements require a new definition version")
    if payload.code != row.slug and db.scalar(select(AchievementDefinition.id).where(AchievementDefinition.slug == payload.code, AchievementDefinition.id != row.id)):
        raise HTTPException(409, "Achievement code already exists")
    for key, value in {"slug": payload.code, "title": payload.title, "title_mm": payload.title_mm, "description": payload.description, "description_mm": payload.description_mm, "criteria_description": payload.criteria, "criteria_description_mm": payload.criteria_mm, "category": payload.category, "threshold": payload.threshold, "rule_type": payload.rule_type, "badge_image_url": payload.badge_image_url, "icon_name": payload.icon_name, "tier": payload.tier, "related_course_id": payload.related_course_id, "related_path_id": payload.related_path_id, "visibility": payload.visibility, "display_order": payload.display_order}.items():
        setattr(row, key, value)
    row.rule_json = json.dumps(payload.rule, separators=(",", ":"))
    row.rule_version += 1
    db.add(AchievementRuleVersion(achievement_id=row.id, version=row.rule_version, rule_type=row.rule_type, rule_json=row.rule_json, status="draft", created_by=user.id))
    row.status = "draft"
    audit(db, user, "achievement_definition_updated", "achievement_definition", row.id)
    db.commit()
    return definition_payload(row, include_private=True)


@router.post("/admin/achievements/{achievement_id}/submit-review")
def submit_achievement(achievement_id: UUID, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(AchievementDefinition, achievement_id)
    if not row or row.status != "draft":
        raise HTTPException(409, "Only drafts can be submitted for review")
    row.status = "in_review"
    audit(db, user, "achievement_definition_submitted", "achievement_definition", row.id)
    db.commit()
    return {"id": str(row.id), "status": row.status}


@router.post("/admin/achievements/{achievement_id}/approve")
def approve_achievement(achievement_id: UUID, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(AchievementDefinition, achievement_id)
    if not row or row.status != "in_review":
        raise HTTPException(409, "Only definitions in review can be approved")
    row.status = "approved"
    audit(db, user, "achievement_definition_approved", "achievement_definition", row.id)
    db.commit()
    return {"id": str(row.id), "status": row.status}


@router.post("/admin/achievements/{achievement_id}/publish")
def publish_achievement(achievement_id: UUID, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(AchievementDefinition, achievement_id)
    if not row or row.status != "approved":
        raise HTTPException(409, "An approved definition is required before publishing")
    if row.rule_type not in ALLOWED_RULE_TYPES or not row.criteria_description.strip():
        raise HTTPException(422, "A valid allowlisted rule and criteria description are required")
    row.status = "published"
    row.published_at = datetime.now(timezone.utc)
    audit(db, user, "achievement_definition_published", "achievement_definition", row.id)
    db.commit()
    return definition_payload(row, include_private=True)


@router.post("/admin/achievements/{achievement_id}/archive")
def archive_achievement(achievement_id: UUID, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(AchievementDefinition, achievement_id)
    if not row:
        raise HTTPException(404, "Achievement not found")
    row.status = "archived"
    audit(db, user, "achievement_definition_archived", "achievement_definition", row.id)
    db.commit()
    return {"id": str(row.id), "status": row.status}


@router.get("/admin/achievements/{achievement_id}/eligibility/{user_id}")
def evaluate_achievement(achievement_id: UUID, user_id: UUID, user: User = Depends(full_admin), db: Session = Depends(get_db)):
    row = db.get(AchievementDefinition, achievement_id)
    if not row:
        raise HTTPException(404, "Achievement not found")
    return {"achievement": definition_payload(row, include_private=True), "user_id": str(user_id), "evaluation": evaluate_definition(db, user_id, row)}


@router.post("/admin/achievement-awards/{public_id}/revoke")
def revoke_award(public_id: str, reason: str = Query(..., min_length=3, max_length=500), user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.scalar(select(StudentAchievement).where(StudentAchievement.public_id == public_id))
    if not row:
        raise HTTPException(404, "Achievement award not found")
    if row.status != "revoked":
        row.status = "revoked"
        row.revoked_at = datetime.now(timezone.utc)
        row.revocation_reason = reason.strip()
        db.add(AchievementAuditEvent(actor_id=user.id, action="achievement_award_revoked", resource_type="student_achievement", resource_id=row.id, metadata_json=json.dumps({"reason": reason.strip()})))
        audit(db, user, "achievement_award_revoked", "student_achievement", row.id)
        db.commit()
    return _award_summary(db, row)


@router.get("/admin/achievement-audit")
def achievement_audit(page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=100), user: User = Depends(full_admin), db: Session = Depends(get_db)):
    rows = db.scalars(select(AchievementAuditEvent).order_by(AchievementAuditEvent.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [{"id": str(row.id), "action": row.action, "resource_type": row.resource_type, "resource_id": str(row.resource_id) if row.resource_id else None, "actor_id": str(row.actor_id) if row.actor_id else None, "metadata": json.loads(row.metadata_json or "{}"), "created_at": row.created_at} for row in rows], "page": page, "page_size": page_size}
