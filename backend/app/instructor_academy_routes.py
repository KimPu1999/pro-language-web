"""Instructor development and teaching-quality evidence APIs."""
import re
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .auth import current_user, require_csrf, verified_user
from .db import get_db
from .models import (
    Course, CourseQualityReview, InstructorAcademyAuditLog, InstructorAcademyProfile,
    InstructorApplication, InstructorApplicationReview, InstructorDevelopmentGoal,
    InstructorDevelopmentPlan, InstructorPeerReview, InstructorTrainingEnrollment,
    InstructorTrainingPath, TeachingStandard, User,
)

router = APIRouter(prefix="/api/v1/instructor-academy", tags=["instructor-academy"])
ADMIN = {"admin", "platform_admin", "super_admin"}
REVIEWERS = ADMIN | {"moderator", "instructor"}


def clean(value: str) -> str:
    return re.sub(r"(?is)<script[^>]*>.*?</script>|javascript:", "", value).strip()


class OnboardingIn(BaseModel):
    expertise: list[str] = Field(default_factory=list, max_length=20)
    teaching_experience: str = Field(default="", max_length=5000)
    sample_lesson: str = Field(default="", max_length=20000)
    guidelines_agreed: bool


class DecisionIn(BaseModel):
    decision: str = Field(pattern="^(approved|changes_requested|rejected)$")
    note: str = Field(default="", max_length=3000)


