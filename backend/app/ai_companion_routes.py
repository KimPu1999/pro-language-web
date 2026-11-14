"""Phase 29 adaptive companion boundary.

The existing `/api/v1/ai` provider and SSE implementation remains the chat
transport. These routes add authorized learning context, deterministic study
state, privacy controls, and truthful provider/voice status around it.
"""
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .auth import current_user, require_csrf, verified_user
from .config import settings
from .db import get_db
from .models import (
    AICompanionAuditLog, AICompanionConversation, AICompanionLearningGoal,
    AICompanionProfile, AICompanionRevisionItem,
    AICompanionRevisionReview, AICompanionSecurityEvent, AICompanionStudyPlan,
    AICompanionStudyPlanItem, AICompanionUsageRecord, AICompanionVoiceSession,
    AIConversation, AIStudySession, AIStudySessionActivity, AIUsageRecord, Course, CourseModule, Enrollment,
    Lesson, LessonProgress, StudentSkillAssessment, StudentSkillEvidence, User,
)
from .rbac import require_platform_admin

router = APIRouter(prefix="/api/v1/ai-companion", tags=["ai-companion"])
ADMIN = {"instructor", "admin", "platform_admin", "super_admin"}

class ProfileIn(BaseModel):
    language: str = Field(default="en", pattern=r"^(en|mm)$")
    difficulty: str = Field(default="beginner", max_length=30)
    study_minutes: int = Field(default=30, ge=5, le=240)
    personalization_enabled: bool = True
class SessionIn(BaseModel):
    session_type: str = Field(default="mixed", pattern=r"^(concept|revision|coding|debugging|quiz|project|mixed)$")
class SessionUpdate(BaseModel):
    status: str = Field(pattern=r"^(active|paused|completed)$")
class ReviewIn(BaseModel):
    confidence: int = Field(ge=1, le=5)
    correct: bool
