"""Durable platform announcements, templates, inbox messages and delivery evidence."""

import json
import logging
import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .auth import current_user, require_csrf, verified_user
from .config import settings
from .db import get_db
from .mailer import mailer
from .models import (
    NotificationAnnouncement, NotificationAuditEvent, NotificationDeliveryAttempt,
    NotificationMessage, NotificationOutbox, NotificationPreference, NotificationProviderEvent,
    Enrollment, NotificationTemplate, NotificationTemplateVersion, User, UserProfile,
)
from .rbac import require_platform_admin
from .schemas import NotificationAnnouncementIn, NotificationAnnouncementPatch, NotificationPreferencePatch, NotificationTemplateIn, NotificationTemplatePatch

logger = logging.getLogger("codemaster.notifications")
admin_router = APIRouter(prefix="/api/v1/admin/notifications", tags=["admin-notifications"])
me_router = APIRouter(prefix="/api/v1/me/notifications", tags=["notifications"])
preference_router = APIRouter(prefix="/api/v1/me/notification-preferences", tags=["notification-preferences"])
PLACEHOLDER = re.compile(r"\{\{\s*([a-z][a-z0-9_]*)\s*\}\}")
ALLOWED_VARIABLES = {"user_name", "course_name", "announcement_title", "support_url", "unsubscribe_url"}
RETRYABLE_ERRORS = {"smtp_send_failed", "provider_timeout", "provider_rate_limited"}


def _json(value: str, fallback: Any):
    try:
        parsed = json.loads(value or "")
        return parsed
    except (TypeError, ValueError, json.JSONDecodeError):
        return fallback


def _correlation(request: Request) -> str:
    return request.headers.get("X-Request-ID") or getattr(request.state, "request_id", str(uuid.uuid4()))


def _audit(db: Session, actor: User | None, action: str, resource_type: str, resource_id: uuid.UUID | None, correlation_id: str, outcome="success", metadata=None):
    db.add(NotificationAuditEvent(actor_id=actor.id if actor else None, action=action, resource_type=resource_type, resource_id=resource_id, outcome=outcome, correlation_id=correlation_id, metadata_json=json.dumps(metadata or {}, separators=(",", ":"))))


def _template_payload(template: NotificationTemplate, version: NotificationTemplateVersion | None = None):
    return {"id": str(template.id), "template_key": template.template_key, "name": template.name, "category": template.category, "channel": template.channel, "locale": template.locale, "status": template.status, "current_version": template.current_version, "version": ({"id": str(version.id), "version": version.version, "subject": version.subject, "body": version.body, "variables": _json(version.variables_json, []), "status": version.status, "created_at": version.created_at} if version else None)}


def _announcement_payload(row: NotificationAnnouncement):
    return {"id": str(row.id), "title_en": row.title_en, "title_mm": row.title_mm, "body_en": row.body_en, "body_mm": row.body_mm, "audience_type": row.audience_type, "audience": _json(row.audience_json, {}), "channels": _json(row.channels_json, ["in_app"]), "status": row.status, "scheduled_at": row.scheduled_at, "created_at": row.created_at, "published_at": row.published_at}


def _validate_template_content(subject: str, body: str, variables: list[str]):
    unknown = {name for text in (subject, body) for name in PLACEHOLDER.findall(text)} - set(variables)
    invalid = set(variables) - ALLOWED_VARIABLES
    if unknown or invalid:
        raise HTTPException(422, {"message": "Template variables must be explicitly allowed", "unknown": sorted(unknown), "invalid": sorted(invalid)})


def _render(text: str, values: dict[str, Any]) -> str:
    return PLACEHOLDER.sub(lambda match: str(values.get(match.group(1), match.group(0))), text)


def _preference(db: Session, user: User) -> NotificationPreference:
    row = db.scalar(select(NotificationPreference).where(NotificationPreference.user_id == user.id))
    if row:
        return row
    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
    row = NotificationPreference(user_id=user.id, preferred_locale="my" if profile and profile.preferred_language == "my" else "en")
    db.add(row)
    db.flush()
    return row


