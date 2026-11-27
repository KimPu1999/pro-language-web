"""Typed, database-backed platform configuration.

Only fields declared in ``GROUP_SCHEMAS`` are writable.  Deployment secrets
remain in ``Settings`` and are represented by status-only integration data.
"""

import json
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from .config import settings
from .models import AdminAuditLog, PlatformSetting, PlatformSettingHistory, User
from .schemas import (
    BrandingSettings,
    PlatformEmailSettings,
    PlatformGeneralSettings,
    PlatformLanguageSettings,
    PlatformLearningSettings,
    PlatformMediaSettings,
    PlatformRegistrationSettings,
    PlatformSeoSettings,
)

GROUP_SCHEMAS = {
    "general": ("platform:general", PlatformGeneralSettings),
    "branding": ("branding", BrandingSettings),
    "languages": ("platform:languages", PlatformLanguageSettings),
    "seo": ("platform:seo", PlatformSeoSettings),
    "registration": ("platform:registration", PlatformRegistrationSettings),
    "email": ("platform:email", PlatformEmailSettings),
    "media": ("platform:media", PlatformMediaSettings),
    "learning": ("platform:learning", PlatformLearningSettings),
}
READ_ONLY_GROUPS = {"integrations", "system"}
_cache: dict[str, tuple[int, dict[str, Any]]] = {}


def _json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def _safe_load(row: PlatformSetting | None) -> dict[str, Any]:
    if not row:
        return {}
    try:
        value = json.loads(row.value_json or "{}")
        return value if isinstance(value, dict) else {}
    except (TypeError, ValueError, json.JSONDecodeError):
        return {}


def _schema_for(group: str):
    if group not in GROUP_SCHEMAS:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Unknown settings group")
    return GROUP_SCHEMAS[group][1]


def _defaults(group: str):
    return _schema_for(group)()


def _row(db: Session, group: str) -> PlatformSetting | None:
    key = GROUP_SCHEMAS[group][0]
    return db.scalar(select(PlatformSetting).where(PlatformSetting.key == key))


def _record(group: str, db: Session) -> dict[str, Any]:
    schema = _schema_for(group)
    row = _row(db, group)
    values = schema.model_validate({**schema().model_dump(mode="json"), **_safe_load(row)})
    version = row.version if row else 0
    cached = _cache.get(group)
    if cached and cached[0] == version:
        values_json = cached[1]
    else:
        values_json = values.model_dump(mode="json")
        _cache[group] = (version, values_json)
    return {
        "group": group,
        "status": "configured" if row else "default",
        "version": version,
        "values": values_json,
        "updated_at": row.updated_at if row else None,
        "updated_by": str(row.updated_by) if row and row.updated_by else None,
    }


def integration_status() -> dict[str, Any]:
    return {
        "group": "integrations",
        "status": "configured",
        "values": {
            "database": {"configured": True, "status": "live query"},
            "media_storage": {"configured": True, "status": "filesystem-backed"},
            "email": {"configured": settings.mailer_mode != "console", "status": settings.mailer_mode},
            "runner": {"configured": settings.runner_enabled, "status": "enabled" if settings.runner_enabled else "disabled"},
            "ai": {"configured": settings.ai_enabled, "status": settings.ai_provider if settings.ai_enabled else "disabled"},
            "video": {"configured": settings.video_enabled, "status": settings.video_provider if settings.video_enabled else "disabled"},
            "github": {"configured": settings.github_enabled, "status": "enabled" if settings.github_enabled else "disabled"},
            "oidc": {"configured": settings.oidc_enabled, "status": "enabled" if settings.oidc_enabled else "disabled"},
            "saml": {"configured": settings.saml_enabled, "status": "enabled" if settings.saml_enabled else "disabled"},
            "webauthn": {"configured": settings.webauthn_enabled, "status": "enabled" if settings.webauthn_enabled else "disabled"},
            "scim": {"configured": settings.scim_enabled, "status": "enabled" if settings.scim_enabled else "disabled"},
        },
        "updated_at": None,
        "version": 0,
    }


def system_status() -> dict[str, Any]:
    return {
        "group": "system",
        "status": "configured",
        "version": 0,
        "updated_at": None,
        "values": {
            "environment": settings.app_env,
            "api_version": "1.0.0",
            "media_root_configured": bool(settings.media_root),
            "cache": "in-process versioned cache",
            "secrets_source": "deployment environment",
        },
    }


