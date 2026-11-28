"""Verified course certificate rules and idempotent issuance.

Certificates are created only from persisted enrollment, lesson progress, and
published quiz attempts.  This module deliberately has no admin/manual bypass.
"""
import json
import secrets
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .models import CertificatePolicy, CertificateTemplate, Course, CourseModule, Enrollment, IssuedCertificate, Lesson, LessonProgress, LessonQuiz, QuizAttempt, User

COURSE_ACHIEVEMENT = "course_completion"
DEFAULT_QUIZ_PASS_PERCENT = 70


def _now() -> datetime:
    return datetime.now(timezone.utc)


def active_policy(db: Session, course_id: UUID) -> CertificatePolicy | None:
    return db.scalar(select(CertificatePolicy).where(
        CertificatePolicy.achievement_type == COURSE_ACHIEVEMENT,
        CertificatePolicy.active.is_(True),
        or_(CertificatePolicy.resource_id == course_id, CertificatePolicy.resource_id.is_(None)),
    ).order_by(CertificatePolicy.resource_id.is_(None), CertificatePolicy.version.desc()))


def ensure_default_configuration(db: Session) -> tuple[CertificateTemplate, CertificatePolicy]:
    template = db.scalar(select(CertificateTemplate).where(CertificateTemplate.slug == "course-completion-default"))
    if not template:
        template = CertificateTemplate(
            slug="course-completion-default",
            title="Course Completion Certificate",
            heading="Certificate of Completion",
            issuer="Learn-Coding",
            accent_color="#6d5dfc",
            active=True,
        )
        db.add(template)
        db.flush()
    policy = db.scalar(select(CertificatePolicy).where(
        CertificatePolicy.template_id == template.id,
        CertificatePolicy.achievement_type == COURSE_ACHIEVEMENT,
        CertificatePolicy.resource_id.is_(None),
        CertificatePolicy.active.is_(True),
    ).order_by(CertificatePolicy.version.desc()))
    if not policy:
        policy = CertificatePolicy(
            template_id=template.id,
            achievement_type=COURSE_ACHIEVEMENT,
            minimum_score=DEFAULT_QUIZ_PASS_PERCENT,
            rules_json=json.dumps({"lessons": "all_published", "quizzes": "published_quizzes_passed"}),
            version=1,
            active=True,
        )
        db.add(policy)
        db.flush()
    return template, policy


def course_eligibility(db: Session, user_id: UUID, course_id: UUID) -> dict:
    course = db.get(Course, course_id)
    if not course or not course.published:
        return {"eligible": False, "missing_requirements": ["Course is not published"], "evidence": {}}
    if not db.scalar(select(Enrollment.id).where(Enrollment.user_id == user_id, Enrollment.course_id == course_id)):
        return {"eligible": False, "missing_requirements": ["Enroll in this course"], "evidence": {}}

    lesson_rows = db.scalars(
        select(Lesson).join(CourseModule).where(CourseModule.course_id == course_id, Lesson.published.is_(True)).order_by(CourseModule.order_index, Lesson.order_index)
    ).all()
    if not lesson_rows:
        return {"eligible": False, "missing_requirements": ["Course has no published lessons"], "evidence": {}}
    lesson_ids = [lesson.id for lesson in lesson_rows]
    progress_rows = db.scalars(select(LessonProgress).where(LessonProgress.user_id == user_id, LessonProgress.lesson_id.in_(lesson_ids))).all()
    progress_by_lesson = {row.lesson_id: row for row in progress_rows}
    incomplete = [lesson.title for lesson in lesson_rows if not progress_by_lesson.get(lesson.id) or not progress_by_lesson[lesson.id].completed]
    missing = [f"Complete lesson: {title}" for title in incomplete]

    policy = active_policy(db, course_id)
    minimum_score = policy.minimum_score if policy and policy.minimum_score is not None else DEFAULT_QUIZ_PASS_PERCENT
    quizzes = db.scalars(select(LessonQuiz).where(LessonQuiz.lesson_id.in_(lesson_ids), LessonQuiz.status == "published")).all()
    quiz_evidence = []
    for quiz in quizzes:
        attempt = db.scalar(select(QuizAttempt).where(QuizAttempt.user_id == user_id, QuizAttempt.quiz_id == quiz.id).order_by(QuizAttempt.created_at.desc()))
        percentage = round((attempt.score / attempt.total) * 100, 1) if attempt and attempt.total else 0
        quiz_evidence.append({"quiz_id": str(quiz.id), "attempt_id": str(attempt.id) if attempt else None, "passed": bool(attempt and percentage >= minimum_score)})
        if not attempt or percentage < minimum_score:
            missing.append(f"Pass quiz: {quiz.title}")

    timestamps = [row.updated_at for row in progress_rows if row.completed and row.updated_at]
    timestamps.extend(row.created_at for row in [] if row.created_at)
    completion_at = max(timestamps) if timestamps else _now()
    evidence = {
        "course_id": str(course.id),
        "published_lesson_ids": [str(value) for value in lesson_ids],
        "completed_lesson_count": len(lesson_rows) - len(incomplete),
        "lesson_count": len(lesson_rows),
        "quizzes": quiz_evidence,
    }
    return {"eligible": not missing, "missing_requirements": missing, "evidence": evidence, "completion_at": completion_at, "policy": policy}


def issue_course_certificate(db: Session, user: User, course: Course, locale: str = "en") -> IssuedCertificate | None:
    result = course_eligibility(db, user.id, course.id)
    if not result["eligible"]:
        return None
    existing = db.scalar(select(IssuedCertificate).where(
        IssuedCertificate.user_id == user.id,
        IssuedCertificate.achievement_type == COURSE_ACHIEVEMENT,
        IssuedCertificate.resource_id == course.id,
    ))
    if existing:
        return existing
    template, default_policy = ensure_default_configuration(db)
    policy = result.get("policy") or default_policy
    if policy.template_id != template.id:
        template = db.get(CertificateTemplate, policy.template_id) or template
    if not template.active:
        return None
    title = course.display_title or course.title
    row = IssuedCertificate(
        public_id=secrets.token_urlsafe(24), user_id=user.id, template_id=template.id,
        achievement_type=COURSE_ACHIEVEMENT, resource_id=course.id, title=title,
        student_name=user.display_name, issuer=template.issuer, policy_version=policy.version,
        evidence_json=json.dumps(result["evidence"]), locale="my" if locale in {"my", "mm"} else "en",
        completion_at=result.get("completion_at") or _now(), recipient_visible=False,
    )
    db.add(row)
    try:
        db.flush()
    except IntegrityError:
        # The unique user/achievement/resource constraint is the final
        # concurrency guard. Another request may have issued it first.
        db.rollback()
        return db.scalar(select(IssuedCertificate).where(
            IssuedCertificate.user_id == user.id,
            IssuedCertificate.achievement_type == COURSE_ACHIEVEMENT,
            IssuedCertificate.resource_id == course.id,
        ))
    return row


def certificate_payload(row: IssuedCertificate, include_recipient: bool = False) -> dict:
    payload = {
        "certificate_id": row.public_id,
        "title": row.title,
        "issuer": row.issuer,
        "completion_date": row.completion_at or row.issued_at,
        "issued_at": row.issued_at,
        "status": "revoked" if row.revoked_at else ("expired" if row.expires_at and row.expires_at <= _now() else "valid"),
        "verification_url": f"/verify/certificate/{row.public_id}",
        "locale": row.locale,
        "achievement_type": row.achievement_type,
    }
    if include_recipient and row.recipient_visible:
        payload["recipient_name"] = row.student_name
    return payload