def _audience(db: Session, row: NotificationAnnouncement) -> list[User]:
    audience = _json(row.audience_json, {})
    if row.audience_type == "administrators":
        return db.scalars(select(User).where(User.account_status == "active", User.role.in_(["admin", "platform_admin", "super_admin"]))).all()
    if row.audience_type == "user_ids":
        ids = audience.get("user_ids", []) if isinstance(audience, dict) else []
        try:
            parsed = [uuid.UUID(str(item)) for item in ids]
        except (ValueError, TypeError):
            raise HTTPException(422, "Audience user_ids are invalid")
        return db.scalars(select(User).where(User.id.in_(parsed), User.account_status == "active")).all() if parsed else []
    if row.audience_type == "course_enrolled":
        course_id = audience.get("course_id") if isinstance(audience, dict) else None
        try:
            parsed_course_id = uuid.UUID(str(course_id))
        except (ValueError, TypeError):
            raise HTTPException(422, "Audience course_id is invalid")
        return db.scalars(select(User).join(Enrollment, Enrollment.user_id == User.id).where(Enrollment.course_id == parsed_course_id, User.account_status == "active")).all()
    if row.audience_type == "all_users":
        return db.scalars(select(User).where(User.account_status == "active")).all()
    return db.scalars(select(User).where(User.account_status == "active", User.role == "student")).all()


def _message_payload(row: NotificationMessage, recipient: User | None = None):
    return {"id": str(row.id), "announcement_id": str(row.announcement_id) if row.announcement_id else None, "recipient_id": str(row.recipient_id), "recipient": recipient.email if recipient else None, "channel": row.channel, "locale": row.locale, "subject": row.subject, "body": row.body, "status": row.status, "provider": row.provider, "provider_message_id": row.provider_message_id, "error_code": row.error_code, "next_retry_at": row.next_retry_at, "read_at": row.read_at, "created_at": row.created_at}


@admin_router.get("/overview")
def overview(db: Session = Depends(get_db), _: User = Depends(require_platform_admin)):
    statuses = dict(db.execute(select(NotificationMessage.status, func.count(NotificationMessage.id)).group_by(NotificationMessage.status)).all())
    return {"data_source": "database", "announcements": {"draft": db.scalar(select(func.count(NotificationAnnouncement.id)).where(NotificationAnnouncement.status == "draft")) or 0, "scheduled": db.scalar(select(func.count(NotificationAnnouncement.id)).where(NotificationAnnouncement.status == "scheduled")) or 0, "published": db.scalar(select(func.count(NotificationAnnouncement.id)).where(NotificationAnnouncement.status == "published")) or 0}, "deliveries": statuses, "queued_outbox": db.scalar(select(func.count(NotificationOutbox.id)).where(NotificationOutbox.status == "queued")) or 0, "failed_deliveries": sum(value for key, value in statuses.items() if key in {"failed", "bounced", "deferred"}), "providers": {"in_app": "ready", "email": "configured" if settings.mailer_mode != "console" else "not_configured", "web_push": "not_configured", "sms": "not_configured"}}


