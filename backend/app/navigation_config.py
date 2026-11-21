"""Safe persistence and validation helpers for public navigation.

Navigation remains stored in PlatformSetting so the migration is additive and
does not create a second content table.  The legacy ``navigation`` key is
read-only fallback data; new edits use draft/published keys.
"""

import json
from urllib.parse import urlparse

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import PlatformSetting
from .schemas import NavigationSettings

NAVIGATION_KEY = "navigation"
NAVIGATION_DRAFT_KEY = "navigation:draft"
NAVIGATION_PUBLISHED_KEY = "navigation:published"

DEFAULT_NAVIGATION = {
    "status": "published",
    "items": [
        {"id": "courses", "label": "Courses", "href": "/courses", "enabled": True, "position": 0, "area": "header"},
        {"id": "projects", "label": "Projects", "href": "/projects", "enabled": True, "position": 1, "area": "header"},
        {"id": "challenges", "label": "Challenges", "href": "/challenges", "enabled": True, "position": 2, "area": "header"},
        {"id": "careers", "label": "Careers", "href": "/careers", "enabled": True, "position": 3, "area": "header"},
        {"id": "tools", "label": "Developer Tools", "href": "/tools", "enabled": True, "position": 4, "area": "header"},
    ],
}

ALLOWED_INTERNAL_PATHS = {
    "/", "/courses", "/projects", "/challenges", "/careers", "/careers/paths",
    "/careers/resume", "/careers/interview", "/careers/jobs", "/careers/assessments",
    "/careers/portfolio", "/careers/my-plan", "/tools", "/about", "/contact", "/privacy",
    "/terms", "/login", "/dashboard", "/profile", "/achievements",
}
ALLOWED_INTERNAL_PREFIXES = (
    "/courses/", "/projects/", "/challenges/", "/tools/", "/careers/paths/", "/careers/assessments/",
)


def _decode(row: PlatformSetting | None, fallback: NavigationSettings | None = None) -> NavigationSettings | None:
    if not row:
        return fallback
    try:
        value = json.loads(row.value_json or "{}")
        if not isinstance(value, dict):
            return fallback
        return NavigationSettings.model_validate(value)
    except (TypeError, ValueError, json.JSONDecodeError):
        return fallback


def default_navigation() -> NavigationSettings:
    return NavigationSettings.model_validate(DEFAULT_NAVIGATION)


def read_navigation(db: Session, key: str, *, public: bool = False) -> NavigationSettings:
    row = db.scalar(select(PlatformSetting).where(PlatformSetting.key == key))
    value = _decode(row)
    if value:
        return value
    if key == NAVIGATION_PUBLISHED_KEY:
        legacy = _decode(db.scalar(select(PlatformSetting).where(PlatformSetting.key == NAVIGATION_KEY)))
        if legacy:
            return legacy.model_copy(update={"status": "published"})
        return default_navigation() if public else NavigationSettings(items=[], status="published")
    return default_navigation() if public else NavigationSettings(items=[], status="published")


def read_admin_navigation(db: Session) -> NavigationSettings:
    draft = _decode(db.scalar(select(PlatformSetting).where(PlatformSetting.key == NAVIGATION_DRAFT_KEY)))
    if draft:
        return draft.model_copy(update={"status": "draft"})
    published = _decode(db.scalar(select(PlatformSetting).where(PlatformSetting.key == NAVIGATION_PUBLISHED_KEY)))
    if published:
        return published.model_copy(update={"status": "published"})
    legacy = _decode(db.scalar(select(PlatformSetting).where(PlatformSetting.key == NAVIGATION_KEY)))
    return legacy.model_copy(update={"status": "published"}) if legacy else NavigationSettings(items=[], status="published")


def validate_navigation(payload: NavigationSettings) -> NavigationSettings:
    ids: set[str] = set()
    parent_ids: set[str] = set()
    for item in payload.items:
        if item.id in ids:
            raise HTTPException(422, "Navigation item IDs must be unique")
        ids.add(item.id)
        if item.area == "header" and item.parent_id:
            parent_ids.add(item.id)
        if item.link_type == "internal":
            path = item.href.split("?", 1)[0].split("#", 1)[0]
            if path not in ALLOWED_INTERNAL_PATHS and not path.startswith(ALLOWED_INTERNAL_PREFIXES):
                raise HTTPException(422, f"Invalid internal navigation destination: {item.href}")
        else:
            parsed = urlparse(item.external_url or item.href)
            if parsed.scheme != "https" or not parsed.hostname:
                raise HTTPException(422, "External navigation links must use HTTPS")
    for item in payload.items:
        if item.parent_id:
            if item.parent_id not in ids:
                raise HTTPException(422, "Navigation parent does not exist")
            if item.parent_id == item.id:
                raise HTTPException(422, "Navigation items cannot be their own parent")
            parent = next(value for value in payload.items if value.id == item.parent_id)
            if parent.parent_id:
                raise HTTPException(422, "Navigation supports one level of dropdown nesting")
            if parent.area != item.area:
                raise HTTPException(422, "Navigation parent and child must use the same area")
    return payload


def save_navigation(db: Session, user_id, key: str, payload: NavigationSettings) -> NavigationSettings:
    values = payload.model_dump(mode="json")
    row = db.scalar(select(PlatformSetting).where(PlatformSetting.key == key))
    if row:
        row.value_json = json.dumps(values)
        row.updated_by = user_id
    else:
        db.add(PlatformSetting(key=key, value_json=json.dumps(values), updated_by=user_id))
    return NavigationSettings.model_validate(values)