class GoalIn(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    target_type: str = Field(pattern=r"^(minutes|lessons|practice|course)$")
    target_id: UUID | None = None
    target_value: int = Field(ge=0, le=100000)
class PlanIn(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    timezone: str = Field(default="UTC", max_length=80)
class VoiceIn(BaseModel):
    language: str = Field(default="en", pattern=r"^(en|mm)$")

def utcnow(): return datetime.now(timezone.utc)
def provider_status(): return "configured" if settings.ai_enabled and settings.ai_provider != "disabled" else "not_configured"

@router.get("/dashboard")
def dashboard(user: User = Depends(current_user), db: Session = Depends(get_db)):
    completed = db.scalar(select(func.count()).select_from(LessonProgress).where(LessonProgress.user_id == user.id, LessonProgress.completed.is_(True))) or 0
    due = db.scalar(select(func.count()).select_from(AICompanionRevisionItem).where(AICompanionRevisionItem.user_id == user.id, AICompanionRevisionItem.next_review_at <= utcnow())) or 0
    goals = db.scalars(select(AICompanionLearningGoal).where(AICompanionLearningGoal.user_id == user.id, AICompanionLearningGoal.status == "active").limit(6)).all()
    return {"completed_lessons": completed, "due_revisions": due, "goals": [{"id": str(x.id), "title": x.title, "current_value": x.current_value, "target_value": x.target_value} for x in goals], "provider": provider_status(), "verified_data_only": True}

@router.get("/profile")
def profile(user: User = Depends(current_user), db: Session = Depends(get_db)):
    row = db.scalar(select(AICompanionProfile).where(AICompanionProfile.user_id == user.id))
    return {"language": row.language if row else "en", "difficulty": row.difficulty if row else "beginner", "study_minutes": row.study_minutes if row else 30, "personalization_enabled": row.personalization_enabled if row else True}

@router.put("/profile")
def update_profile(payload: ProfileIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.scalar(select(AICompanionProfile).where(AICompanionProfile.user_id == user.id))
    if not row: row = AICompanionProfile(user_id=user.id); db.add(row)
    row.language, row.difficulty, row.study_minutes, row.personalization_enabled = payload.language, payload.difficulty, payload.study_minutes, payload.personalization_enabled
    db.add(AICompanionAuditLog(actor_id=user.id, action="companion_profile_updated", resource_type="profile", resource_id=row.id)); db.commit()
    return profile(user, db)

@router.post("/study-sessions", status_code=201)
def create_session(payload: SessionIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    session = AIStudySession(user_id=user.id, session_type=payload.session_type); db.add(session); db.flush()
    lessons = db.scalars(select(Lesson).join(CourseModule).join(Course).where(Lesson.published.is_(True), Course.published.is_(True)).order_by(Lesson.order_index).limit(3)).all()
    for position, lesson in enumerate(lessons):
        db.add(AIStudySessionActivity(session_id=session.id, activity_type="lesson", resource_id=lesson.id, position=position))
        if not db.scalar(select(AICompanionRevisionItem).where(AICompanionRevisionItem.user_id == user.id, AICompanionRevisionItem.lesson_id == lesson.id)):
            db.add(AICompanionRevisionItem(user_id=user.id, lesson_id=lesson.id, next_review_at=utcnow() + timedelta(days=1)))
    db.add(AICompanionAuditLog(actor_id=user.id, action="study_session_created", resource_type="study_session", resource_id=session.id)); db.commit()
    return {"id": str(session.id), "status": session.status, "activities": len(lessons), "verified": False}

@router.get("/study-sessions")
def sessions(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(AIStudySession).where(AIStudySession.user_id == user.id).order_by(AIStudySession.created_at.desc()).limit(20)).all()
    return {"items": [{"id": str(x.id), "session_type": x.session_type, "status": x.status, "verified": x.verified, "activities": [{"id": str(a.id), "type": a.activity_type, "resource_id": str(a.resource_id) if a.resource_id else None, "status": a.status} for a in db.scalars(select(AIStudySessionActivity).where(AIStudySessionActivity.session_id == x.id).order_by(AIStudySessionActivity.position)).all()]} for x in rows]}

@router.patch("/study-sessions/{session_id}")
def update_session(session_id: UUID, payload: SessionUpdate, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.scalar(select(AIStudySession).where(AIStudySession.id == session_id, AIStudySession.user_id == user.id))
    if not row: raise HTTPException(404, "Study session not found")
    row.status = payload.status; row.completed_at = utcnow() if payload.status == "completed" else None; row.verified = False; db.commit()
    return {"id": str(row.id), "status": row.status, "verified": False}

@router.get("/revision")
def revision(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.execute(select(AICompanionRevisionItem, Lesson).join(Lesson, Lesson.id == AICompanionRevisionItem.lesson_id).where(AICompanionRevisionItem.user_id == user.id).order_by(AICompanionRevisionItem.next_review_at)).all()
    now = utcnow(); return {"algorithm_version": "v1", "items": [{"id": str(item.id), "lesson_id": str(lesson.id), "lesson_title": lesson.title, "next_review_at": item.next_review_at, "due": item.next_review_at <= now, "interval_days": item.interval_days} for item, lesson in rows]}

@router.post("/revision/{item_id}/review")
def review(item_id: UUID, payload: ReviewIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    item = db.scalar(select(AICompanionRevisionItem).where(AICompanionRevisionItem.id == item_id, AICompanionRevisionItem.user_id == user.id))
    if not item: raise HTTPException(404, "Revision item not found")
    item.ease_factor = max(1.3, min(3.0, item.ease_factor + (0.1 if payload.correct else -0.2)))
    item.interval_days = max(1, round(item.interval_days * item.ease_factor * (1.0 if payload.correct else 0.25)))
    item.next_review_at = utcnow() + timedelta(days=item.interval_days); db.add(AICompanionRevisionReview(item_id=item.id, user_id=user.id, confidence=payload.confidence, correct=payload.correct)); db.commit()
    return {"next_review_at": item.next_review_at, "interval_days": item.interval_days, "algorithm_version": item.algorithm_version}

@router.get("/recommendations")
def recommendations(user: User = Depends(current_user), db: Session = Depends(get_db)):
    enrolled = set(db.scalars(select(Enrollment.course_id).where(Enrollment.user_id == user.id)).all()); rows = db.scalars(select(Course).where(Course.published.is_(True)).order_by(Course.title).limit(20)).all(); now = utcnow(); items = []
    for course in rows:
        if course.id in enrolled: continue
        items.append({"resource_type": "course", "resource_id": str(course.id), "title": course.title, "reason": "Published content not yet enrolled in.", "evidence": ["published_course_catalog", "enrollment_history"], "difficulty": course.level, "prerequisites": [], "generated_at": now})
    return {"items": items[:10], "provenance": "rule_based_verified_catalog"}

@router.get("/goals")
def goals(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return {"items": [{"id": str(x.id), "title": x.title, "target_type": x.target_type, "target_value": x.target_value, "current_value": x.current_value, "status": x.status} for x in db.scalars(select(AICompanionLearningGoal).where(AICompanionLearningGoal.user_id == user.id).order_by(AICompanionLearningGoal.created_at.desc())).all()]}

@router.post("/goals", status_code=201)
def create_goal(payload: GoalIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = AICompanionLearningGoal(user_id=user.id, title=payload.title, target_type=payload.target_type, target_id=payload.target_id, target_value=payload.target_value); db.add(row); db.commit(); return {"id": str(row.id), "status": row.status}

@router.get("/insights")
def insights(user: User = Depends(current_user), db: Session = Depends(get_db)):
    completed = db.scalar(select(func.count()).select_from(LessonProgress).where(LessonProgress.user_id == user.id, LessonProgress.completed.is_(True))) or 0; verified_evidence = db.scalar(select(func.count()).select_from(StudentSkillEvidence).where(StudentSkillEvidence.user_id == user.id, StudentSkillEvidence.verified.is_(True))) or 0; verified_assessments = db.scalar(select(func.count()).select_from(StudentSkillAssessment).where(StudentSkillAssessment.user_id == user.id, StudentSkillAssessment.verified.is_(True))) or 0
    return {"items": [{"kind": "activity", "provenance": "observed_data", "content": {"completed_lessons": completed}}, {"kind": "skills", "provenance": "verified_evidence", "content": {"evidence_count": verified_evidence, "assessment_count": verified_assessments}}], "ai_estimates": [], "note": "AI estimates are not used as verified mastery."}

@router.get("/planner")
def planner(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(AICompanionStudyPlan).where(AICompanionStudyPlan.user_id == user.id).order_by(AICompanionStudyPlan.created_at.desc())).all(); return {"items": [{"id": str(x.id), "title": x.title, "timezone": x.timezone, "status": x.status, "entries": [{"activity_type": i.activity_type, "resource_id": str(i.resource_id) if i.resource_id else None, "scheduled_for": i.scheduled_for, "minutes": i.minutes} for i in db.scalars(select(AICompanionStudyPlanItem).where(AICompanionStudyPlanItem.plan_id == x.id).order_by(AICompanionStudyPlanItem.scheduled_for)).all()]} for x in rows]}

@router.post("/planner", status_code=201)
def create_plan(payload: PlanIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    plan = AICompanionStudyPlan(user_id=user.id, title=payload.title, timezone=payload.timezone); db.add(plan); db.flush(); db.add(AICompanionStudyPlanItem(plan_id=plan.id, activity_type="revision", scheduled_for=utcnow(), minutes=30)); db.commit(); return {"id": str(plan.id), "status": plan.status}

@router.get("/voice/status")
def voice_status(user: User = Depends(current_user)):
    return {"status": "not_configured", "provider": "not_configured", "raw_audio_retained": False, "text_fallback": True, "microphone_required": False}

@router.post("/voice/sessions", status_code=201)
def voice_session(payload: VoiceIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = AICompanionVoiceSession(user_id=user.id); db.add(row); db.commit(); return {"id": str(row.id), "status": row.status, "provider": row.provider, "raw_audio_retained": False}

@router.get("/explain/status")
@router.get("/debugging/status")
def assistant_status(user: User = Depends(current_user)):
    return {"status": provider_status(), "hidden_tests_exposed": False, "automatic_scoring": False, "hint_first": True}

@router.delete("/privacy")
def delete_companion_data(user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    for row in db.scalars(select(AICompanionConversation).where(AICompanionConversation.user_id == user.id)).all(): row.status = "deleted"
    for row in db.scalars(select(AIConversation).where(AIConversation.user_id == user.id)).all(): row.status = "deleted"
    db.query(AICompanionProfile).filter(AICompanionProfile.user_id == user.id).delete(); db.add(AICompanionAuditLog(actor_id=user.id, action="companion_data_deleted", resource_type="privacy", metadata_json="{}")); db.commit(); return {"status": "deleted", "provider_data": "provider_deletion_not_configured"}

@router.get("/instructor/insights")
def instructor_insights(user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role not in ADMIN: raise HTTPException(403, "Instructor permission required")
    count = db.scalar(select(func.count()).select_from(User).where(User.role == "student")) or 0
    if count < 5: return {"status": "suppressed_for_privacy", "minimum_group_size": 5, "items": []}
    return {"status": "available", "minimum_group_size": 5, "items": [{"kind": "course_activity", "provenance": "aggregated_observed_data", "student_count": count}]}

@router.get("/platform/operations")
def operations(user: User = Depends(require_platform_admin), db: Session = Depends(get_db)):
    return {"provider": provider_status(), "requests": db.scalar(select(func.count()).select_from(AIUsageRecord)) or 0, "companion_usage": db.scalar(select(func.count()).select_from(AICompanionUsageRecord)) or 0, "security_events": db.scalar(select(func.count()).select_from(AICompanionSecurityEvent)) or 0, "voice": "not_configured", "data_source": "postgresql"}
