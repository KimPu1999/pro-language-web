"""Server-side, allowlisted eligibility and award issuance for achievements."""

import json
import secrets
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .models import (
    AchievementAuditEvent,
    AchievementAwardEvidence,
    AchievementDefinition,
    AssessmentAttempt,
    CareerRoadmap,
    Course,
    CourseModule,
    IssuedCertificate,
    LearningPathCourse,
    Lesson,
    LessonProgress,
    LessonQuiz,
    NotificationMessage,
    NotificationPreference,
    QuizAttempt,
    RoadmapStage,
    RoadmapStep,
    RoadmapStepResource,
    StudentAchievement,
    StudentProject,
    StudentRoadmap,
    User,
)

ALLOWED_RULE_TYPES = {
    "lesson_completion_count",
    "course_verified_completion",
    "quiz_passed",
    "approved_project_count",
    "learning_path_completion",
    "capstone_approved",
}
PUBLIC_STATUSES = {"published"}


def _json(value: str | None, fallback: dict[str, Any] | None = None) -> dict[str, Any]:
    try:
        parsed = json.loads(value or "{}")
        return parsed if isinstance(parsed, dict) else (fallback or {})
    except (TypeError, ValueError, json.JSONDecodeError):
        return fallback or {}


def _uuid(value: Any) -> UUID | None:
    try:
        return UUID(str(value)) if value else None
    except (TypeError, ValueError):
        return None


def _count_completed_lessons(db: Session, user_id: UUID, course_id: UUID | None = None) -> tuple[int, list[UUID]]:
    query = (
        select(LessonProgress.lesson_id)
        .join(Lesson, Lesson.id == LessonProgress.lesson_id)
        .join(CourseModule, CourseModule.id == Lesson.module_id)
        .join(Course, Course.id == CourseModule.course_id)
        .where(LessonProgress.user_id == user_id, LessonProgress.completed.is_(True), Lesson.published.is_(True), Course.published.is_(True))
    )
    if course_id:
        query = query.where(Course.id == course_id)
    ids = list(dict.fromkeys(db.scalars(query).all()))
    return len(ids), ids