def list_settings(db: Session) -> dict[str, Any]:
    groups = {group: _record(group, db) for group in GROUP_SCHEMAS}
    groups["integrations"] = integration_status()
    groups["system"] = system_status()
    return {
        "groups": groups,
        "data_source": "postgresql",
        "cache_policy": "versioned and invalidated after successful save",
        "permissions": {"read": True, "update": True},
    }


def get_settings_group(db: Session, group: str) -> dict[str, Any]:
    if group in READ_ONLY_GROUPS:
        return integration_status() if group == "integrations" else system_status()
    return _record(group, db)


def save_settings_group(
    db: Session,
    actor: User,
    group: str,
    values: dict[str, Any],
    expected_version: int,
    change_reason: str,
    correlation_id: str | None,
) -> dict[str, Any]:
    if group in READ_ONLY_GROUPS:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This settings group is deployment-controlled")
    schema = _schema_for(group)
    allowed = set(schema.model_fields)
    unknown = sorted(set(values) - allowed)
    if unknown:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"Unknown settings key(s): {', '.join(unknown)}")
    key = GROUP_SCHEMAS[group][0]
    row = db.scalar(select(PlatformSetting).where(PlatformSetting.key == key).with_for_update())
    current_values = {**schema().model_dump(mode="json"), **_safe_load(row)}
    current_version = row.version if row else 0
    if expected_version != current_version:
        raise HTTPException(status.HTTP_409_CONFLICT, {"message": "Settings changed by another administrator", "current_version": current_version})
    validated = schema.model_validate({**current_values, **values})
    previous_json = _json(current_values)
    next_json = _json(validated.model_dump(mode="json"))
    if row:
        row.value_json = next_json
        row.updated_by = actor.id
        row.category = group
        row.version = current_version + 1
    else:
        row = PlatformSetting(key=key, scope="platform", category=group, version=1, value_json=next_json, updated_by=actor.id)
        db.add(row)
        current_version = 0
    next_version = current_version + 1
    db.add(PlatformSettingHistory(setting_key=key, category=group, version=next_version, previous_value_json=previous_json, new_value_json=next_json, actor_id=actor.id, change_reason=change_reason.strip()[:240], correlation_id=correlation_id, outcome="success"))
    db.add(AdminAuditLog(actor_id=actor.id, action="platform_setting_updated", entity_type="platform_setting", entity_id=row.id, metadata_json=_json({"category": group, "keys": sorted(values), "version": next_version, "correlation_id": correlation_id})))
    db.flush()
    _cache.pop(group, None)
    return _record(group, db)


def history(db: Session, page: int, page_size: int, group: str | None = None) -> dict[str, Any]:
    from sqlalchemy import func
    conditions = []
    if group:
        if group not in GROUP_SCHEMAS:
            raise HTTPException(status.HTTP_404_NOT_FOUND, "Unknown settings group")
        conditions.append(PlatformSettingHistory.category == group)
    query = select(PlatformSettingHistory)
    count_query = select(func.count()).select_from(PlatformSettingHistory)
    if conditions:
        query = query.where(*conditions)
        count_query = count_query.where(*conditions)
    total = db.scalar(count_query) or 0
    rows = db.scalars(query.order_by(PlatformSettingHistory.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return {
        "items": [{"id": str(row.id), "group": row.category, "setting_key": row.setting_key, "version": row.version, "previous": json.loads(row.previous_value_json), "new": json.loads(row.new_value_json), "actor_id": str(row.actor_id) if row.actor_id else None, "change_reason": row.change_reason, "correlation_id": row.correlation_id, "outcome": row.outcome, "created_at": row.created_at} for row in rows],
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": max(1, (total + page_size - 1) // page_size),
    }


def public_config(db: Session) -> dict[str, Any]:
    general = _record("general", db)["values"]
    branding = _record("branding", db)["values"]
    languages = _record("languages", db)["values"]
    seo = _record("seo", db)["values"]
    return {
        "website": {"name": general["website_name"], "tagline": general["website_tagline"], "description": general["website_description"], "site_url": general["site_url"]},
        "branding": {"logo_url": branding["logo_url"], "mobile_logo_url": branding["mobile_logo_url"], "favicon_url": branding["favicon_url"], "primary_color": branding["primary_color"], "header_background": branding["header_background"]},
        "languages": languages,
        "seo": {"default_title": seo["default_title"], "meta_description": seo["meta_description"], "open_graph_title": seo["open_graph_title"], "open_graph_description": seo["open_graph_description"], "open_graph_image": seo["open_graph_image"], "canonical_url": seo["canonical_url"], "robots_indexing": seo["robots_indexing"], "sitemap_enabled": seo["sitemap_enabled"], "locale_metadata": seo["locale_metadata"]},
    }
