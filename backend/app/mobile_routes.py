"""Mobile/offline learning boundary.

Only published course content is packaged. Authenticated API responses are
never placed in the service-worker cache; offline records are account-scoped
and lesson completion is reconciled as ordinary progress, never as grading.
"""
import json
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, HttpUrl
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from .auth import current_user, require_csrf, verified_user
from .db import get_db
from .models import (
    Course, CourseModule, Lesson, LessonProgress, MobileDeviceRegistration,
    MobileLearningPreference, MobileNotificationPreference, MobilePushSubscription, OfflineContentBookmark, OfflineContentManifest,
    OfflineDownloadPolicy, OfflineLearningActivity,
    OfflineSyncConflict, OfflineSyncEvent, User,
)
from .rbac import require_platform_admin

router = APIRouter(prefix="/api/v1/mobile", tags=["mobile"])

class DeviceIn(BaseModel):
    device_id: str = Field(min_length=8, max_length=180)
    platform: str = Field(min_length=2, max_length=30)
class ManifestIn(BaseModel):
    course_id: UUID
class SyncEventIn(BaseModel):
    event_id: str = Field(min_length=8, max_length=180)
    event_type: str = Field(pattern=r"^(lesson_progress|bookmark|activity)$")
    lesson_id: UUID | None = None
    content_version: str | None = Field(default=None, max_length=80)
    payload: dict = Field(default_factory=dict)
class SyncIn(BaseModel):
    events: list[SyncEventIn] = Field(max_length=100)
class PushIn(BaseModel):
    endpoint: HttpUrl
    keys: dict[str, str]
class PushRemoveIn(BaseModel):
    endpoint: HttpUrl
class PreferenceIn(BaseModel):
    language: str = Field(default="en", pattern=r"^(en|mm)$")
    reduced_data: bool = False
    reduced_motion: bool = False
    text_scale: int = Field(default=100, ge=80, le=200)
class NotificationIn(BaseModel):
    enabled: bool = False
    quiet_hours: dict = Field(default_factory=dict)
    categories: list[str] = Field(default_factory=list, max_length=12)

def course_version(course: Course) -> str:
    return (course.updated_at or course.created_at or datetime.now(timezone.utc)).isoformat()

def lesson_json(lesson: Lesson) -> dict:
    return {"id": str(lesson.id), "title": lesson.title, "slug": lesson.slug, "content_en": lesson.content_en, "content_mm": lesson.content_mm, "duration_minutes": lesson.duration_minutes, "updated_at": lesson.updated_at.isoformat() if lesson.updated_at else None, "code_examples": [{"title": x.title, "language": x.language, "code": x.code, "description": x.description} for x in lesson.code_examples]}

@router.get("/dashboard")
def dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)):
    manifests = db.scalars(select(OfflineContentManifest).where(OfflineContentManifest.user_id == user.id).order_by(OfflineContentManifest.updated_at.desc()).limit(10)).all()
    pending = db.scalar(select(func.count()).select_from(OfflineSyncEvent).where(OfflineSyncEvent.user_id == user.id, OfflineSyncEvent.status == "pending")) or 0
    pref = db.scalar(select(MobileLearningPreference).where(MobileLearningPreference.user_id == user.id))
    return {"downloaded_courses": len([x for x in manifests if x.status == "ready"]), "downloads": [{"id": str(x.id), "course_id": str(x.course_id), "status": x.status, "content_version": x.content_version, "size_bytes": x.size_bytes} for x in manifests], "pending_sync": pending, "preferences": {"language": pref.language if pref else "en", "reduced_data": pref.reduced_data if pref else False}, "offline_grading": False, "data_source": "postgresql"}

@router.get("/library")
def library(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(OfflineContentManifest).where(OfflineContentManifest.user_id == user.id).order_by(OfflineContentManifest.updated_at.desc())).all()
    return {"items": [{"id": str(x.id), "course_id": str(x.course_id), "status": x.status, "content_version": x.content_version, "size_bytes": x.size_bytes} for x in rows]}

