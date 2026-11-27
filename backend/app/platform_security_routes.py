"""Platform-level security center backed by the existing auth and audit tables.

The application intentionally keeps its canonical role on ``users.role``. This
router adds the management and reporting surface around that value instead of
introducing a second authentication or RBAC system.
"""

import json
import math
from datetime import timedelta
from uuid import UUID

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from .auth import SESSION_COOKIE, hash_token, now, require_csrf
from .config import settings
from .db import get_db
from .models import (
    AdminAuditLog,
    AuthSession,
    PlatformSetting,
    SecurityAlertEvent,
    SecurityAlertRule,
    SecurityAuditLog,
    User,
)
from .rbac import PLATFORM_ADMIN_ROLES, require_platform_admin, require_super_admin

router = APIRouter(prefix="/api/v1/platform/security", tags=["platform security"])

ROLE_ORDER = (
    "student",
    "content_editor",
    "content_reviewer",
    "instructor",
    "moderator",
    "admin",
    "platform_admin",
    "super_admin",
)
ROLE_RANK = {role: index for index, role in enumerate(ROLE_ORDER)}
SECURITY_POLICY_KEY = "platform:security_policy"

ROLE_DEFINITIONS = {
    "student": {"label": "Student", "description": "Learning access only."},
    "content_editor": {"label": "Content editor", "description": "Creates and updates assigned learning content."},
    "content_reviewer": {"label": "Content reviewer", "description": "Reviews content before publication."},
    "instructor": {"label": "Instructor", "description": "Creates instructional and live learning content."},
    "moderator": {"label": "Moderator", "description": "Handles community moderation workflows."},
    "admin": {"label": "Administrator", "description": "Legacy platform administrator role."},
    "platform_admin": {"label": "Platform administrator", "description": "Manages platform operations and governance."},
    "super_admin": {"label": "Platform super administrator", "description": "Highest privilege; protected by last-admin safeguards."},
}

PERMISSION_DEFINITIONS = (
    ("security.read", "Read Security Center records.", ("admin", "platform_admin", "super_admin")),
    ("security.roles.manage", "Assign and revoke platform roles.", ("super_admin",)),
    ("security.audit.read", "Read privileged action history.", ("admin", "platform_admin", "super_admin")),
    ("security.events.read", "Read authentication and security events.", ("admin", "platform_admin", "super_admin")),
    ("security.sessions.manage", "Revoke administrator sessions.", ("super_admin",)),
    ("security.policies.manage", "Update persisted platform security policy.", ("super_admin",)),
    ("users.read", "Read user and role assignments.", ("admin", "platform_admin", "super_admin")),
    ("users.manage", "Manage user account access.", ("super_admin",)),
    ("courses.read", "Read course administration records.", ("admin", "platform_admin", "super_admin")),
    ("courses.create", "Create course drafts.", ("admin", "platform_admin", "super_admin")),
    ("courses.update", "Update course content.", ("admin", "platform_admin", "super_admin")),
    ("courses.publish", "Publish course content.", ("platform_admin", "super_admin")),
)


class RoleAssignmentIn(BaseModel):
    user_id: UUID
    role: str = Field(pattern=r"^(student|content_editor|content_reviewer|instructor|moderator|admin|platform_admin|super_admin)$")


class SecurityPolicyPatch(BaseModel):
    require_admin_mfa: bool | None = None
    session_timeout_minutes: int | None = Field(default=None, ge=15, le=43200)
    max_login_attempts: int | None = Field(default=None, ge=3, le=20)
    audit_retention_days: int | None = Field(default=None, ge=1, le=3650)
    access_review_days: int | None = Field(default=None, ge=1, le=730)


DEFAULT_SECURITY_POLICY = {
    "require_admin_mfa": False,
    "session_timeout_minutes": 10080,
    "max_login_attempts": 10,
    "audit_retention_days": settings.security_audit_retention_days,
    "access_review_days": 90,
}


def _safe_json(value: str | None) -> dict:
    try:
        parsed = json.loads(value or "{}")
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def _actor_name(user: User | None) -> dict | None:
    if not user:
        return None
    return {"id": user.id, "display_name": user.display_name, "role": user.role}


def _page(page: int, page_size: int, total: int) -> dict:
    return {"page": page, "page_size": page_size, "total": total, "pages": math.ceil(total / page_size) if total else 0}


