"""Phase 36 assessment integrity, grading, competency, and credential APIs."""
import hashlib
import json
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .auth import check_rate_limit, current_user, require_csrf, verified_user
from .db import get_db
from .models import (
    AssessmentAppeal, AssessmentAttempt, AssessmentAttemptAnswer, AssessmentAttemptEvent,
    AssessmentAuditLog, AssessmentDefinition, AssessmentGradingJob, AssessmentGradingResult,
    AssessmentGradeRevision, AssessmentIntegrityCase, AssessmentQuestion,
    AssessmentQuestionVersion, AssessmentVersion, CompetencyDefinition, CredentialAward, CredentialStatusEvent, IssuedCertificate, StudentCompetencyRecord, User,
    Course,
)

router = APIRouter(prefix="/api/v1/assessments", tags=["assessments"])
ADMIN = {"admin", "platform_admin", "super_admin"}
REVIEWERS = ADMIN | {"instructor", "moderator"}


def reviewer(user: User = Depends(current_user)) -> User:
    if user.role not in REVIEWERS or not user.email_verified_at:
        raise HTTPException(403, "Assessment reviewer access required")
    return user


def platform_admin(user: User = Depends(current_user)) -> User:
    if user.role not in ADMIN or not user.email_verified_at:
        raise HTTPException(403, "Platform credential permission required")
    return user


def data(row):
    return {column.name: getattr(row, column.name) for column in row.__table__.columns}


def audit(db, actor, action, entity_type, entity_id=None):
    db.add(AssessmentAuditLog(actor_id=actor.id, action=action, entity_type=entity_type, entity_id=entity_id))