@admin_router.get("/announcements")
def announcements(db: Session = Depends(get_db), _: User = Depends(require_platform_admin), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    total = db.scalar(select(func.count(NotificationAnnouncement.id))) or 0
    rows = db.scalars(select(NotificationAnnouncement).order_by(NotificationAnnouncement.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [_announcement_payload(row) for row in rows], "page": page, "page_size": page_size, "total": total, "pages": (total + page_size - 1) // page_size}


@admin_router.post("/announcements")
def create_announcement(payload: NotificationAnnouncementIn, request: Request, db: Session = Depends(get_db), actor: User = Depends(require_platform_admin), _: None = Depends(require_csrf)):
    row = NotificationAnnouncement(title_en=payload.title_en, title_mm=payload.title_mm, body_en=payload.body_en, body_mm=payload.body_mm, audience_type=payload.audience_type, audience_json=json.dumps(payload.audience), channels_json=json.dumps(list(dict.fromkeys(payload.channels))), scheduled_at=payload.scheduled_at, created_by=actor.id, correlation_id=_correlation(request))
    db.add(row); db.flush(); _audit(db, actor, "announcement.created", "announcement", row.id, _correlation(request)); db.commit(); db.refresh(row)
    return _announcement_payload(row)


@admin_router.patch("/announcements/{announcement_id}")
def update_announcement(announcement_id: uuid.UUID, payload: NotificationAnnouncementPatch, request: Request, db: Session = Depends(get_db), actor: User = Depends(require_platform_admin), _: None = Depends(require_csrf)):
    row = db.get(NotificationAnnouncement, announcement_id)
    if not row: raise HTTPException(404, "Announcement not found")
    if row.status not in {"draft", "in_review"}: raise HTTPException(409, "Only draft or in-review announcements can be edited")
    for key, value in payload.model_dump(exclude_unset=True).items():
        if key == "audience": setattr(row, "audience_json", json.dumps(value))
        elif key == "channels": setattr(row, "channels_json", json.dumps(list(dict.fromkeys(value))))
        elif value is not None: setattr(row, key, value)
    _audit(db, actor, "announcement.updated", "announcement", row.id, _correlation(request)); db.commit(); db.refresh(row); return _announcement_payload(row)


def _announcement_transition(announcement_id: uuid.UUID, target: str, request: Request, db: Session, actor: User):
    row = db.get(NotificationAnnouncement, announcement_id)
    if not row: raise HTTPException(404, "Announcement not found")
    allowed = {"submit": {"draft": "in_review"}, "approve": {"in_review": "approved"}, "schedule": {"approved": "scheduled"}, "cancel": {"draft": "cancelled", "in_review": "cancelled", "approved": "cancelled", "scheduled": "cancelled"}, "archive": {"published": "archived", "cancelled": "archived"}}
    if target not in allowed or row.status not in allowed[target]: raise HTTPException(409, f"Announcement cannot transition from {row.status}")
    row.status = allowed[target][row.status]
    if target == "approve": row.approved_by = actor.id
    _audit(db, actor, f"announcement.{target}", "announcement", row.id, _correlation(request)); db.commit(); db.refresh(row); return _announcement_payload(row)


@admin_router.post("/announcements/{announcement_id}/submit")
def submit_announcement(announcement_id: uuid.UUID, request: Request, db: Session = Depends(get_db), actor: User = Depends(require_platform_admin), _: None = Depends(require_csrf)): return _announcement_transition(announcement_id, "submit", request, db, actor)
@admin_router.post("/announcements/{announcement_id}/approve")
def approve_announcement(announcement_id: uuid.UUID, request: Request, db: Session = Depends(get_db), actor: User = Depends(require_platform_admin), _: None = Depends(require_csrf)): return _announcement_transition(announcement_id, "approve", request, db, actor)
@admin_router.post("/announcements/{announcement_id}/schedule")
def schedule_announcement(announcement_id: uuid.UUID, request: Request, db: Session = Depends(get_db), actor: User = Depends(require_platform_admin), _: None = Depends(require_csrf)): return _announcement_transition(announcement_id, "schedule", request, db, actor)
@admin_router.post("/announcements/{announcement_id}/cancel")
def cancel_announcement(announcement_id: uuid.UUID, request: Request, db: Session = Depends(get_db), actor: User = Depends(require_platform_admin), _: None = Depends(require_csrf)): return _announcement_transition(announcement_id, "cancel", request, db, actor)
@admin_router.post("/announcements/{announcement_id}/archive")
def archive_announcement(announcement_id: uuid.UUID, request: Request, db: Session = Depends(get_db), actor: User = Depends(require_platform_admin), _: None = Depends(require_csrf)): return _announcement_transition(announcement_id, "archive", request, db, actor)


@admin_router.post("/announcements/{announcement_id}/publish")
def publish_announcement(announcement_id: uuid.UUID, request: Request, db: Session = Depends(get_db), actor: User = Depends(require_platform_admin), _: None = Depends(require_csrf)):
    row = db.get(NotificationAnnouncement, announcement_id)
    if not row: raise HTTPException(404, "Announcement not found")
    if row.status not in {"approved", "scheduled"}: raise HTTPException(409, "Announcement must be approved before publishing")
    now = datetime.now(timezone.utc)
    if row.status == "scheduled" and row.scheduled_at and row.scheduled_at > now: raise HTTPException(409, "Announcement is scheduled for a future time")
    users = _audience(db, row); channels = _json(row.channels_json, ["in_app"]); created = 0
    for user in users:
        pref = _preference(db, user); locale = pref.preferred_locale if pref.preferred_locale in {"en", "my"} else "en"
        title = row.title_mm if locale == "my" and row.title_mm else row.title_en
        body = row.body_mm if locale == "my" and row.body_mm else row.body_en
        for channel in channels:
            if channel == "in_app" and not pref.in_app_enabled: continue
            if channel == "email" and (not pref.email_enabled or not pref.course_announcements): continue
            key = f"announcement:{row.id}:user:{user.id}:channel:{channel}"
            if db.scalar(select(NotificationMessage.id).where(NotificationMessage.idempotency_key == key)): continue
            message = NotificationMessage(announcement_id=row.id, recipient_id=user.id, channel=channel, locale=locale, subject=title, body=body, status="delivered" if channel == "in_app" else "queued", provider="in_app" if channel == "in_app" else "smtp", idempotency_key=key, correlation_id=_correlation(request))
            db.add(message); db.flush(); db.add(NotificationDeliveryAttempt(message_id=message.id, attempt_number=1, status=message.status, correlation_id=_correlation(request)))
            db.add(NotificationOutbox(message_id=message.id, status="completed" if channel == "in_app" else "queued", attempt_count=1 if channel == "in_app" else 0)); created += 1
    row.status = "published"; row.published_by = actor.id; row.published_at = now; _audit(db, actor, "announcement.published", "announcement", row.id, _correlation(request), metadata={"message_count": created}); db.commit(); return {**_announcement_payload(row), "messages_created": created, "email_provider": "configured" if settings.mailer_mode != "console" else "not_configured"}


@admin_router.get("/templates")
def templates(db: Session = Depends(get_db), _: User = Depends(require_platform_admin)):
    rows = db.scalars(select(NotificationTemplate).order_by(NotificationTemplate.name)).all(); output=[]
    for row in rows:
        version = db.scalar(select(NotificationTemplateVersion).where(NotificationTemplateVersion.template_id == row.id, NotificationTemplateVersion.version == row.current_version))
        output.append(_template_payload(row, version))
    return {"items": output, "allowed_variables": sorted(ALLOWED_VARIABLES)}


@admin_router.get("/templates/{template_id}/versions")
def template_versions(template_id: uuid.UUID, db: Session = Depends(get_db), _: User = Depends(require_platform_admin)):
    if not db.get(NotificationTemplate, template_id): raise HTTPException(404, "Template not found")
    rows = db.scalars(select(NotificationTemplateVersion).where(NotificationTemplateVersion.template_id == template_id).order_by(NotificationTemplateVersion.version.desc())).all()
    return {"items": [{"id": str(row.id), "version": row.version, "subject": row.subject, "body": row.body, "variables": _json(row.variables_json, []), "status": row.status, "created_at": row.created_at} for row in rows]}


@admin_router.post("/templates")
def create_template(payload: NotificationTemplateIn, request: Request, db: Session = Depends(get_db), actor: User = Depends(require_platform_admin), _: None = Depends(require_csrf)):
    _validate_template_content(payload.subject, payload.body, payload.variables)
    if db.scalar(select(NotificationTemplate).where(NotificationTemplate.template_key == payload.template_key, NotificationTemplate.channel == payload.channel, NotificationTemplate.locale == payload.locale)): raise HTTPException(409, "Template already exists")
    row=NotificationTemplate(template_key=payload.template_key, name=payload.name, category=payload.category, channel=payload.channel, locale=payload.locale); db.add(row); db.flush(); db.add(NotificationTemplateVersion(template_id=row.id, version=1, subject=payload.subject, body=payload.body, variables_json=json.dumps(payload.variables), created_by=actor.id)); _audit(db, actor, "template.created", "template", row.id, _correlation(request)); db.commit(); db.refresh(row); version=db.scalar(select(NotificationTemplateVersion).where(NotificationTemplateVersion.template_id == row.id)); return _template_payload(row, version)


@admin_router.patch("/templates/{template_id}")
def update_template(template_id: uuid.UUID, payload: NotificationTemplatePatch, request: Request, db: Session = Depends(get_db), actor: User = Depends(require_platform_admin), _: None = Depends(require_csrf)):
    row=db.get(NotificationTemplate, template_id)
    if not row: raise HTTPException(404, "Template not found")
    current=db.scalar(select(NotificationTemplateVersion).where(NotificationTemplateVersion.template_id == row.id, NotificationTemplateVersion.version == row.current_version))
    if not current: raise HTTPException(500, "Template version is missing")
    values=payload.model_dump(exclude_unset=True); subject=values.get("subject", current.subject); body=values.get("body", current.body); variables=values.get("variables", _json(current.variables_json, [])); _validate_template_content(subject, body, variables)
    if "name" in values: row.name=values["name"]
    if "category" in values: row.category=values["category"]
    version=NotificationTemplateVersion(template_id=row.id, version=row.current_version + 1, subject=subject, body=body, variables_json=json.dumps(variables), created_by=actor.id); db.add(version); row.current_version += 1; row.status="draft"; _audit(db, actor, "template.version_created", "template", row.id, _correlation(request), metadata={"version": row.current_version}); db.commit(); db.refresh(row); return _template_payload(row, version)


@admin_router.post("/templates/{template_id}/{action}")
def template_action(template_id: uuid.UUID, action: str, request: Request, db: Session = Depends(get_db), actor: User = Depends(require_platform_admin), _: None = Depends(require_csrf)):
    row=db.get(NotificationTemplate, template_id)
    if not row or action not in {"submit", "approve", "publish", "archive"}: raise HTTPException(404, "Template or action not found")
    transitions={"submit":{"draft":"in_review"},"approve":{"in_review":"approved"},"publish":{"approved":"published"},"archive":{"published":"archived"}}
    if row.status not in transitions[action]: raise HTTPException(409, f"Template cannot transition from {row.status}")
    row.status=transitions[action][row.status]; version=db.scalar(select(NotificationTemplateVersion).where(NotificationTemplateVersion.template_id == row.id, NotificationTemplateVersion.version == row.current_version)); version.status=row.status if version else row.status
    if action == "approve" and version: version.reviewed_by=actor.id
    if action == "publish" and version: version.published_by=actor.id
    _audit(db, actor, f"template.{action}", "template", row.id, _correlation(request)); db.commit(); return _template_payload(row, version)


@admin_router.post("/templates/{template_id}/preview")
def preview_template(template_id: uuid.UUID, values: dict[str, Any], db: Session = Depends(get_db), _: User = Depends(require_platform_admin)):
    row=db.get(NotificationTemplate, template_id); version=db.scalar(select(NotificationTemplateVersion).where(NotificationTemplateVersion.template_id == template_id, NotificationTemplateVersion.version == row.current_version if row else -1)) if row else None
    if not row or not version: raise HTTPException(404, "Template not found")
    allowed=set(_json(version.variables_json, [])); return {"subject": _render(version.subject, {key: values.get(key, "") for key in allowed}), "body": _render(version.body, {key: values.get(key, "") for key in allowed}), "sent": False}


@admin_router.get("/deliveries")
def deliveries(db: Session = Depends(get_db), _: User = Depends(require_platform_admin), status_filter: str | None = Query(None, alias="status"), channel: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100)):
    query=select(NotificationMessage, User).join(User, User.id == NotificationMessage.recipient_id)
    if status_filter: query=query.where(NotificationMessage.status == status_filter)
    if channel: query=query.where(NotificationMessage.channel == channel)
    total=db.scalar(select(func.count(NotificationMessage.id)).where(*(x for x in [NotificationMessage.status == status_filter if status_filter else None, NotificationMessage.channel == channel if channel else None] if x is not None))) or 0
    rows=db.execute(query.order_by(NotificationMessage.created_at.desc()).offset((page-1)*page_size).limit(page_size)).all()
    return {"items": [_message_payload(message, user) for message, user in rows], "page": page, "page_size": page_size, "total": total, "pages": (total+page_size-1)//page_size}


@admin_router.get("/failures")
def failures(db: Session = Depends(get_db), _: User = Depends(require_platform_admin), page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100)):
    rows=db.scalars(select(NotificationMessage).where(NotificationMessage.status.in_(["failed", "bounced", "deferred", "not_configured"])).order_by(NotificationMessage.created_at.desc()).offset((page-1)*page_size).limit(page_size)).all()
    return {"items": [_message_payload(row) for row in rows], "page": page, "page_size": page_size, "retryable_statuses": sorted(RETRYABLE_ERRORS)}


@admin_router.post("/deliveries/{message_id}/retry")
def retry_delivery(message_id: uuid.UUID, request: Request, db: Session = Depends(get_db), actor: User = Depends(require_platform_admin), _: None = Depends(require_csrf)):
    row=db.get(NotificationMessage, message_id)
    if not row: raise HTTPException(404, "Delivery not found")
    if row.error_code not in RETRYABLE_ERRORS and row.status not in {"failed", "deferred"}: raise HTTPException(409, "Only retryable failed deliveries can be retried")
    row.status="queued"; row.next_retry_at=datetime.now(timezone.utc); row.error_code=None; outbox=db.scalar(select(NotificationOutbox).where(NotificationOutbox.message_id == row.id));
    if outbox: outbox.status="queued"; outbox.available_at=datetime.now(timezone.utc); outbox.last_error_code=None
    _audit(db, actor, "delivery.retry_requested", "message", row.id, _correlation(request)); db.commit(); return _message_payload(row)


@admin_router.post("/outbox/process")
def process_outbox(request: Request, db: Session = Depends(get_db), actor: User = Depends(require_platform_admin), _: None = Depends(require_csrf), limit: int = Query(50, ge=1, le=200)):
    rows=db.scalars(select(NotificationOutbox).where(NotificationOutbox.status == "queued", NotificationOutbox.available_at <= datetime.now(timezone.utc)).order_by(NotificationOutbox.created_at).limit(limit)).all(); processed=0
    for outbox in rows:
        message=db.get(NotificationMessage, outbox.message_id)
        if not message: outbox.status="dead_letter"; continue
        outbox.status="processing"; outbox.attempt_count += 1; message.status="processing"; db.flush()
        if message.channel == "in_app":
            message.status="delivered"; outbox.status="completed"; message.error_code=None; db.add(NotificationDeliveryAttempt(message_id=message.id, attempt_number=outbox.attempt_count, status="delivered", correlation_id=_correlation(request)))
        else:
            recipient=db.get(User, message.recipient_id); result=mailer.send_notification(recipient.email, message.subject, message.body) if recipient else None
            result_status=result.status if result else "failed"; message.status=result_status; message.provider=result.provider if result else "smtp"; message.provider_message_id=result.provider_message_id if result else None; message.error_code=result.error_code if result else "recipient_not_found"; message.next_retry_at=datetime.now(timezone.utc)+timedelta(minutes=min(60, 2 ** min(outbox.attempt_count, 6))) if result_status == "failed" else None
            outbox.status="queued" if result_status == "failed" and outbox.attempt_count < 5 else "dead_letter" if result_status == "failed" else "blocked" if result_status == "not_configured" else "completed"; outbox.last_error_code=message.error_code; db.add(NotificationDeliveryAttempt(message_id=message.id, attempt_number=outbox.attempt_count, status=result_status, provider_message_id=message.provider_message_id, error_code=message.error_code, correlation_id=_correlation(request)))
        processed += 1
    _audit(db, actor, "outbox.processed", "outbox", None, _correlation(request), metadata={"processed": processed}); db.commit(); return {"processed": processed, "provider": "configured" if settings.mailer_mode != "console" else "not_configured", "durable": True}


@admin_router.get("/providers")
def providers(_: User = Depends(require_platform_admin)):
    return {"items": [{"channel": "in_app", "provider": "database", "status": "ready", "delivery_evidence": "persisted_inbox"}, {"channel": "email", "provider": settings.mailer_mode, "status": "configured" if settings.mailer_mode != "console" else "not_configured", "delivery_evidence": "provider_acceptance_only" if settings.mailer_mode != "console" else "none"}, {"channel": "web_push", "provider": "not_configured", "status": "not_configured"}, {"channel": "sms", "provider": "not_configured", "status": "not_configured"}]}


@admin_router.get("/audit")
def audit(db: Session = Depends(get_db), _: User = Depends(require_platform_admin), page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=100)):
    rows=db.scalars(select(NotificationAuditEvent).order_by(NotificationAuditEvent.created_at.desc()).offset((page-1)*page_size).limit(page_size)).all(); return {"items": [{"id": str(row.id), "action": row.action, "resource_type": row.resource_type, "resource_id": str(row.resource_id) if row.resource_id else None, "outcome": row.outcome, "correlation_id": row.correlation_id, "created_at": row.created_at} for row in rows], "page": page, "page_size": page_size}


@me_router.get("")
def inbox(db: Session = Depends(get_db), user: User = Depends(verified_user), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100)):
    total=db.scalar(select(func.count(NotificationMessage.id)).where(NotificationMessage.recipient_id == user.id, NotificationMessage.channel == "in_app")) or 0; unread=db.scalar(select(func.count(NotificationMessage.id)).where(NotificationMessage.recipient_id == user.id, NotificationMessage.channel == "in_app", NotificationMessage.read_at.is_(None))) or 0; rows=db.scalars(select(NotificationMessage).where(NotificationMessage.recipient_id == user.id, NotificationMessage.channel == "in_app").order_by(NotificationMessage.created_at.desc()).offset((page-1)*page_size).limit(page_size)).all(); return {"items": [_message_payload(row) for row in rows], "unread": unread, "page": page, "page_size": page_size, "total": total, "pages": (total+page_size-1)//page_size}


@me_router.post("/{message_id}/read")
def read_notification(message_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(verified_user), _: None = Depends(require_csrf)):
    row=db.scalar(select(NotificationMessage).where(NotificationMessage.id == message_id, NotificationMessage.recipient_id == user.id, NotificationMessage.channel == "in_app"));
    if not row: raise HTTPException(404, "Notification not found")
    row.read_at=datetime.now(timezone.utc); db.commit(); return {"id": str(row.id), "read": True}


@me_router.post("/read-all")
def read_all(db: Session = Depends(get_db), user: User = Depends(verified_user), _: None = Depends(require_csrf)):
    rows=db.scalars(select(NotificationMessage).where(NotificationMessage.recipient_id == user.id, NotificationMessage.channel == "in_app", NotificationMessage.read_at.is_(None))).all(); now=datetime.now(timezone.utc)
    for row in rows: row.read_at=now
    db.commit(); return {"updated": len(rows)}


@preference_router.get("")
def get_preferences(db: Session = Depends(get_db), user: User = Depends(verified_user)):
    row=_preference(db, user); db.commit(); return {"preferred_locale": row.preferred_locale, "in_app_enabled": row.in_app_enabled, "email_enabled": row.email_enabled, "course_announcements": row.course_announcements, "digest_frequency": row.digest_frequency, "quiet_hours_start": row.quiet_hours_start, "quiet_hours_end": row.quiet_hours_end}


@preference_router.patch("")
def update_preferences(payload: NotificationPreferencePatch, request: Request, db: Session = Depends(get_db), user: User = Depends(verified_user), _: None = Depends(require_csrf)):
    row=_preference(db, user)
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(row, key, value)
    _audit(db, user, "preferences.updated", "preference", row.id, _correlation(request)); db.commit(); return get_preferences(db, user)