def _record_privileged_action(
    db: Session,
    actor: User,
    request: Request,
    action: str,
    entity_type: str,
    entity_id: UUID | None = None,
    metadata: dict | None = None,
    outcome: str = "success",
) -> None:
    request_id = getattr(request.state, "request_id", None)
    safe_metadata = {"outcome": outcome, "request_id": request_id, **(metadata or {})}
    encoded = json.dumps(safe_metadata, sort_keys=True, default=str)
    db.add(AdminAuditLog(actor_id=actor.id, action=action, entity_type=entity_type, entity_id=entity_id, metadata_json=encoded))
    db.add(SecurityAuditLog(user_id=actor.id, event=action, ip_address=request.client.host if request.client else None, metadata_json=encoded))


def _assignment(row: User) -> dict:
    return {
        "id": row.id,
        "user_id": row.id,
        "display_name": row.display_name,
        "email": row.email,
        "role": row.role,
        "account_status": row.account_status,
        "email_verified": row.email_verified_at is not None,
        "created_at": row.created_at,
        "last_login_at": row.last_login_at,
    }


def _policy(db: Session) -> dict:
    row = db.scalar(select(PlatformSetting).where(PlatformSetting.key == SECURITY_POLICY_KEY))
    if not row:
        return DEFAULT_SECURITY_POLICY.copy()
    return {**DEFAULT_SECURITY_POLICY, **_safe_json(row.value_json)}


@router.get("/overview")
def security_overview(user: User = Depends(require_platform_admin), db: Session = Depends(get_db)):
    active_admins = db.scalar(select(func.count()).select_from(User).where(User.role.in_(PLATFORM_ADMIN_ROLES), User.account_status == "active")) or 0
    active_sessions = db.scalar(select(func.count()).select_from(AuthSession).join(User, User.id == AuthSession.user_id).where(User.role.in_(PLATFORM_ADMIN_ROLES), User.account_status == "active", AuthSession.revoked_at.is_(None), AuthSession.expires_at > now())) or 0
    since = now() - timedelta(hours=24)
    failed_logins = db.scalar(select(func.count()).select_from(SecurityAuditLog).where(SecurityAuditLog.event == "login_failed", SecurityAuditLog.created_at >= since)) or 0
    denied_requests = db.scalar(select(func.count()).select_from(SecurityAuditLog).where(SecurityAuditLog.event.in_(["authorization_denied", "access_denied"]), SecurityAuditLog.created_at >= since)) or 0
    role_changes = db.scalar(select(func.count()).select_from(AdminAuditLog).where(AdminAuditLog.action.in_(["platform_role_assigned", "platform_role_revoked"]), AdminAuditLog.created_at >= since)) or 0
    alert_rules = db.scalar(select(func.count()).select_from(SecurityAlertRule).where(SecurityAlertRule.organization_id.is_(None), SecurityAlertRule.enabled.is_(True))) or 0
    open_alerts = db.scalar(select(func.count()).select_from(SecurityAlertEvent).where(SecurityAlertEvent.organization_id.is_(None), SecurityAlertEvent.status.in_(["open", "investigating"]))) or 0
    recent = db.execute(select(AdminAuditLog, User).outerjoin(User, User.id == AdminAuditLog.actor_id).order_by(AdminAuditLog.created_at.desc()).limit(8)).all()
    return {
        "status": "available",
        "data_source": "database security and authentication records",
        "metrics": {
            "active_admin_assignments": active_admins,
            "active_admin_sessions": active_sessions,
            "failed_logins_24h": failed_logins,
            "denied_requests_24h": denied_requests,
            "role_changes_24h": role_changes,
            "unresolved_alerts": open_alerts if alert_rules else None,
        },
        "metric_states": {
            "failed_logins_24h": "recorded" if failed_logins else "no_events_recorded",
            "denied_requests_24h": "recorded" if denied_requests else "no_events_recorded",
            "unresolved_alerts": "recorded" if alert_rules else "not_configured",
        },
        "capabilities": {
            "roles": "available",
            "audit_logs": "available",
            "security_events": "available",
            "alerts": "available" if alert_rules else "not_configured",
            "admin_mfa": "configured" if settings.webauthn_enabled else "not_configured",
        },
        "recent_privileged_actions": [
            {"id": row.id, "action": row.action, "entity_type": row.entity_type, "entity_id": row.entity_id, "actor": _actor_name(actor), "created_at": row.created_at}
            for row, actor in recent
        ],
        "viewer": {"id": user.id, "role": user.role},
    }


@router.get("/roles")
def security_roles(user: User = Depends(require_platform_admin), db: Session = Depends(get_db)):
    counts = dict(db.execute(select(User.role, func.count()).group_by(User.role)).all())
    return {"items": [{"key": role, **ROLE_DEFINITIONS[role], "assignment_count": counts.get(role, 0), "permissions": [permission for permission, _, roles in PERMISSION_DEFINITIONS if role in roles]} for role in ROLE_ORDER], "data_source": "users.role and server permission registry", "viewer_role": user.role}