def evaluate_definition(db: Session, user_id: UUID, definition: AchievementDefinition) -> dict[str, Any]:
    """Evaluate only known rule types against persisted, verified records."""
    config = _json(definition.rule_json)
    rule_type = definition.rule_type
    target = max(1, int(config.get("count", definition.threshold or 1)))
    evidence: list[dict[str, Any]] = []

    if rule_type == "lesson_completion_count":
        course_id = _uuid(config.get("course_id")) or definition.related_course_id
        current, lesson_ids = _count_completed_lessons(db, user_id, course_id)
        evidence = [{"type": "lesson_progress", "id": str(value)} for value in lesson_ids[:target]]
        return {"available": True, "current": current, "target": target, "evidence": evidence}

    if rule_type == "course_verified_completion":
        course_id = _uuid(config.get("course_id")) or definition.related_course_id
        query = select(IssuedCertificate).where(
            IssuedCertificate.user_id == user_id,
            IssuedCertificate.achievement_type == "course_completion",
            IssuedCertificate.revoked_at.is_(None),
        )
        if course_id:
            query = query.where(IssuedCertificate.resource_id == course_id)
        certificates = db.scalars(query.order_by(IssuedCertificate.issued_at)).all()
        evidence = [{"type": "course_certificate", "id": str(row.id)} for row in certificates[:1]]
        return {"available": True, "current": 1 if certificates else 0, "target": 1, "evidence": evidence}

    if rule_type == "quiz_passed":
        minimum = int(config.get("minimum_score", 70))
        query = select(QuizAttempt).where(QuizAttempt.user_id == user_id, QuizAttempt.total > 0, (QuizAttempt.score * 100) >= (QuizAttempt.total * minimum))
        lesson_id = _uuid(config.get("lesson_id"))
        if lesson_id:
            query = query.join(LessonQuiz, LessonQuiz.id == QuizAttempt.quiz_id).where(LessonQuiz.lesson_id == lesson_id)
        attempts = db.scalars(query.order_by(QuizAttempt.created_at)).all()
        assessment_query = select(AssessmentAttempt).where(AssessmentAttempt.user_id == user_id, AssessmentAttempt.score.is_not(None), AssessmentAttempt.score >= minimum, AssessmentAttempt.status.in_(["submitted", "graded"]))
        assessments = db.scalars(assessment_query.order_by(AssessmentAttempt.created_at)).all()
        evidence = ([{"type": "lesson_quiz_attempt", "id": str(row.id)} for row in attempts[:1]] or [{"type": "assessment_attempt", "id": str(row.id)} for row in assessments[:1]])
        return {"available": True, "current": 1 if attempts or assessments else 0, "target": 1, "evidence": evidence}

    if rule_type in {"approved_project_count", "capstone_approved"}:
        query = select(StudentProject).where(StudentProject.user_id == user_id, StudentProject.status == "approved")
        project_id = _uuid(config.get("project_id"))
        if project_id:
            query = query.where(StudentProject.project_id == project_id)
        projects = db.scalars(query.order_by(StudentProject.created_at)).all()
        target = 1 if rule_type == "capstone_approved" else target
        evidence = [{"type": "approved_project", "id": str(row.id)} for row in projects[:target]]
        return {"available": True, "current": len(projects), "target": target, "evidence": evidence}

    if rule_type == "learning_path_completion":
        path_id = _uuid(config.get("path_id")) or definition.related_path_id
        if not path_id or not db.scalar(select(CareerRoadmap.id).where(CareerRoadmap.id == path_id, CareerRoadmap.published.is_(True))):
            return {"available": False, "current": None, "target": 1, "evidence": [], "unavailable_reason": "Learning path evidence is not configured"}
        enrollment = db.scalar(select(StudentRoadmap).where(StudentRoadmap.user_id == user_id, StudentRoadmap.roadmap_id == path_id))
        steps = db.scalars(select(RoadmapStep).join(RoadmapStage).where(RoadmapStage.roadmap_id == path_id, RoadmapStep.required.is_(True))).all()
        if not steps:
            return {"available": False, "current": None, "target": 1, "evidence": [], "unavailable_reason": "Learning path has no required steps"}
        completed = 0
        step_evidence: list[dict[str, Any]] = []
        for step in steps:
            resources = db.scalars(select(RoadmapStepResource).where(RoadmapStepResource.step_id == step.id)).all()
            if any(_resource_verified(db, user_id, resource) for resource in resources):
                completed += 1
                step_evidence.append({"type": "learning_path_step", "id": str(step.id)})
        return {"available": bool(enrollment), "current": completed, "target": len(steps), "evidence": step_evidence, "unavailable_reason": None if enrollment else "Learning path has not been started"}

    return {"available": False, "current": None, "target": target, "evidence": [], "unavailable_reason": "Unsupported achievement rule"}


def _resource_verified(db: Session, user_id: UUID, resource: RoadmapStepResource) -> bool:
    if resource.resource_type == "lesson":
        return bool(db.scalar(select(LessonProgress.id).where(LessonProgress.user_id == user_id, LessonProgress.lesson_id == resource.resource_id, LessonProgress.completed.is_(True))))
    if resource.resource_type == "project":
        return bool(db.scalar(select(StudentProject.id).where(StudentProject.user_id == user_id, StudentProject.project_id == resource.resource_id, StudentProject.status == "approved")))
    if resource.resource_type == "course":
        total = db.scalar(select(func.count(Lesson.id)).join(CourseModule).where(CourseModule.course_id == resource.resource_id, Lesson.published.is_(True))) or 0
        done = db.scalar(select(func.count(LessonProgress.id)).join(Lesson, Lesson.id == LessonProgress.lesson_id).join(CourseModule, CourseModule.id == Lesson.module_id).where(LessonProgress.user_id == user_id, CourseModule.course_id == resource.resource_id, Lesson.published.is_(True), LessonProgress.completed.is_(True))) or 0
        return bool(total and done >= total)
    return False


def _notify_award(db: Session, user: User, definition: AchievementDefinition, award: StudentAchievement):
    preference = db.scalar(select(NotificationPreference).where(NotificationPreference.user_id == user.id))
    if not preference or not preference.in_app_enabled:
        return
    key = f"achievement-earned:{user.id}:{definition.id}"
    if db.scalar(select(NotificationMessage.id).where(NotificationMessage.idempotency_key == key)):
        return
    locale = preference.preferred_locale if preference.preferred_locale in {"en", "my"} else "en"
    title = definition.title_mm if locale == "my" and definition.title_mm else definition.title
    db.add(NotificationMessage(
        recipient_id=user.id,
        channel="in_app",
        locale=locale,
        subject="Achievement earned" if locale == "en" else "အောင်မြင်မှု ရရှိပါပြီ",
        body=f"{title} — verified learning reward" if locale == "en" else f"{title} — အတည်ပြုထားသော သင်ယူမှုဆု",
        status="delivered",
        provider="in_app",
        idempotency_key=key,
    ))


