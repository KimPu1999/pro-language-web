import json
from urllib.parse import urlparse

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from .models import PlatformSetting
from .schemas import FooterSettings

FOOTER_KEY = "footer"
FOOTER_DRAFT_KEY = "footer_draft"

DEFAULT_FOOTER = {
    "tagline": "Learn to code. Build your future.",
    "description": "Practical coding education, projects, and tools for your next step.",
    "groups": [
        {"id": "learn", "title": "Learn", "position": 0, "enabled": True, "links": [
            {"id": "courses", "label": "Courses", "href": "/courses", "position": 0, "enabled": True},
            {"id": "projects", "label": "Projects", "href": "/projects", "position": 1, "enabled": True},
            {"id": "challenges", "label": "Challenges", "href": "/challenges", "position": 2, "enabled": True},
            {"id": "learning-paths", "label": "Learning Paths", "href": "/careers/paths", "position": 3, "enabled": True},
        ]},
        {"id": "careers", "title": "Careers", "position": 1, "enabled": True, "links": [
            {"id": "career-paths", "label": "Career Paths", "href": "/careers/paths", "position": 0, "enabled": True},
            {"id": "resume-builder", "label": "Resume Builder", "href": "/careers/resume", "position": 1, "enabled": True},
            {"id": "interview-preparation", "label": "Interview Preparation", "href": "/careers/interview", "position": 2, "enabled": True},
        ]},
        {"id": "tools", "title": "Tools", "position": 2, "enabled": True, "links": [
            {"id": "developer-tools", "label": "Developer Tools", "href": "/tools", "position": 0, "enabled": True},
            {"id": "json-formatter", "label": "JSON Formatter", "href": "/tools/json-formatter", "position": 1, "enabled": True},
            {"id": "regex-tester", "label": "Regex Tester", "href": "/tools/regex-tester", "position": 2, "enabled": True},
            {"id": "code-playground", "label": "Code Playground", "href": "/tools/code-playground", "position": 3, "enabled": True},
        ]},
        {"id": "company", "title": "Company", "position": 3, "enabled": True, "links": [
            {"id": "about", "label": "About", "href": "/about", "position": 0, "enabled": True},
            {"id": "contact", "label": "Contact", "href": "/contact", "position": 1, "enabled": True},
        ]},
        {"id": "legal", "title": "Legal", "position": 4, "enabled": True, "links": [
            {"id": "privacy", "label": "Privacy Policy", "href": "/privacy", "position": 0, "enabled": True},
            {"id": "terms", "label": "Terms of Service", "href": "/terms", "position": 1, "enabled": True},
        ]},
    ],
    "social_links": [],
    "newsletter_enabled": False,
    "newsletter_note": "Newsletter sign-ups are not available yet.",
    "copyright_text": "© 2026 Learn-Coding. All rights reserved.",
    "status": "published",
}

ALLOWED_INTERNAL_PATHS = {
    "/", "/courses", "/projects", "/challenges", "/careers", "/careers/paths", "/careers/resume",
    "/careers/interview", "/careers/jobs", "/careers/assessments", "/careers/portfolio", "/careers/my-plan",
    "/tools", "/about", "/contact", "/privacy", "/terms", "/login", "/dashboard", "/profile", "/achievements",
}
ALLOWED_INTERNAL_PREFIXES = ("/courses/", "/projects/", "/challenges/", "/tools/", "/careers/paths/", "/careers/assessments/")

def default_footer() -> FooterSettings:
    return FooterSettings.model_validate(DEFAULT_FOOTER)

def _decode(value_json: str | None) -> FooterSettings | None:
    try:
        raw = json.loads(value_json or "{}")
        if not isinstance(raw, dict):
            return None
        return FooterSettings.model_validate({**DEFAULT_FOOTER, **raw})
    except (TypeError, ValueError, json.JSONDecodeError):
        return None

def read_footer(db: Session, key: str = FOOTER_KEY) -> FooterSettings:
    row = db.scalar(select(PlatformSetting).where(PlatformSetting.key == key))
    value = _decode(row.value_json if row else None)
    if value:
        return value
    if key == FOOTER_KEY:
        navigation = db.scalar(select(PlatformSetting).where(PlatformSetting.key == "navigation"))
        try:
            legacy_items = json.loads(navigation.value_json or "{}").get("items", []) if navigation else []
            footer_items = [item for item in legacy_items if item.get("area") == "footer" and item.get("enabled", True)]
            if footer_items:
                fallback = default_footer().model_dump(mode="json")
                fallback["groups"] = [{"id": "navigation", "title": "Explore", "position": 0, "enabled": True, "links": [
                    {"id": f"legacy-{index}", "label": item["label"], "href": item["href"], "position": index, "enabled": True} for index, item in enumerate(footer_items)
                ]}]
                return FooterSettings.model_validate(fallback)
        except (TypeError, ValueError, json.JSONDecodeError):
            pass
    return default_footer()

def validate_footer(payload: FooterSettings) -> FooterSettings:
    group_ids: set[str] = set()
    for group in payload.groups:
        if group.id in group_ids:
            raise HTTPException(422, "Footer group IDs must be unique")
        group_ids.add(group.id)
        link_ids: set[str] = set()
        for link in group.links:
            if link.id in link_ids:
                raise HTTPException(422, "Footer link IDs must be unique within a group")
            link_ids.add(link.id)
            if link.href.startswith("/"):
                path = link.href.split("?", 1)[0].split("#", 1)[0]
                if path not in ALLOWED_INTERNAL_PATHS and not path.startswith(ALLOWED_INTERNAL_PREFIXES):
                    raise HTTPException(422, f"Invalid internal footer destination: {link.href}")
            else:
                parsed = urlparse(link.href)
                if parsed.scheme != "https" or not parsed.hostname:
                    raise HTTPException(422, "External footer links must use HTTPS")
    social_ids: set[str] = set()
    for social in payload.social_links:
        if social.id in social_ids:
            raise HTTPException(422, "Social link IDs must be unique")
        social_ids.add(social.id)
        parsed = urlparse(social.url)
        if parsed.scheme != "https" or not parsed.hostname:
            raise HTTPException(422, "Social links must use HTTPS")
    return payload