@router.get("/permissions")
def security_permissions(user: User = Depends(require_platform_admin)):
    return {"items": [{"key": key, "description": description, "roles": list(roles)} for key, description, roles in PERMISSION_DEFINITIONS], "viewer_role": user.role}


@router.get("/assignments")
def security_assignments(
    search: str | None = None,
    role: str | None = Query(default=None, pattern=r"^(student|content_editor|content_reviewer|instructor|moderator|admin|platform_admin|super_admin)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    _: User = Depends(require_platform_admin),
    db: Session = Depends(get_db),
):
    query = select(User)
    count = select(func.count()).select_from(User)
    conditions = []
    if search:
        pattern = f"%{search.strip()}%"
        conditions.append(or_(User.email.ilike(pattern), User.display_name.ilike(pattern), User.role.ilike(pattern)))
    if role:
        conditions.append(User.role == role)
    if conditions:
        query = query.where(*conditions)
        count = count.where(*conditions)
    total = db.scalar(count) or 0
    rows = db.scalars(query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [_assignment(row) for row in rows], **_page(page, page_size, total)}


@router.post("/assignments", status_code=201)
def assign_role(payload: RoleAssignmentIn, request: Request, actor: User = Depends(require_super_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    target = db.get(User, payload.user_id)
    if not target:
        raise HTTPException(404, "User not found")
    if target.id == actor.id:
        raise HTTPException(409, "You cannot change your own platform role")
    if payload.role == "super_admin" and actor.role != "super_admin":
        raise HTTPException(403, "Only a platform super administrator can grant super administrator access")
    previous_role = target.role
    if previous_role == payload.role:
        return {"assignment": _assignment(target), "changed": False}
    if previous_role == "super_admin" and payload.role != "super_admin":
        remaining = db.scalar(select(func.count()).select_from(User).where(User.role == "super_admin", User.account_status == "active", User.id != target.id)) or 0
        if remaining < 1:
            raise HTTPException(409, "The last active platform super administrator cannot be removed")
    target.role = payload.role
    _record_privileged_action(db, actor, request, "platform_role_assigned", "user", target.id, {"previous_role": previous_role, "new_role": payload.role})
    db.commit()
    db.refresh(target)
    return {"assignment": _assignment(target), "changed": True}


@router.delete("/assignments/{user_id}")
def revoke_role(user_id: UUID, request: Request, actor: User = Depends(require_super_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(404, "User not found")
    if target.id == actor.id:
        raise HTTPException(409, "You cannot revoke your own platform role")
    if target.role == "super_admin":
        remaining = db.scalar(select(func.count()).select_from(User).where(User.role == "super_admin", User.account_status == "active", User.id != target.id)) or 0
        if remaining < 1:
            raise HTTPException(409, "The last active platform super administrator cannot be removed")
    previous_role = target.role
    target.role = "student"
    _record_privileged_action(db, actor, request, "platform_role_revoked", "user", target.id, {"previous_role": previous_role, "new_role": "student"})
    db.commit()
    return {"status": "revoked", "user_id": target.id, "previous_role": previous_role}


@router.get("/audit-logs")
def security_audit_logs(
    search: str | None = None,
    action: str | None = None,
    actor_id: UUID | None = None,
    outcome: str | None = Query(default=None, pattern=r"^(success|denied|failure)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    _: User = Depends(require_platform_admin),
    db: Session = Depends(get_db),
):
    query = select(AdminAuditLog, User).outerjoin(User, User.id == AdminAuditLog.actor_id)
    count = select(func.count()).select_from(AdminAuditLog)
    conditions = []
    if search:
        pattern = f"%{search.strip()}%"
        conditions.append(or_(AdminAuditLog.action.ilike(pattern), AdminAuditLog.entity_type.ilike(pattern)))
    if action:
        conditions.append(AdminAuditLog.action == action)
    if actor_id:
        conditions.append(AdminAuditLog.actor_id == actor_id)
    if outcome:
        conditions.append(AdminAuditLog.metadata_json.ilike(f'%"outcome": "{outcome}"%'))
    if conditions:
        query = query.where(*conditions)
        count = count.where(*conditions)
    total = db.scalar(count) or 0
    rows = db.execute(query.order_by(AdminAuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [{"id": row.id, "action": row.action, "entity_type": row.entity_type, "entity_id": row.entity_id, "actor": _actor_name(actor), "outcome": _safe_json(row.metadata_json).get("outcome", "success"), "correlation_id": _safe_json(row.metadata_json).get("request_id"), "metadata": {key: value for key, value in _safe_json(row.metadata_json).items() if key not in {"request_id", "outcome"}}, "created_at": row.created_at} for row, actor in rows], **_page(page, page_size, total)}


@router.get("/events")
def security_events(
    event: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    _: User = Depends(require_platform_admin),
    db: Session = Depends(get_db),
):
    query = select(SecurityAuditLog, User).outerjoin(User, User.id == SecurityAuditLog.user_id)
    count = select(func.count()).select_from(SecurityAuditLog)
    if event:
        query = query.where(SecurityAuditLog.event == event)
        count = count.where(SecurityAuditLog.event == event)
    total = db.scalar(count) or 0
    rows = db.execute(query.order_by(SecurityAuditLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [{"id": row.id, "event": row.event, "actor": _actor_name(actor), "ip_address": row.ip_address, "correlation_id": _safe_json(row.metadata_json).get("request_id"), "metadata": {key: value for key, value in _safe_json(row.metadata_json).items() if key != "request_id"}, "created_at": row.created_at} for row, actor in rows], **_page(page, page_size, total)}


@router.get("/alerts")
def security_alerts(_: User = Depends(require_platform_admin), db: Session = Depends(get_db)):
    rules = db.scalars(select(SecurityAlertRule).where(SecurityAlertRule.organization_id.is_(None))).all()
    if not rules:
        return {"status": "not_configured", "data_source": "security_alert_rules", "items": [], "message": "No platform security alert rules are configured."}
    rows = db.scalars(select(SecurityAlertEvent).where(SecurityAlertEvent.organization_id.is_(None)).order_by(SecurityAlertEvent.created_at.desc()).limit(100)).all()
    return {"status": "available", "data_source": "security_alert_events", "items": [{"id": row.id, "rule_id": row.rule_id, "severity": row.severity, "status": row.status, "metadata": _safe_json(row.metadata_json), "created_at": row.created_at} for row in rows]}


@router.get("/policies")
def get_security_policy(_: User = Depends(require_platform_admin), db: Session = Depends(get_db)):
    return {"status": "available", "data_source": "platform_settings", "key": SECURITY_POLICY_KEY, "policy": _policy(db), "mfa_provider": "configured" if settings.webauthn_enabled else "not_configured"}


@router.patch("/policies")
def update_security_policy(payload: SecurityPolicyPatch, request: Request, actor: User = Depends(require_super_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    current = _policy(db)
    changes = payload.model_dump(exclude_none=True)
    if changes.get("require_admin_mfa") and not settings.webauthn_enabled:
        raise HTTPException(409, "Administrative MFA cannot be required until a supported MFA provider is configured")
    current.update(changes)
    row = db.scalar(select(PlatformSetting).where(PlatformSetting.key == SECURITY_POLICY_KEY))
    if row:
        row.value_json = json.dumps(current, sort_keys=True)
        row.updated_by = actor.id
    else:
        db.add(PlatformSetting(key=SECURITY_POLICY_KEY, value_json=json.dumps(current, sort_keys=True), updated_by=actor.id))
    _record_privileged_action(db, actor, request, "security_policy_updated", "platform_security_policy", metadata={"changed_fields": sorted(changes)})
    db.commit()
    return {"status": "saved", "policy": current}


@router.get("/sessions")
def platform_security_sessions(
    session_token: str | None = Cookie(default=None, alias=SESSION_COOKIE),
    _: User = Depends(require_platform_admin),
    db: Session = Depends(get_db),
):
    current_hash = hash_token(session_token) if session_token else None
    rows = db.execute(select(AuthSession, User).join(User, User.id == AuthSession.user_id).where(User.role.in_(PLATFORM_ADMIN_ROLES)).order_by(AuthSession.created_at.desc()).limit(100)).all()
    return {"items": [{"id": session.id, "user": _actor_name(user), "created_at": session.created_at, "expires_at": session.expires_at, "revoked": bool(session.revoked_at), "current": session.token_hash == current_hash, "active": session.revoked_at is None and session.expires_at > now()} for session, user in rows]}


@router.post("/sessions/{session_id}/revoke")
def revoke_platform_session(session_id: UUID, request: Request, actor: User = Depends(require_super_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.scalar(select(AuthSession).join(User, User.id == AuthSession.user_id).where(AuthSession.id == session_id, User.role.in_(PLATFORM_ADMIN_ROLES)))
    if not row:
        raise HTTPException(404, "Administrator session not found")
    if row.revoked_at:
        return {"status": "already_revoked"}
    row.revoked_at = now()
    _record_privileged_action(db, actor, request, "administrator_session_revoked", "auth_session", row.id)
    db.commit()
    return {"status": "revoked", "session_id": row.id}