def award_verified_achievements(db: Session, user_id: UUID, event_type: str, source_id: UUID | None = None) -> list[StudentAchievement]:
    """Award published definitions after a verified event; never trusts client claims."""
    user = db.get(User, user_id)
    if not user:
        return []
    definitions = db.scalars(select(AchievementDefinition).where(AchievementDefinition.status.in_(PUBLIC_STATUSES), AchievementDefinition.visibility == "public").order_by(AchievementDefinition.display_order, AchievementDefinition.created_at)).all()
    created: list[StudentAchievement] = []
    for definition in definitions:
        result = evaluate_definition(db, user_id, definition)
        if not result.get("available") or (result.get("current") or 0) < result.get("target", 1):
            continue
        existing = db.scalar(select(StudentAchievement).where(StudentAchievement.user_id == user_id, StudentAchievement.achievement_id == definition.id))
        if existing:
            continue
        evidence = result.get("evidence") or ([{"type": event_type, "id": str(source_id)}] if source_id else [])
        award = StudentAchievement(user_id=user_id, achievement_id=definition.id, criteria_version=definition.rule_version, evidence_json=json.dumps({"event": event_type, "source_id": str(source_id) if source_id else None, "evidence": evidence}, separators=(",", ":")), status="active")
        db.add(award)
        db.flush()
        for item in evidence:
            evidence_id = _uuid(item.get("id"))
            if evidence_id:
                db.add(AchievementAwardEvidence(award_id=award.id, evidence_type=str(item.get("type", event_type)), evidence_id=evidence_id, evidence_summary="Verified platform record"))
        db.add(AchievementAuditEvent(actor_id=user_id, action="achievement_awarded", resource_type="student_achievement", resource_id=award.id, metadata_json=json.dumps({"definition_id": str(definition.id), "event_type": event_type})))
        _notify_award(db, user, definition, award)
        created.append(award)
    return created


def definition_payload(definition: AchievementDefinition, locale: str = "en", include_private: bool = False) -> dict[str, Any]:
    localized = locale == "my" and bool(definition.title_mm and definition.description_mm)
    return {
        "id": str(definition.id),
        "code": definition.slug,
        "title": definition.title_mm if localized else definition.title,
        "title_en": definition.title,
        "title_mm": definition.title_mm,
        "description": definition.description_mm if localized else definition.description,
        "description_en": definition.description,
        "description_mm": definition.description_mm,
        "criteria": definition.criteria_description_mm if localized and definition.criteria_description_mm else definition.criteria_description,
        "criteria_en": definition.criteria_description,
        "criteria_mm": definition.criteria_description_mm,
        "category": definition.category,
        "rule_type": definition.rule_type,
        "rule_version": definition.rule_version,
        "badge_image_url": definition.badge_image_url,
        "icon_name": definition.icon_name,
        "tier": definition.tier,
        "related_course_id": str(definition.related_course_id) if definition.related_course_id else None,
        "related_path_id": str(definition.related_path_id) if definition.related_path_id else None,
        "status": definition.status,
        "visibility": definition.visibility,
        "display_order": definition.display_order,
        "resolved_locale": "my" if localized else "en",
        "translation_available": localized,
        **({"rule_json": _json(definition.rule_json), "created_at": definition.created_at, "updated_at": definition.updated_at} if include_private else {}),
    }


def award_payload(db: Session, award: StudentAchievement, locale: str = "en", include_evidence: bool = False) -> dict[str, Any]:
    definition = db.get(AchievementDefinition, award.achievement_id)
    payload = {"award_id": str(award.public_id), "status": "revoked" if award.revoked_at or award.status == "revoked" else award.status, "awarded_at": award.awarded_at, "criteria_version": award.criteria_version, "achievement": definition_payload(definition, locale) if definition else None}
    if include_evidence:
        payload["evidence"] = _json(award.evidence_json)
    return payload
