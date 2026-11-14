import json
from datetime import datetime, timedelta, timezone
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .auth import current_user, require_csrf, verified_user
from .config import settings
from .db import get_db
from .models import (Course, CourseModule, Enrollment, LearningCoachInteraction,
    LearningRecommendation, LearningRecommendationFeedback, LearningRevisionAttempt,
    LearningRevisionItem, LearningSkillSnapshot, LearningStudyPlan,
    LearningStudyPlanItem, Lesson, LessonProgress, SkillDefinition, StudentLearningGoal,
    StudentSkillAssessment, StudentSkillEvidence, User)

router = APIRouter(prefix="/api/v1/learning", tags=["learning intelligence"])
ADMIN = {"admin", "platform_admin", "super_admin"}

class FeedbackIn(BaseModel):
    action: str = Field(pattern="^(accept|dismiss|save_for_later|not_interested|already_completed)$")
class PlanIn(BaseModel):
    title: str = Field(default="My weekly study plan", min_length=1, max_length=180)
    week_start: datetime | None = None
class RevisionAttemptIn(BaseModel):
    confidence: int = Field(ge=1, le=5)
class CoachIn(BaseModel):
    message: str = Field(min_length=1, max_length=4000)

def utcnow(): return datetime.now(timezone.utc)
def owned_plan(db, user, plan_id):
    row = db.scalar(select(LearningStudyPlan).where(LearningStudyPlan.id == plan_id, LearningStudyPlan.user_id == user.id))
    if not row: raise HTTPException(404, "Study plan not found")
    return row

def skill_score(db, user_id, skill_id):
    evidence = db.scalars(select(StudentSkillEvidence).where(StudentSkillEvidence.user_id == user_id, StudentSkillEvidence.skill_id == skill_id, StudentSkillEvidence.verified.is_(True))).all()
    assessments = db.scalars(select(StudentSkillAssessment).where(StudentSkillAssessment.user_id == user_id, StudentSkillAssessment.skill_id == skill_id, StudentSkillAssessment.verified.is_(True))).all()
    weights = {"instructor_project": 1.0, "project_review": 1.0, "challenge": 0.9, "assessment": 1.0, "lesson": 0.2, "milestone": 0.4}
    weighted = sum(weights.get(item.evidence_type, 0.5) for item in evidence)
    assessed = [a.score for a in assessments if a.score is not None]
    score = round(sum(assessed) / len(assessed)) if assessed else (min(100, round(weighted / 3 * 100)) if weighted >= 1 else None)
    count = len(evidence) + len(assessments)
    confidence = "high" if count >= 3 and weighted >= 2.5 else "medium" if count >= 2 else "not_yet_assessed"
    if confidence == "not_yet_assessed": score = None
    explanation = "Verified evidence is insufficient for a reliable skill score." if score is None else f"Score uses {count} verified evidence item(s), weighted by source reliability."
    last = max([x.created_at for x in evidence + assessments if x.created_at] or [None])
    return {"score": score, "confidence": confidence, "evidence_count": count, "last_assessed_at": last, "explanation": explanation}

def recommendations_for(db, user):
    goal = db.scalar(select(StudentLearningGoal).where(StudentLearningGoal.user_id == user.id))
    enrolled = set(db.scalars(select(Enrollment.course_id).where(Enrollment.user_id == user.id)).all())
    courses = db.scalars(select(Course).where(Course.published.is_(True)).order_by(Course.title)).all()
    words = set((goal.career_goal.lower().split() if goal else []))
    result = []
    for course in courses:
        if course.id in enrolled: continue
        match = bool(words.intersection(set(course.title.lower().split())))
        result.append({"resource_type": "course", "resource_id": course.id, "title": course.title, "score": 80 if match else 50, "reason": "Matches your selected career goal." if match else "Published course available for your next learning step.", "explanation": "Rule-based recommendation using published content and enrollment history."})
    return sorted(result, key=lambda x: (-x["score"], x["title"]))[:12]