def answer_hash(answer):
    return hashlib.sha256(json.dumps(answer, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


class AssessmentIn(BaseModel):
    title: str = Field(min_length=3, max_length=180)
    slug: str = Field(pattern=r"^[a-z0-9-]{3,180}$")
    assessment_type: str = Field(pattern=r"^(multiple_choice|multiple_select|short_answer|coding|sql|debugging|project|code_review)$")
    attempt_limit: int = Field(default=1, ge=1, le=10)
    time_limit_minutes: int | None = Field(default=None, ge=1, le=480)
    course_id: UUID | None = None


class VersionIn(BaseModel):
    instructions: str = Field(default="", max_length=20000)


class QuestionIn(BaseModel):
    question_type: str = Field(pattern=r"^(multiple_choice|multiple_select|short_answer|coding|sql|debugging|project|code_review)$")
    prompt: str = Field(min_length=3, max_length=20000)
    options: list[str] = Field(default_factory=list, max_length=30)
    correct_answer: object | None = None
    points: int = Field(default=1, ge=1, le=100)


class AnswerIn(BaseModel):
    question_id: UUID
    answer: object


class FinalizeIn(BaseModel):
    idempotency_key: str = Field(min_length=8, max_length=180)


class AppealIn(BaseModel):
    reason: str = Field(min_length=10, max_length=10000)
    evidence: str = Field(default="", max_length=10000)


class GradeIn(BaseModel):
    score: int = Field(ge=0, le=100)
    reason: str = Field(min_length=5, max_length=10000)


class CredentialIn(BaseModel):
    user_id: UUID
    credential_type: str = Field(pattern=r"^(skill_badge|project|competency|learning_path)$")
    title: str = Field(min_length=3, max_length=180)
    source_id: UUID
    public: bool = False


@router.get("")
def assessment_center(user: User = Depends(verified_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(AssessmentDefinition).where(AssessmentDefinition.status == "published").order_by(AssessmentDefinition.title)).all()
    attempts = db.scalars(select(AssessmentAttempt).where(AssessmentAttempt.user_id == user.id).order_by(AssessmentAttempt.created_at.desc()).limit(50)).all()
    credentials = db.scalars(select(CredentialAward).where(CredentialAward.user_id == user.id, CredentialAward.status == "active")).all()
    return {"available": [data(row) for row in rows], "attempts": [data(row) for row in attempts], "credentials": [data(row) for row in credentials], "source": "published_assessments_and_verified_records"}


@router.get("/competencies")
def competencies(user: User = Depends(verified_user), db: Session = Depends(get_db)):
    definitions = db.scalars(select(CompetencyDefinition).where(CompetencyDefinition.status == "published").order_by(CompetencyDefinition.title)).all()
    records = db.scalars(select(StudentCompetencyRecord).where(StudentCompetencyRecord.user_id == user.id, StudentCompetencyRecord.verified.is_(True))).all()
    return {"definitions": [data(row) for row in definitions], "verified": [data(row) for row in records], "note": "Only verified evidence is shown."}


@router.get("/skill-passport")
def skill_passport(user: User = Depends(verified_user), db: Session = Depends(get_db)):
    records = db.scalars(select(StudentCompetencyRecord).where(StudentCompetencyRecord.user_id == user.id, StudentCompetencyRecord.verified.is_(True), StudentCompetencyRecord.public.is_(True))).all()
    awards = db.scalars(select(CredentialAward).where(CredentialAward.user_id == user.id, CredentialAward.status == "active", CredentialAward.public.is_(True))).all()
    return {"skills": [data(row) for row in records], "credentials": [data(row) for row in awards], "visibility": "public_records_only"}


@router.get("/credentials")
def credentials(user: User = Depends(verified_user), db: Session = Depends(get_db)):
    awards = db.scalars(select(CredentialAward).where(CredentialAward.user_id == user.id).order_by(CredentialAward.issued_at.desc())).all()
    certificates = db.scalars(select(IssuedCertificate).where(IssuedCertificate.user_id == user.id, IssuedCertificate.revoked_at.is_(None))).all()
    return {"awards": [data(row) for row in awards], "course_certificates": [{"verification_id": row.public_id, "title": row.title, "issuer": row.issuer, "issued_at": row.issued_at, "status": "valid"} for row in certificates]}


@router.get("/credentials/verify/{verification_id}")
def verify_credential(verification_id: str, db: Session = Depends(get_db)):
    row = db.scalar(select(CredentialAward).where(CredentialAward.verification_id == verification_id))
    if not row: return {"status": "not_found", "verification_id": verification_id}
    return {"status": row.status, "verification_id": row.verification_id, "title": row.title, "issuer": row.issuer, "issued_at": row.issued_at, "credential_type": row.credential_type}


@router.post("", status_code=201)
def create_assessment(payload: AssessmentIn, user: User = Depends(reviewer), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if user.role == "instructor" and payload.course_id and not db.scalar(select(func.count()).select_from(Course).where(Course.id == payload.course_id, Course.created_by == user.id)):
        raise HTTPException(403, "Course ownership required")
    if db.scalar(select(AssessmentDefinition).where(AssessmentDefinition.slug == payload.slug)): raise HTTPException(409, "Assessment slug already exists")
    row = AssessmentDefinition(created_by=user.id, **payload.model_dump()); db.add(row); audit(db, user, "assessment_created", "assessment_definition", row.id); db.commit(); db.refresh(row); return data(row)


@router.post("/{assessment_id}/versions", status_code=201)
def create_version(assessment_id: UUID, payload: VersionIn, user: User = Depends(reviewer), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    assessment = db.get(AssessmentDefinition, assessment_id)
    if not assessment: raise HTTPException(404, "Assessment not found")
    if user.role == "instructor" and assessment.created_by != user.id: raise HTTPException(403, "Assessment ownership required")
    number = (db.scalar(select(func.max(AssessmentVersion.version)).where(AssessmentVersion.assessment_id == assessment.id)) or 0) + 1
    row = AssessmentVersion(assessment_id=assessment.id, version=number, instructions=payload.instructions); db.add(row); db.commit(); db.refresh(row); return data(row)


@router.post("/{assessment_id}/questions", status_code=201)
def add_question(assessment_id: UUID, payload: QuestionIn, user: User = Depends(reviewer), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    assessment = db.get(AssessmentDefinition, assessment_id)
    if not assessment: raise HTTPException(404, "Assessment not found")
    if user.role == "instructor" and assessment.created_by != user.id: raise HTTPException(403, "Assessment ownership required")
    position = (db.scalar(select(func.max(AssessmentQuestion.position)).where(AssessmentQuestion.assessment_id == assessment.id)) or 0) + 1
    question = AssessmentQuestion(assessment_id=assessment.id, question_type=payload.question_type, position=position, points=payload.points); db.add(question); db.flush()
    version = AssessmentQuestionVersion(question_id=question.id, version=1, prompt=payload.prompt, options_json=json.dumps(payload.options), answer_hash=answer_hash(payload.correct_answer) if payload.correct_answer is not None else None)
    db.add(version); db.commit(); db.refresh(question); return data(question)


@router.post("/{assessment_id}/publish")
def publish_assessment(assessment_id: UUID, user: User = Depends(reviewer), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    assessment = db.get(AssessmentDefinition, assessment_id)
    if not assessment: raise HTTPException(404, "Assessment not found")
    if user.role == "instructor" and assessment.created_by != user.id: raise HTTPException(403, "Assessment ownership required")
    version = db.scalar(select(AssessmentVersion).where(AssessmentVersion.assessment_id == assessment.id).order_by(AssessmentVersion.version.desc()))
    if not version: raise HTTPException(409, "A version is required before publishing")
    version.status = "published"; version.published_at = datetime.now(timezone.utc); assessment.status = "published"; audit(db, user, "assessment_published", "assessment_definition", assessment.id); db.commit(); return data(assessment)


@router.get("/{assessment_id}")
def assessment_detail(assessment_id: UUID, user: User = Depends(verified_user), db: Session = Depends(get_db)):
    assessment = db.scalar(select(AssessmentDefinition).where(AssessmentDefinition.id == assessment_id, AssessmentDefinition.status == "published"))
    if not assessment: raise HTTPException(404, "Published assessment not found")
    version = db.scalar(select(AssessmentVersion).where(AssessmentVersion.assessment_id == assessment.id, AssessmentVersion.status == "published").order_by(AssessmentVersion.version.desc()))
    questions = db.scalars(select(AssessmentQuestion).where(AssessmentQuestion.assessment_id == assessment.id).order_by(AssessmentQuestion.position)).all()
    question_data = []
    for question in questions:
        qv = db.scalar(select(AssessmentQuestionVersion).where(AssessmentQuestionVersion.question_id == question.id).order_by(AssessmentQuestionVersion.version.desc()))
        question_data.append({"id": question.id, "question_type": question.question_type, "position": question.position, "points": question.points, "prompt": qv.prompt if qv else "", "options": json.loads(qv.options_json or "[]") if qv else []})
    return {"assessment": data(assessment), "version": data(version) if version else None, "questions": question_data}


@router.post("/{assessment_id}/attempts", status_code=201)
def start_attempt(assessment_id: UUID, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    assessment = db.scalar(select(AssessmentDefinition).where(AssessmentDefinition.id == assessment_id, AssessmentDefinition.status == "published")); version = db.scalar(select(AssessmentVersion).where(AssessmentVersion.assessment_id == assessment_id, AssessmentVersion.status == "published").order_by(AssessmentVersion.version.desc()))
    if not assessment or not version: raise HTTPException(404, "Published assessment not found")
    count = db.scalar(select(func.count()).select_from(AssessmentAttempt).where(AssessmentAttempt.assessment_id == assessment.id, AssessmentAttempt.user_id == user.id)) or 0
    if count >= assessment.attempt_limit: raise HTTPException(409, "Assessment attempt limit reached")
    expires = datetime.now(timezone.utc) + timedelta(minutes=assessment.time_limit_minutes) if assessment.time_limit_minutes else None
    row = AssessmentAttempt(assessment_id=assessment.id, version_id=version.id, user_id=user.id, attempt_number=count + 1, expires_at=expires); db.add(row); db.flush(); db.add(AssessmentAttemptEvent(attempt_id=row.id, actor_id=user.id, event_type="started")); db.commit(); db.refresh(row); return data(row)


@router.put("/attempts/{attempt_id}/answers")
def save_answer(attempt_id: UUID, payload: AnswerIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    attempt = db.scalar(select(AssessmentAttempt).where(AssessmentAttempt.id == attempt_id, AssessmentAttempt.user_id == user.id))
    if not attempt: raise HTTPException(404, "Assessment attempt not found")
    if attempt.status != "active": raise HTTPException(409, "Attempt is no longer active")
    if attempt.expires_at and attempt.expires_at <= datetime.now(timezone.utc): attempt.status = "expired"; db.commit(); raise HTTPException(409, "Assessment attempt expired")
    question = db.scalar(select(AssessmentQuestion).where(AssessmentQuestion.id == payload.question_id, AssessmentQuestion.assessment_id == attempt.assessment_id))
    if not question: raise HTTPException(404, "Question not found")
    row = db.scalar(select(AssessmentAttemptAnswer).where(AssessmentAttemptAnswer.attempt_id == attempt.id, AssessmentAttemptAnswer.question_id == question.id)) or AssessmentAttemptAnswer(attempt_id=attempt.id, question_id=question.id, answer_json="")
    row.answer_json = json.dumps(payload.answer, sort_keys=True); db.add(row); db.commit(); return {"saved": True, "attempt_id": attempt.id, "question_id": question.id}


@router.post("/attempts/{attempt_id}/submit")
def finalize_attempt(attempt_id: UUID, payload: FinalizeIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    attempt = db.scalar(select(AssessmentAttempt).where(AssessmentAttempt.id == attempt_id, AssessmentAttempt.user_id == user.id))
    if not attempt: raise HTTPException(404, "Assessment attempt not found")
    if attempt.status in {"submitted", "graded", "expired"}: return {"id": attempt.id, "status": attempt.status, "score": attempt.score, "idempotent": True}
    if attempt.expires_at and attempt.expires_at <= datetime.now(timezone.utc): attempt.status = "expired"; db.commit(); raise HTTPException(409, "Assessment attempt expired")
    answers = db.scalars(select(AssessmentAttemptAnswer).where(AssessmentAttemptAnswer.attempt_id == attempt.id)).all(); questions = db.scalars(select(AssessmentQuestion).where(AssessmentQuestion.assessment_id == attempt.assessment_id)).all(); total = sum(q.points for q in questions) or 1; earned = 0
    for answer in answers:
        qv = db.scalar(select(AssessmentQuestionVersion).where(AssessmentQuestionVersion.question_id == answer.question_id).order_by(AssessmentQuestionVersion.version.desc()))
        if qv and qv.answer_hash and qv.answer_hash == answer_hash(json.loads(answer.answer_json)): earned += next((q.points for q in questions if q.id == answer.question_id), 0)
    attempt.status = "submitted"; attempt.submitted_at = datetime.now(timezone.utc); attempt.score = round(earned / total * 100); attempt.finalized_key = payload.idempotency_key
    db.add(AssessmentAttemptEvent(attempt_id=attempt.id, actor_id=user.id, event_type="submitted")); db.add(AssessmentGradingJob(attempt_id=attempt.id, job_key=payload.idempotency_key, status="complete")); db.add(AssessmentGradingResult(attempt_id=attempt.id, score=attempt.score, passed=attempt.score >= 70, result_json=json.dumps({"source": "deterministic_answer_keys"}))); audit(db, user, "assessment_submitted", "assessment_attempt", attempt.id); db.commit(); return {"id": attempt.id, "status": attempt.status, "score": attempt.score, "passed": attempt.score >= 70, "grading": "deterministic"}


@router.post("/attempts/{attempt_id}/appeals", status_code=201)
def appeal(attempt_id: UUID, payload: AppealIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    check_rate_limit(f"assessment-appeal:{user.id}", limit=5, window_seconds=3600)
    attempt = db.scalar(select(AssessmentAttempt).where(AssessmentAttempt.id == attempt_id, AssessmentAttempt.user_id == user.id))
    if not attempt: raise HTTPException(404, "Assessment attempt not found")
    row = AssessmentAppeal(attempt_id=attempt.id, appellant_id=user.id, reason=payload.reason, evidence=payload.evidence); db.add(row); audit(db, user, "assessment_appeal_submitted", "assessment_appeal", row.id); db.commit(); db.refresh(row); return data(row)


@router.get("/instructor/grading")
def grading_queue(user: User = Depends(reviewer), db: Session = Depends(get_db)):
    query = select(AssessmentAttempt).where(AssessmentAttempt.status.in_(["submitted", "graded"]))
    if user.role == "instructor": query = query.join(AssessmentDefinition, AssessmentDefinition.id == AssessmentAttempt.assessment_id).where(AssessmentDefinition.created_by == user.id)
    return [data(row) for row in db.scalars(query.order_by(AssessmentAttempt.updated_at.desc()).limit(100)).all()]


@router.post("/attempts/{attempt_id}/grade")
def grade_attempt(attempt_id: UUID, payload: GradeIn, user: User = Depends(reviewer), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    attempt = db.get(AssessmentAttempt, attempt_id)
    if not attempt: raise HTTPException(404, "Assessment attempt not found")
    assessment = db.get(AssessmentDefinition, attempt.assessment_id)
    if user.role == "instructor" and (not assessment or assessment.created_by != user.id): raise HTTPException(403, "Assessment grading scope required")
    previous = attempt.score; attempt.score = payload.score; attempt.status = "graded"; db.add(AssessmentGradeRevision(attempt_id=attempt.id, previous_score=previous, revised_score=payload.score, reviewer_id=user.id, reason=payload.reason)); audit(db, user, "grade_revised", "assessment_attempt", attempt.id); db.commit(); return data(attempt)


@router.get("/integrity")
def integrity_queue(user: User = Depends(platform_admin), db: Session = Depends(get_db)):
    cases = db.scalars(select(AssessmentIntegrityCase).where(AssessmentIntegrityCase.status == "open").order_by(AssessmentIntegrityCase.created_at.desc()).limit(100)).all()
    return {"cases": [data(row) for row in cases], "policy": "Signals require human review; similarity or timing alone never declares cheating."}


@router.post("/integrity/{case_id}/decision")
def integrity_decision(case_id: UUID, decision: str = Query(..., pattern="^(no_action|policy_violation|needs_more_evidence)$"), note: str = Query("", max_length=5000), user: User = Depends(platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(AssessmentIntegrityCase, case_id)
    if not row: raise HTTPException(404, "Integrity case not found")
    row.status = "reviewed"; row.decision = decision; row.reviewer_id = user.id; row.decision_note = note; audit(db, user, "integrity_case_reviewed", "assessment_integrity_case", row.id); db.commit(); return data(row)


@router.get("/analytics/{assessment_id}")
def analytics(assessment_id: UUID, user: User = Depends(reviewer), db: Session = Depends(get_db)):
    assessment = db.get(AssessmentDefinition, assessment_id)
    if not assessment or (user.role == "instructor" and assessment.created_by != user.id): raise HTTPException(404, "Assessment not found")
    attempts = db.scalar(select(func.count()).select_from(AssessmentAttempt).where(AssessmentAttempt.assessment_id == assessment.id)) or 0
    if attempts < 5: return {"suppressed": True, "attempts": attempts, "minimum_group_size": 5}
    passed = db.scalar(select(func.count()).select_from(AssessmentAttempt).where(AssessmentAttempt.assessment_id == assessment.id, AssessmentAttempt.score >= 70)) or 0
    return {"suppressed": False, "attempts": attempts, "passed": passed, "pass_rate": round(passed / attempts * 100, 2)}


@router.get("/platform/credentials")
def platform_credentials(user: User = Depends(platform_admin), db: Session = Depends(get_db)):
    return {"awards": [data(row) for row in db.scalars(select(CredentialAward).order_by(CredentialAward.issued_at.desc()).limit(100)).all()], "audit_source": "credential_awards"}


@router.post("/platform/credentials", status_code=201)
def issue_credential(payload: CredentialIn, user: User = Depends(platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if db.scalar(select(CredentialAward).where(CredentialAward.user_id == payload.user_id, CredentialAward.credential_type == payload.credential_type, CredentialAward.source_id == payload.source_id)):
        raise HTTPException(409, "Credential already issued")
    if payload.credential_type == "competency" and not db.scalar(select(StudentCompetencyRecord).where(StudentCompetencyRecord.user_id == payload.user_id, StudentCompetencyRecord.id == payload.source_id, StudentCompetencyRecord.verified.is_(True))):
        raise HTTPException(403, "Verified competency evidence required")
    row = CredentialAward(user_id=payload.user_id, credential_type=payload.credential_type, title=payload.title, source_id=payload.source_id, verification_id=f"cm-{uuid4().hex}", public=payload.public); db.add(row); db.flush(); db.add(CredentialStatusEvent(credential_id=row.id, actor_id=user.id, to_status="active", reason="Eligibility verified by platform operator")); audit(db, user, "credential_issued", "credential_award", row.id); db.commit(); db.refresh(row); return data(row)


@router.post("/platform/credentials/{credential_id}/revoke")
def revoke_credential(credential_id: UUID, reason: str = Query(..., min_length=3, max_length=500), user: User = Depends(platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(CredentialAward, credential_id)
    if not row: raise HTTPException(404, "Credential not found")
    if row.status == "revoked": return data(row)
    old = row.status; row.status = "revoked"; row.revoked_at = datetime.now(timezone.utc); db.add(CredentialStatusEvent(credential_id=row.id, actor_id=user.id, from_status=old, to_status="revoked", reason=reason)); audit(db, user, "credential_revoked", "credential_award", row.id); db.commit(); return data(row)