class PlanIn(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    goal: str = Field(min_length=2, max_length=2000)


class PeerIn(BaseModel):
    course_id: UUID
    reviewer_id: UUID | None = None


class AppealIn(BaseModel):
    review_id: UUID
    reason: str = Field(min_length=3, max_length=4000)


class QualityIn(BaseModel):
    course_id: UUID
    rubric_id: UUID


def audit(db: Session, user: User | None, action: str, entity_type: str, entity_id: UUID | None = None):
    db.add(InstructorAcademyAuditLog(actor_id=user.id if user else None, action=action, entity_type=entity_type, entity_id=entity_id))


def require_instructor(user: User):
    if user.role not in REVIEWERS:
        raise HTTPException(403, "Instructor permission required")
    return user


@router.get("/dashboard")
def dashboard(user: User = Depends(verified_user), db: Session = Depends(get_db)):
    profile = db.scalar(select(InstructorAcademyProfile).where(InstructorAcademyProfile.user_id == user.id))
    courses = db.scalar(select(func.count()).select_from(Course).where(Course.created_by == user.id, Course.published.is_(True))) or 0
    pending = db.scalar(select(func.count()).select_from(InstructorApplication).where(InstructorApplication.user_id == user.id, InstructorApplication.status.in_(["submitted", "changes_requested"]))) or 0
    training = db.scalars(select(InstructorTrainingEnrollment, InstructorTrainingPath).join(InstructorTrainingPath, InstructorTrainingEnrollment.path_id == InstructorTrainingPath.id).where(InstructorTrainingEnrollment.user_id == user.id)).all()
    return {"onboarding_status": profile.onboarding_status if profile else "not_started", "published_courses": courses, "pending_reviews": db.scalar(select(func.count()).select_from(CourseQualityReview).where(CourseQualityReview.reviewer_id == user.id, CourseQualityReview.decision == "in_review")) or 0, "applications": pending, "training": [{"title": path.title, "progress_percent": enrollment.progress_percent, "verified": enrollment.verified} for enrollment, path in training], "data_source": "persisted_instructor_records"}


@router.get("/onboarding")
def onboarding(user: User = Depends(verified_user), db: Session = Depends(get_db)):
    profile = db.scalar(select(InstructorAcademyProfile).where(InstructorAcademyProfile.user_id == user.id))
    application = db.scalar(select(InstructorApplication).where(InstructorApplication.user_id == user.id).order_by(InstructorApplication.created_at.desc()))
    return {"profile": {"status": profile.onboarding_status, "expertise": profile.expertise_json, "guidelines_agreed": profile.guidelines_agreed} if profile else None, "application": {"id": str(application.id), "status": application.status, "note": application.note} if application else None}


@router.post("/onboarding", status_code=202)
def submit_onboarding(payload: OnboardingIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if not payload.guidelines_agreed: raise HTTPException(422, "Teaching guidelines must be accepted")
    profile = db.scalar(select(InstructorAcademyProfile).where(InstructorAcademyProfile.user_id == user.id))
    if not profile: profile = InstructorAcademyProfile(user_id=user.id); db.add(profile); db.flush()
    profile.expertise_json, profile.teaching_experience, profile.sample_lesson, profile.guidelines_agreed, profile.onboarding_status = ",".join(clean(x) for x in payload.expertise), clean(payload.teaching_experience), clean(payload.sample_lesson), True, "submitted"
    application = InstructorApplication(user_id=user.id, profile_id=profile.id, note="Application submitted")
    db.add(application); audit(db, user, "instructor_application_submitted", "application", application.id); db.commit(); return {"id": str(application.id), "status": application.status}


@router.get("/standards")
def standards(db: Session = Depends(get_db)):
    return [{"id": str(x.id), "version": x.version, "title": x.title, "criteria": x.criteria_json} for x in db.scalars(select(TeachingStandard).where(TeachingStandard.status == "published").order_by(TeachingStandard.version.desc())).all()]


@router.get("/training")
def training(user: User = Depends(verified_user), db: Session = Depends(get_db)):
    paths = db.scalars(select(InstructorTrainingPath).where(InstructorTrainingPath.published.is_(True))).all()
    return [{"id": str(path.id), "title": path.title, "description": path.description, "enrollment": (lambda x: {"progress_percent": x.progress_percent, "verified": x.verified} if x else None)(db.scalar(select(InstructorTrainingEnrollment).where(InstructorTrainingEnrollment.path_id == path.id, InstructorTrainingEnrollment.user_id == user.id)))} for path in paths]


@router.post("/training/{path_id}/enroll", status_code=201)
def enroll_training(path_id: UUID, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    path = db.get(InstructorTrainingPath, path_id)
    if not path or not path.published: raise HTTPException(404, "Training path not found")
    if db.scalar(select(InstructorTrainingEnrollment).where(InstructorTrainingEnrollment.path_id == path_id, InstructorTrainingEnrollment.user_id == user.id)): raise HTTPException(409, "Already enrolled")
    row = InstructorTrainingEnrollment(path_id=path_id, user_id=user.id); db.add(row); audit(db, user, "training_enrolled", "training_path", path.id); db.commit(); return {"id": str(row.id), "status": row.status}


@router.get("/development")
def development(user: User = Depends(verified_user), db: Session = Depends(get_db)):
    plans = db.scalars(select(InstructorDevelopmentPlan).where(InstructorDevelopmentPlan.user_id == user.id).order_by(InstructorDevelopmentPlan.created_at.desc())).all()
    return [{"id": str(x.id), "title": x.title, "status": x.status, "goals": [{"id": str(g.id), "description": g.description, "status": g.status} for g in db.scalars(select(InstructorDevelopmentGoal).where(InstructorDevelopmentGoal.plan_id == x.id)).all()]} for x in plans]


@router.post("/development", status_code=201)
def create_plan(payload: PlanIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = InstructorDevelopmentPlan(user_id=user.id, title=clean(payload.title)); db.add(row); db.flush(); db.add(InstructorDevelopmentGoal(plan_id=row.id, description=clean(payload.goal))); audit(db, user, "development_plan_created", "development_plan", row.id); db.commit(); return {"id": str(row.id), "status": row.status}


@router.post("/peer-reviews", status_code=201)
def peer_review(payload: PeerIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    course = db.get(Course, payload.course_id)
    if not course or course.created_by != user.id: raise HTTPException(403, "Course ownership required")
    if payload.reviewer_id == user.id: raise HTTPException(409, "Self-review is not allowed")
    if payload.reviewer_id:
        reviewer = db.get(User, payload.reviewer_id)
        if not reviewer or reviewer.role not in REVIEWERS: raise HTTPException(422, "Reviewer is not eligible")
    row = InstructorPeerReview(course_id=course.id, requester_id=user.id, reviewer_id=payload.reviewer_id); db.add(row); audit(db, user, "peer_review_requested", "peer_review", row.id); db.commit(); return {"id": str(row.id), "status": row.status}


@router.get("/analytics")
def analytics(user: User = Depends(verified_user), db: Session = Depends(get_db)):
    require_instructor(user)
    return {"published_courses": db.scalar(select(func.count()).select_from(Course).where(Course.created_by == user.id, Course.published.is_(True))) or 0, "quality_reviews": db.scalar(select(func.count()).select_from(CourseQualityReview).where(CourseQualityReview.reviewer_id == user.id)) or 0, "student_data": "suppressed_without_verified_aggregate", "data_source": "persisted_records"}


@router.get("/quality")
def quality(user: User = Depends(verified_user), db: Session = Depends(get_db)):
    require_instructor(user)
    return [{"id": str(x.id), "course_id": str(x.course_id), "decision": x.decision, "total_score": x.total_score, "comments": x.comments} for x in db.scalars(select(CourseQualityReview).join(Course, CourseQualityReview.course_id == Course.id).where((Course.created_by == user.id) | (CourseQualityReview.reviewer_id == user.id))).all()]


@router.post("/quality/reviews", status_code=201)
def create_quality(payload: QualityIn, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if user.role not in REVIEWERS: raise HTTPException(403, "Quality reviewer permission required")
    course = db.get(Course, payload.course_id)
    if not course: raise HTTPException(404, "Course not found")
    if course.created_by == user.id: raise HTTPException(409, "Conflict of interest: authors cannot review their own course")
    row = CourseQualityReview(course_id=course.id, rubric_id=payload.rubric_id, reviewer_id=user.id); db.add(row); audit(db, user, "quality_review_created", "quality_review", row.id); db.commit(); return {"id": str(row.id), "decision": row.decision}


@router.get("/certifications")
def certifications(user: User = Depends(verified_user), db: Session = Depends(get_db)):
    rows = db.execute(select(InstructorAcademyProfile, InstructorTrainingEnrollment).join(InstructorTrainingEnrollment, InstructorTrainingEnrollment.user_id == InstructorAcademyProfile.user_id, isouter=True).where(InstructorAcademyProfile.user_id == user.id)).all()
    return {"records": [], "training_verified": any(x[1] and x[1].verified for x in rows), "status": "not_issued_without_verified_requirements"}


@router.get("/ai-coach")
def ai_coach(user: User = Depends(verified_user), db: Session = Depends(get_db)):
    require_instructor(user)
    return {"status": "draft_only", "provider": "not_configured", "suggestions": [], "context": "authorized_instructor_records_only"}


@router.post("/appeals", status_code=201)
def appeal(payload: AppealIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    review = db.get(CourseQualityReview, payload.review_id)
    if not review: raise HTTPException(404, "Quality review not found")
    course = db.get(Course, review.course_id)
    if not course or course.created_by != user.id: raise HTTPException(403, "Course owner required")
    from .models import InstructorQualityAppeal
    row = InstructorQualityAppeal(review_id=review.id, appellant_id=user.id, reason=clean(payload.reason)); db.add(row); audit(db, user, "quality_appeal_submitted", "appeal", row.id); db.commit(); return {"id": str(row.id), "status": row.status}


@router.get("/platform/overview")
def platform_overview(user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role not in ADMIN: raise HTTPException(403, "Platform administrator permission required")
    return {"applications": db.scalar(select(func.count()).select_from(InstructorApplication).where(InstructorApplication.status == "submitted")) or 0, "quality_reviews": db.scalar(select(func.count()).select_from(CourseQualityReview).where(CourseQualityReview.decision == "in_review")) or 0, "peer_reviews": db.scalar(select(func.count()).select_from(InstructorPeerReview).where(InstructorPeerReview.status == "requested")) or 0, "data_source": "persisted_academy_records"}


@router.get("/platform/applications")
def applications(user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role not in ADMIN: raise HTTPException(403, "Platform administrator permission required")
    return [{"id": str(x.id), "user_id": str(x.user_id), "status": x.status, "note": x.note} for x in db.scalars(select(InstructorApplication).order_by(InstructorApplication.created_at)).all()]


@router.post("/platform/applications/{application_id}")
def decide_application(application_id: UUID, payload: DecisionIn, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if user.role not in ADMIN: raise HTTPException(403, "Platform administrator permission required")
    application = db.get(InstructorApplication, application_id)
    if not application: raise HTTPException(404, "Application not found")
    target = db.get(User, application.user_id); application.status = payload.decision; application.note = clean(payload.note); db.add(InstructorApplicationReview(application_id=application.id, reviewer_id=user.id, decision=payload.decision, note=clean(payload.note)))
    if payload.decision == "approved": target.role = "instructor"; db.get(InstructorAcademyProfile, application.profile_id).onboarding_status = "approved"
    elif payload.decision in {"rejected", "changes_requested"}: db.get(InstructorAcademyProfile, application.profile_id).onboarding_status = payload.decision
    audit(db, user, f"instructor_application_{payload.decision}", "application", application.id); db.commit(); return {"status": application.status, "role": target.role}