@router.get("/intelligence")
def intelligence(user: User = Depends(current_user), db: Session = Depends(get_db)):
    skills = []
    for skill in db.scalars(select(SkillDefinition).order_by(SkillDefinition.name)).all():
        snapshot = skill_score(db, user.id, skill.id)
        existing = db.scalar(select(LearningSkillSnapshot).where(LearningSkillSnapshot.user_id == user.id, LearningSkillSnapshot.skill_id == skill.id))
        if existing:
            existing.score, existing.confidence, existing.evidence_count, existing.explanation, existing.last_assessed_at = snapshot["score"], snapshot["confidence"], snapshot["evidence_count"], snapshot["explanation"], snapshot["last_assessed_at"]
        skills.append({"id": skill.id, "name": skill.name, "category": skill.category, **snapshot})
    db.commit()
    completed = db.scalar(select(func.count(LessonProgress.id)).where(LessonProgress.user_id == user.id, LessonProgress.completed.is_(True))) or 0
    activity = db.scalar(select(func.count(LessonProgress.id)).where(LessonProgress.user_id == user.id, LessonProgress.updated_at >= utcnow() - timedelta(days=7))) or 0
    return {"skills": skills, "recommendations": recommendations_for(db, user)[:6], "metrics": {"completed_lessons": completed, "last_7_days_activity": activity}, "status": "observed_data"}