@router.post("/manifests", status_code=201)
def create_manifest(payload: ManifestIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    course = db.scalar(select(Course).where(Course.id == payload.course_id, Course.published.is_(True)))
    if not course:
        raise HTTPException(404, "Published course not found")
    policy = db.scalar(select(OfflineDownloadPolicy).where(OfflineDownloadPolicy.course_id == course.id))
    if policy and not policy.enabled:
        raise HTTPException(403, "Offline downloads are disabled for this course")
    existing = db.scalar(select(OfflineContentManifest).where(OfflineContentManifest.user_id == user.id, OfflineContentManifest.course_id == course.id))
    if existing:
        existing.content_version = course_version(course); existing.status = "ready"; db.commit()
        return {"id": str(existing.id), "status": existing.status, "content_version": existing.content_version}
    manifest = OfflineContentManifest(user_id=user.id, course_id=course.id, content_version=course_version(course), status="ready")
    db.add(manifest); db.commit()
    return {"id": str(manifest.id), "status": manifest.status, "content_version": manifest.content_version}

@router.get("/manifests/{manifest_id}/content")
def manifest_content(manifest_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    manifest = db.scalar(select(OfflineContentManifest).where(OfflineContentManifest.id == manifest_id, OfflineContentManifest.user_id == user.id))
    if not manifest:
        raise HTTPException(404, "Offline manifest not found")
    course = db.scalar(select(Course).options(selectinload(Course.modules).selectinload(CourseModule.lessons).selectinload(Lesson.code_examples)).where(Course.id == manifest.course_id, Course.published.is_(True)))
    if not course:
        raise HTTPException(410, "Course is no longer available offline")
    lessons = [lesson_json(lesson) for module in sorted(course.modules, key=lambda x: x.order_index) for lesson in sorted(module.lessons, key=lambda x: x.order_index) if lesson.published]
    return {"manifest_id": str(manifest.id), "course_id": str(course.id), "title": course.title, "slug": course.slug, "content_version": course_version(course), "lessons": lessons, "verified_offline": False}

@router.post("/sync")
def sync(payload: SyncIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    results = []
    for item in payload.events:
        existing = db.scalar(select(OfflineSyncEvent).where(OfflineSyncEvent.user_id == user.id, OfflineSyncEvent.event_id == item.event_id))
        if existing:
            results.append({"event_id": item.event_id, "status": existing.status}); continue
        lesson = db.scalar(select(Lesson).where(Lesson.id == item.lesson_id, Lesson.published.is_(True))) if item.lesson_id else None
        event = OfflineSyncEvent(user_id=user.id, event_id=item.event_id, event_type=item.event_type, lesson_id=item.lesson_id, content_version=item.content_version, payload_json=json.dumps(item.payload))
        db.add(event); db.flush()
        if item.lesson_id and not lesson:
            event.status = "conflict"; db.add(OfflineSyncConflict(sync_event_id=event.id, user_id=user.id, reason="deleted_or_unpublished_lesson", detail="The lesson is no longer available.")); results.append({"event_id": item.event_id, "status": event.status}); continue
        if lesson and item.content_version and lesson.updated_at and item.content_version != lesson.updated_at.isoformat():
            event.status = "conflict"; db.add(OfflineSyncConflict(sync_event_id=event.id, user_id=user.id, reason="content_version_mismatch", detail="Refresh the course before retrying this event.")); results.append({"event_id": item.event_id, "status": event.status}); continue
        if item.event_type == "lesson_progress" and lesson and bool(item.payload.get("completed")):
            progress = db.scalar(select(LessonProgress).where(LessonProgress.user_id == user.id, LessonProgress.lesson_id == lesson.id))
            if progress: progress.completed = True
            else: db.add(LessonProgress(user_id=user.id, lesson_id=lesson.id, completed=True))
        if item.event_type == "bookmark" and lesson:
            bookmark = db.scalar(select(OfflineContentBookmark).where(OfflineContentBookmark.user_id == user.id, OfflineContentBookmark.lesson_id == lesson.id))
            if not bookmark: db.add(OfflineContentBookmark(user_id=user.id, lesson_id=lesson.id, note=str(item.payload.get("note", ""))[:500]))
        if lesson: db.add(OfflineLearningActivity(user_id=user.id, event_type=item.event_type, lesson_id=lesson.id))
        event.status = "applied"; event.processed_at = datetime.now(timezone.utc); results.append({"event_id": item.event_id, "status": event.status})
    db.commit()
    return {"items": results, "verified_grading": False}

@router.get("/preferences")
def preferences(user: User = Depends(current_user), db: Session = Depends(get_db)):
    row = db.scalar(select(MobileLearningPreference).where(MobileLearningPreference.user_id == user.id))
    return {"language": row.language if row else "en", "reduced_data": row.reduced_data if row else False, "reduced_motion": row.reduced_motion if row else False, "text_scale": row.text_scale if row else 100}

@router.put("/preferences")
def update_preferences(payload: PreferenceIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.scalar(select(MobileLearningPreference).where(MobileLearningPreference.user_id == user.id))
    if not row: row = MobileLearningPreference(user_id=user.id); db.add(row)
    row.language = payload.language; row.reduced_data = payload.reduced_data; row.reduced_motion = payload.reduced_motion; row.text_scale = payload.text_scale; db.commit()
    return preferences(user, db)

@router.get("/notifications")
def notification_preferences(user: User = Depends(current_user), db: Session = Depends(get_db)):
    row = db.scalar(select(MobileNotificationPreference).where(MobileNotificationPreference.user_id == user.id))
    return {"enabled": row.enabled if row else False, "quiet_hours": json.loads(row.quiet_hours_json) if row else {}, "categories": json.loads(row.categories_json) if row else [], "provider": "not_configured"}

@router.put("/notifications")
def update_notification_preferences(payload: NotificationIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.scalar(select(MobileNotificationPreference).where(MobileNotificationPreference.user_id == user.id))
    if not row: row = MobileNotificationPreference(user_id=user.id); db.add(row)
    row.enabled = payload.enabled; row.quiet_hours_json = json.dumps(payload.quiet_hours); row.categories_json = json.dumps(payload.categories); db.commit()
    return {"enabled": row.enabled, "quiet_hours": payload.quiet_hours, "categories": payload.categories, "provider": "not_configured"}

@router.post("/push-subscriptions", status_code=201)
def register_push(payload: PushIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if not payload.keys.get("p256dh") or not payload.keys.get("auth") or len(payload.keys) > 3: raise HTTPException(422, "Invalid push subscription keys")
    endpoint = str(payload.endpoint); row = db.scalar(select(MobilePushSubscription).where(MobilePushSubscription.user_id == user.id, MobilePushSubscription.endpoint == endpoint))
    if row: row.p256dh = payload.keys["p256dh"]; row.auth = payload.keys["auth"]; row.active = True
    else: db.add(MobilePushSubscription(user_id=user.id, endpoint=endpoint, p256dh=payload.keys["p256dh"], auth=payload.keys["auth"]))
    db.commit(); return {"status": "registered", "provider": "not_configured"}

@router.delete("/push-subscriptions")
def unregister_push(payload: PushRemoveIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.scalar(select(MobilePushSubscription).where(MobilePushSubscription.user_id == user.id, MobilePushSubscription.endpoint == str(payload.endpoint)))
    if row: row.active = False; db.commit()
    return {"status": "unsubscribed"}

@router.post("/devices", status_code=201)
def register_device(payload: DeviceIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.scalar(select(MobileDeviceRegistration).where(MobileDeviceRegistration.user_id == user.id, MobileDeviceRegistration.device_id == payload.device_id))
    if not row: db.add(MobileDeviceRegistration(user_id=user.id, device_id=payload.device_id, platform=payload.platform))
    else: row.platform = payload.platform; row.last_seen_at = datetime.now(timezone.utc)
    db.commit(); return {"status": "registered"}

@router.get("/instructor/offline-settings")
def instructor_settings(user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role not in {"instructor", "admin", "platform_admin", "super_admin"}: raise HTTPException(403, "Instructor permission required")
    rows = db.scalars(select(OfflineDownloadPolicy).join(Course, Course.id == OfflineDownloadPolicy.course_id).where(Course.created_by == user.id)).all()
    return {"items": [{"course_id": str(x.course_id), "enabled": x.enabled, "max_age_days": x.max_age_days, "allow_images": x.allow_images} for x in rows], "status": "policy_records_only"}

@router.get("/platform/operations")
def platform_operations(user: User = Depends(require_platform_admin), db: Session = Depends(get_db)):
    return {"manifests": db.scalar(select(func.count()).select_from(OfflineContentManifest)) or 0, "sync_events": db.scalar(select(func.count()).select_from(OfflineSyncEvent)) or 0, "conflicts": db.scalar(select(func.count()).select_from(OfflineSyncConflict).where(OfflineSyncConflict.resolved_at.is_(None))) or 0, "push_subscriptions": db.scalar(select(func.count()).select_from(MobilePushSubscription).where(MobilePushSubscription.active.is_(True))) or 0, "push_provider": "not_configured", "service_worker": "client_configured", "data_source": "postgresql"}