@router.get("/skills")
def skills(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return {"items": [{"id": s.id, "name": s.name, "category": s.category, **skill_score(db, user.id, s.id)} for s in db.scalars(select(SkillDefinition).order_by(SkillDefinition.name)).all()]}

@router.get("/recommendations")
def recommendations(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return {"items": recommendations_for(db, user), "status": "rule_based"}

@router.post("/recommendations/{recommendation_id}/feedback")
def recommendation_feedback(recommendation_id: UUID, payload: FeedbackIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    recommendation = db.scalar(select(LearningRecommendation).where(LearningRecommendation.id == recommendation_id, LearningRecommendation.user_id == user.id))
    if not recommendation:
        course = db.scalar(select(Course).where(Course.id == recommendation_id, Course.published.is_(True)))
        if not course: raise HTTPException(404, "Recommendation not found")
        recommendation = LearningRecommendation(user_id=user.id, resource_type="course", resource_id=course.id, reason="Student feedback recommendation", score=0)
        db.add(recommendation); db.flush()
    recommendation_id = recommendation.id
    existing = db.scalar(select(LearningRecommendationFeedback).where(LearningRecommendationFeedback.recommendation_id == recommendation_id, LearningRecommendationFeedback.user_id == user.id))
    if existing: existing.action = payload.action
    else: db.add(LearningRecommendationFeedback(recommendation_id=recommendation_id, user_id=user.id, action=payload.action))
    db.commit(); return {"status": "saved", "action": payload.action}

@router.post("/study-plans", status_code=201)
def create_plan(payload: PlanIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    start = payload.week_start or utcnow()
    row = LearningStudyPlan(user_id=user.id, title=payload.title.strip(), week_start=start, status="active")
    db.add(row); db.flush()
    lessons = db.scalars(select(Lesson).join(CourseModule).join(Course).where(Lesson.published.is_(True), Course.published.is_(True)).order_by(Lesson.order_index).limit(7)).all()
    for index, lesson in enumerate(lessons):
        db.add(LearningStudyPlanItem(plan_id=row.id, activity_type="lesson", resource_id=lesson.id, scheduled_for=start + timedelta(days=index), minutes=30))
    db.commit(); return {"id": row.id, "title": row.title, "status": row.status, "items": len(lessons)}

@router.get("/study-plans")
def study_plans(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(LearningStudyPlan).where(LearningStudyPlan.user_id == user.id).order_by(LearningStudyPlan.created_at.desc())).all()
    return {"items": [{"id": r.id, "title": r.title, "status": r.status, "week_start": r.week_start, "items": [{"id": i.id, "activity_type": i.activity_type, "resource_id": i.resource_id, "scheduled_for": i.scheduled_for, "minutes": i.minutes, "completed": i.completed} for i in db.scalars(select(LearningStudyPlanItem).where(LearningStudyPlanItem.plan_id == r.id).order_by(LearningStudyPlanItem.scheduled_for)).all()]} for r in rows]}

@router.patch("/study-plans/{plan_id}/items/{item_id}")
def update_plan_item(plan_id: UUID, item_id: UUID, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    owned_plan(db, user, plan_id)
    item = db.scalar(select(LearningStudyPlanItem).where(LearningStudyPlanItem.id == item_id, LearningStudyPlanItem.plan_id == plan_id))
    if not item: raise HTTPException(404, "Study plan item not found")
    lesson_complete = item.resource_id and db.scalar(select(LessonProgress).where(LessonProgress.user_id == user.id, LessonProgress.lesson_id == item.resource_id, LessonProgress.completed.is_(True)))
    item.completed = bool(lesson_complete); item.completed_at = utcnow() if item.completed else None; db.commit()
    return {"id": item.id, "completed": item.completed, "verified": True}

@router.get("/revision")
def revision(user: User = Depends(current_user), db: Session = Depends(get_db)):
    now = utcnow(); rows = db.execute(select(LearningRevisionItem, Lesson).join(Lesson, Lesson.id == LearningRevisionItem.lesson_id).where(LearningRevisionItem.user_id == user.id).order_by(LearningRevisionItem.next_review_at)).all()
    return {"items": [{"id": item.id, "lesson_id": lesson.id, "lesson_title": lesson.title, "next_review_at": item.next_review_at, "due": item.next_review_at <= now, "interval_days": item.interval_days, "confidence": item.confidence} for item, lesson in rows]}

@router.post("/revision/{item_id}/attempt")
def revision_attempt(item_id: UUID, payload: RevisionAttemptIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    item = db.scalar(select(LearningRevisionItem).where(LearningRevisionItem.id == item_id, LearningRevisionItem.user_id == user.id))
    if not item: raise HTTPException(404, "Revision item not found")
    item.confidence = payload.confidence; item.interval_days = {1: 1, 2: 1, 3: 3, 4: 7, 5: 14}[payload.confidence]; item.next_review_at = utcnow() + timedelta(days=item.interval_days); db.add(LearningRevisionAttempt(item_id=item.id, user_id=user.id, confidence=payload.confidence)); db.commit()
    return {"next_review_at": item.next_review_at, "interval_days": item.interval_days}

@router.get("/goals")
def goal(user: User = Depends(current_user), db: Session = Depends(get_db)):
    row = db.scalar(select(StudentLearningGoal).where(StudentLearningGoal.user_id == user.id))
    return None if not row else {"career_goal": row.career_goal, "current_level": row.current_level, "interests": json.loads(row.interests_json), "weekly_hours": row.weekly_hours, "pace": row.pace, "timezone": row.timezone}

@router.post("/coach")
def coach(payload: CoachIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    enabled = settings.ai_enabled and settings.ai_provider != "disabled"
    status = "queued" if enabled else "unavailable"
    db.add(LearningCoachInteraction(user_id=user.id, prompt_summary=payload.message[:500], response_status=status, context_keys="[\"skills\",\"goals\"]")); db.commit()
    if not enabled: return {"status": "unavailable", "message": "AI Learning Coach is not configured. No live response was generated."}
    return {"status": "available_via_ai_tutor", "message": "Use the AI Tutor for an authenticated coaching conversation."}

@router.get("/platform/insights")
def platform_insights(user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role not in ADMIN: raise HTTPException(403, "Administrator access required")
    threshold = 5
    total = db.scalar(select(func.count(User.id)).where(User.role == "student")) or 0
    evidence = db.scalar(select(func.count(StudentSkillEvidence.id)).where(StudentSkillEvidence.verified.is_(True))) or 0
    return {"privacy_threshold": threshold, "student_group_size": total, "status": "available" if total >= threshold else "suppressed_for_privacy", "verified_evidence_count": evidence if total >= threshold else None}
