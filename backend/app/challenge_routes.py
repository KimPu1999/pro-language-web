import json
import re
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .admin_routes import admin_user, audit, full_admin
from .auth import current_user, require_csrf, verified_user
from .config import settings
from .db import get_db
from .models import (
    AchievementDefinition, Challenge, ChallengeCategory, ChallengeHint,
    ChallengeLanguageConfig, ChallengeSubmission, ChallengeTestCase,
    ChallengeTopic, ChallengeTopicLink, CodeExecutionJob, CodeExecutionResult,
    DailyChallenge, StudentAchievement, StudentChallengeProgress, User,
)
from .runner_queue import queue
from .runner_registry import get_runtime

router = APIRouter(prefix="/api/v1/challenges", tags=["challenges"])
CHALLENGE_TYPES = {"coding", "quiz", "debugging"}
DIFFICULTIES = {"beginner", "easy", "medium", "hard", "expert", "intermediate", "professional"}
EXECUTION_MODES = {"stdin", "function"}


class SubmissionIn(BaseModel):
    language: str
    source_code: str = Field(min_length=1, max_length=100000)


class QuizAnswerIn(BaseModel):
    answer: str = Field(min_length=1, max_length=1000)


class ChallengeCreate(BaseModel):
    title: str = Field(default="Untitled challenge", max_length=180)
    slug: str | None = Field(default=None, pattern=r"^[a-z0-9-]+$", max_length=180)
    description_en: str = Field(default="", max_length=30000)
    description_mm: str | None = Field(default=None, max_length=30000)
    difficulty: str = "beginner"
    category_id: UUID | None = None
    challenge_type: str = "coding"
    tags: list[str] = Field(default_factory=list, max_length=30)
    estimated_minutes: int = Field(default=30, ge=1, le=1440)
    input_format: str = Field(default="", max_length=10000)
    output_format: str = Field(default="", max_length=10000)
    explanation_en: str = Field(default="", max_length=30000)
    execution_mode: str = "stdin"
    reference_solution: str | None = Field(default=None, max_length=100000)
    quiz_mode: str | None = Field(default=None, pattern=r"^(single|multiple)$")
    quiz_options: list[str] = Field(default_factory=list, max_length=10)
    quiz_correct_answer: str | None = Field(default=None, max_length=1000)
    quiz_explanation: str = Field(default="", max_length=10000)
    examples: list[dict | str] = Field(default_factory=list, max_length=20)
    constraints: list[str] = Field(default_factory=list, max_length=30)

    @field_validator("challenge_type")
    @classmethod
    def valid_type(cls, value: str):
        if value not in CHALLENGE_TYPES:
            raise ValueError("Challenge type must be coding, quiz, or debugging")
        return value

    @field_validator("difficulty")
    @classmethod
    def valid_difficulty(cls, value: str):
        if value not in DIFFICULTIES:
            raise ValueError("Invalid difficulty")
        return value

    @field_validator("execution_mode")
    @classmethod
    def valid_execution_mode(cls, value: str):
        if value not in EXECUTION_MODES:
            raise ValueError("Execution mode must be stdin or function")
        return value

    @field_validator("tags")
    @classmethod
    def clean_tags(cls, values: list[str]):
        cleaned = [value.strip().lower() for value in values if value.strip()]
        if len(cleaned) != len(set(cleaned)):
            raise ValueError("Tags must be unique")
        return cleaned


class ChallengeUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=180)
    slug: str | None = Field(default=None, pattern=r"^[a-z0-9-]+$", max_length=180)
    description_en: str | None = Field(default=None, max_length=30000)
    description_mm: str | None = Field(default=None, max_length=30000)
    difficulty: str | None = None
    category_id: UUID | None = None
    challenge_type: str | None = None
    tags: list[str] | None = Field(default=None, max_length=30)
    estimated_minutes: int | None = Field(default=None, ge=1, le=1440)
    input_format: str | None = Field(default=None, max_length=10000)
    output_format: str | None = Field(default=None, max_length=10000)
    explanation_en: str | None = Field(default=None, max_length=30000)
    execution_mode: str | None = None
    reference_solution: str | None = Field(default=None, max_length=100000)
    quiz_mode: str | None = Field(default=None, pattern=r"^(single|multiple)$")
    quiz_options: list[str] | None = Field(default=None, max_length=10)
    quiz_correct_answer: str | None = Field(default=None, max_length=1000)
    quiz_explanation: str | None = Field(default=None, max_length=10000)
    examples: list[dict | str] | None = Field(default=None, max_length=20)
    constraints: list[str] | None = Field(default=None, max_length=30)


class TestIn(BaseModel):
    input_data: str = Field(default="", max_length=50000)
    expected_output: str = Field(default="", max_length=50000)
    is_hidden: bool = True
    points: int = Field(default=1, ge=1, le=100)
    position: int = Field(default=0, ge=0)


class TestUpdate(BaseModel):
    input_data: str | None = Field(default=None, max_length=50000)
    expected_output: str | None = Field(default=None, max_length=50000)
    is_hidden: bool | None = None
    points: int | None = Field(default=None, ge=1, le=100)
    position: int | None = Field(default=None, ge=0)


class LanguageIn(BaseModel):
    language: str = Field(min_length=1, max_length=30)
    starter_code: str = Field(default="", max_length=100000)
    time_limit_ms: int = Field(default=2000, ge=100, le=30000)
    memory_limit_mb: int = Field(default=128, ge=16, le=1024)


class LanguageUpdate(BaseModel):
    language: str | None = Field(default=None, max_length=30)
    starter_code: str | None = Field(default=None, max_length=100000)
    time_limit_ms: int | None = Field(default=None, ge=100, le=30000)
    memory_limit_mb: int | None = Field(default=None, ge=16, le=1024)


class CategoryIn(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(pattern=r"^[a-z0-9-]+$", max_length=100)
    description: str = Field(default="", max_length=4000)
    status: str = Field(default="active", pattern=r"^(active|inactive)$")


class ReorderIn(BaseModel):
    ids: list[UUID] = Field(min_length=1, max_length=500)


class SubmissionReviewIn(BaseModel):
    status: str = Field(pattern=r"^(accepted|rejected|reviewed)$")
    score: int | None = Field(default=None, ge=0, le=100)


class HintIn(BaseModel):
    body_en: str = Field(min_length=1, max_length=10000)
    position: int = Field(default=0, ge=0)


def json_list(value: str | None):
    try:
        parsed = json.loads(value or "[]")
        return parsed if isinstance(parsed, list) else []
    except (TypeError, ValueError, json.JSONDecodeError):
        return []


def make_slug(title: str):
    value = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "challenge"
    return f"{value}-{str(uuid4())[:8]}"


def public_challenge(row, db, user_id=None):
    configs = db.scalars(select(ChallengeLanguageConfig).where(ChallengeLanguageConfig.challenge_id == row.id).order_by(ChallengeLanguageConfig.language)).all()
    topics = db.scalars(select(ChallengeTopic).join(ChallengeTopicLink, ChallengeTopic.id == ChallengeTopicLink.topic_id).where(ChallengeTopicLink.challenge_id == row.id)).all()
    solved = False
    if user_id:
        solved = db.scalar(select(StudentChallengeProgress.solved).where(StudentChallengeProgress.user_id == user_id, StudentChallengeProgress.challenge_id == row.id)) or False
    category = db.get(ChallengeCategory, row.category_id) if row.category_id else None
    return {"id": row.id, "title": row.title, "slug": row.slug, "description_en": row.description_en, "description_mm": row.description_mm, "examples": json_list(row.examples_json), "constraints": json_list(row.constraints_json), "difficulty": row.difficulty, "status": row.status, "challenge_type": row.challenge_type, "tags": json_list(row.tags_json), "estimated_minutes": row.estimated_minutes, "input_format": row.input_format, "output_format": row.output_format, "execution_mode": row.execution_mode, "category_id": row.category_id, "category": ({"name": category.name, "slug": category.slug} if category else None), "languages": [{"language": x.language, "starter_code": x.starter_code, "time_limit_ms": x.time_limit_ms, "memory_limit_mb": x.memory_limit_mb} for x in configs], "topics": [{"name": x.name, "slug": x.slug} for x in topics], "quiz_mode": row.quiz_mode if row.challenge_type == "quiz" else None, "quiz_options": json_list(row.quiz_options_json) if row.challenge_type == "quiz" else [], "solved": solved}


def admin_challenge(row, db):
    result = public_challenge(row, db)
    result.update({"explanation_en": row.explanation_en, "reference_solution": row.reference_solution, "quiz_correct_answer": row.quiz_correct_answer, "quiz_explanation": row.quiz_explanation, "published": row.published, "created_by": row.created_by, "created_at": row.created_at, "updated_at": row.updated_at, "languages": [{"id": x.id, "language": x.language, "starter_code": x.starter_code, "time_limit_ms": x.time_limit_ms, "memory_limit_mb": x.memory_limit_mb} for x in db.scalars(select(ChallengeLanguageConfig).where(ChallengeLanguageConfig.challenge_id == row.id).order_by(ChallengeLanguageConfig.language)).all()], "tests": [{"id": t.id, "input_data": t.input_data, "expected_output": t.expected_output, "is_hidden": t.is_hidden, "points": t.points, "position": t.position} for t in db.scalars(select(ChallengeTestCase).where(ChallengeTestCase.challenge_id == row.id).order_by(ChallengeTestCase.position, ChallengeTestCase.created_at)).all()], "hints": [{"id": h.id, "body_en": h.body_en, "position": h.position} for h in db.scalars(select(ChallengeHint).where(ChallengeHint.challenge_id == row.id).order_by(ChallengeHint.position)).all()]})
    return result


def validate_content(row, db, require_runner=False):
    errors = []
    if not row.title.strip() or row.title.strip().lower() == "untitled challenge": errors.append("A challenge title is required.")
    if not row.description_en.strip(): errors.append("English problem statement is required.")
    if row.challenge_type == "quiz":
        options = json_list(row.quiz_options_json)
        if len(options) < 2: errors.append("A quiz needs at least two answer options.")
        if not row.quiz_correct_answer or row.quiz_correct_answer not in options: errors.append("The correct quiz answer must match an option.")
    else:
        if not db.scalar(select(func.count(ChallengeLanguageConfig.id)).where(ChallengeLanguageConfig.challenge_id == row.id)): errors.append("At least one supported language is required.")
        if not db.scalar(select(func.count(ChallengeTestCase.id)).where(ChallengeTestCase.challenge_id == row.id)): errors.append("At least one test case is required.")
        if require_runner and row.reference_solution:
            if not settings.runner_enabled: raise HTTPException(503, "Secure code runner is unavailable; reference solution validation cannot run.")
            raise HTTPException(503, "Reference solution validation service is not configured for this deployment.")
    return errors


def apply_challenge_values(row, values):
    mapping = {"tags": "tags_json", "quiz_options": "quiz_options_json", "examples": "examples_json", "constraints": "constraints_json"}
    for key, value in values.items():
        key = mapping.get(key, key)
        if key in {"tags_json", "quiz_options_json", "examples_json", "constraints_json"}: value = json.dumps(value, ensure_ascii=False)
        if hasattr(row, key): setattr(row, key, value)


@router.get("/categories")
def list_challenge_categories(db: Session = Depends(get_db)):
    return db.scalars(select(ChallengeCategory).where(ChallengeCategory.status == "active").order_by(ChallengeCategory.name)).all()


@router.get("/topics")
def list_challenge_topics(db: Session = Depends(get_db)):
    return db.scalars(select(ChallengeTopic).order_by(ChallengeTopic.name)).all()


@router.get("/progress/me")
@router.get("/me/challenge-progress")
def progress(user: User = Depends(current_user), db: Session = Depends(get_db)):
    attempts = db.scalar(select(func.count(ChallengeSubmission.id)).where(ChallengeSubmission.user_id == user.id)) or 0; solved = db.scalar(select(func.count(StudentChallengeProgress.id)).where(StudentChallengeProgress.user_id == user.id, StudentChallengeProgress.solved.is_(True))) or 0
    return {"attempts": attempts, "solved": solved, "acceptance_rate": round(solved / attempts * 100, 2) if attempts else 0}


@router.get("")
def list_challenges(search: str | None = None, difficulty: str | None = None, language: str | None = None, category: str | None = None, topic: str | None = None, challenge_type: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=50), db: Session = Depends(get_db)):
    q = select(Challenge).where(Challenge.published.is_(True)); count = select(func.count(func.distinct(Challenge.id))).select_from(Challenge).where(Challenge.published.is_(True))
    if search: term = f"%{search}%"; condition = Challenge.title.ilike(term) | Challenge.description_en.ilike(term); q = q.where(condition); count = count.where(condition)
    if difficulty: q = q.where(Challenge.difficulty == difficulty); count = count.where(Challenge.difficulty == difficulty)
    if challenge_type: q = q.where(Challenge.challenge_type == challenge_type); count = count.where(Challenge.challenge_type == challenge_type)
    if language: q = q.join(ChallengeLanguageConfig).where(ChallengeLanguageConfig.language == language); count = count.join(ChallengeLanguageConfig).where(ChallengeLanguageConfig.language == language)
    if category: q = q.join(ChallengeCategory).where(ChallengeCategory.slug == category); count = count.join(ChallengeCategory).where(ChallengeCategory.slug == category)
    if topic: q = q.join(ChallengeTopicLink).join(ChallengeTopic).where(ChallengeTopic.slug == topic); count = count.join(ChallengeTopicLink).join(ChallengeTopic).where(ChallengeTopic.slug == topic)
    total = db.scalar(count) or 0; rows = db.scalars(q.order_by(Challenge.display_order, Challenge.title).offset((page - 1) * page_size).limit(page_size)).unique().all()
    return {"items": [public_challenge(x, db) for x in rows], "page": page, "page_size": page_size, "total": total, "pages": (total + page_size - 1) // page_size if total else 0}


@router.get("/{challenge_id}/hints")
def challenge_hints(challenge_id: UUID, db: Session = Depends(get_db)):
    if not db.scalar(select(Challenge.id).where(Challenge.id == challenge_id, Challenge.published.is_(True))): raise HTTPException(404, "Challenge not found")
    return db.scalars(select(ChallengeHint).where(ChallengeHint.challenge_id == challenge_id).order_by(ChallengeHint.position)).all()


@router.get("/submissions/history")
def history(challenge_id: UUID | None = None, user: User = Depends(current_user), db: Session = Depends(get_db)):
    q = select(ChallengeSubmission).where(ChallengeSubmission.user_id == user.id).order_by(ChallengeSubmission.created_at.desc()).limit(50)
    if challenge_id: q = q.where(ChallengeSubmission.challenge_id == challenge_id)
    return db.scalars(q).all()


@router.get("/daily/today")
def daily(user: User | None = Depends(current_user), db: Session = Depends(get_db)):
    today = datetime.now(timezone.utc).date(); row = db.scalar(select(DailyChallenge).where(func.date(DailyChallenge.challenge_date) == today))
    if not row: return {"challenge": None, "completed": False}
    challenge = db.get(Challenge, row.challenge_id); solved = db.scalar(select(StudentChallengeProgress.solved).where(StudentChallengeProgress.user_id == user.id, StudentChallengeProgress.challenge_id == row.challenge_id)) if user else False
    return {"date": today.isoformat(), "challenge": public_challenge(challenge, db, user.id if user else None), "completed": bool(solved)}


@router.get("/skills/me")
def skills(user: User = Depends(current_user), db: Session = Depends(get_db)):
    attempts = db.scalar(select(func.count(ChallengeSubmission.id)).where(ChallengeSubmission.user_id == user.id)) or 0; solved = db.scalar(select(func.count(StudentChallengeProgress.id)).where(StudentChallengeProgress.user_id == user.id, StudentChallengeProgress.solved.is_(True))) or 0; accepted = db.scalar(select(func.count(ChallengeSubmission.id)).where(ChallengeSubmission.user_id == user.id, ChallengeSubmission.status == "accepted")) or 0
    return {"attempts": attempts, "solved": solved, "acceptance_rate": round(accepted / attempts * 100, 2) if attempts else 0, "difficulty_distribution": [], "topic_progress": [], "recent_submissions": db.scalars(select(ChallengeSubmission).where(ChallengeSubmission.user_id == user.id).order_by(ChallengeSubmission.created_at.desc()).limit(10)).all()}


@router.get("/achievements/me")
def achievements(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.execute(select(AchievementDefinition, StudentAchievement.awarded_at).join(StudentAchievement, StudentAchievement.achievement_id == AchievementDefinition.id).where(StudentAchievement.user_id == user.id)).all(); return [{"slug": d.slug, "title": d.title, "description": d.description, "awarded_at": awarded} for d, awarded in rows]


# Admin static routes are before /{slug} so admin URLs never hit public slug routing.
@router.get("/admin")
def admin_list(search: str | None = None, status: str | None = None, difficulty: str | None = None, challenge_type: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=100), user: User = Depends(admin_user), db: Session = Depends(get_db)):
    query = select(Challenge).order_by(Challenge.display_order, Challenge.updated_at.desc()); filters = []
    if search: filters.append(Challenge.title.ilike(f"%{search}%"))
    if status: filters.append(Challenge.status == status)
    if difficulty: filters.append(Challenge.difficulty == difficulty)
    if challenge_type: filters.append(Challenge.challenge_type == challenge_type)
    if filters: query = query.where(*filters)
    total = db.scalar(select(func.count(Challenge.id)).where(*filters)) if filters else db.scalar(select(func.count(Challenge.id)))
    rows = db.scalars(query.offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [admin_challenge(row, db) for row in rows], "page": page, "page_size": page_size, "total": total or 0, "pages": ((total or 0) + page_size - 1) // page_size if total else 0}


@router.get("/admin/categories")
def admin_categories(user: User = Depends(admin_user), db: Session = Depends(get_db)):
    return db.scalars(select(ChallengeCategory).order_by(ChallengeCategory.name)).all()


@router.post("/admin/categories", status_code=201)
def admin_category_create(payload: CategoryIn, user: User = Depends(admin_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if db.scalar(select(ChallengeCategory).where(ChallengeCategory.slug == payload.slug)): raise HTTPException(409, "Category slug already exists")
    row = ChallengeCategory(**payload.model_dump()); db.add(row); audit(db, user, "challenge_category_created", "challenge_category", row.id); db.commit(); return row


@router.patch("/admin/categories/{category_id}")
def admin_category_update(category_id: UUID, payload: CategoryIn, user: User = Depends(admin_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(ChallengeCategory, category_id)
    if not row: raise HTTPException(404, "Challenge category not found")
    if db.scalar(select(ChallengeCategory).where(ChallengeCategory.slug == payload.slug, ChallengeCategory.id != category_id)): raise HTTPException(409, "Category slug already exists")
    for key, value in payload.model_dump().items(): setattr(row, key, value)
    audit(db, user, "challenge_category_updated", "challenge_category", row.id); db.commit(); return row


@router.delete("/admin/categories/{category_id}")
def admin_category_delete(category_id: UUID, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(ChallengeCategory, category_id)
    if not row: raise HTTPException(404, "Challenge category not found")
    if db.scalar(select(func.count(Challenge.id)).where(Challenge.category_id == category_id)): raise HTTPException(409, "Category is still assigned to challenges; disable it instead")
    db.delete(row); audit(db, user, "challenge_category_deleted", "challenge_category", category_id); db.commit(); return {"status": "deleted"}


@router.get("/admin/submissions")
def admin_submissions(status: str | None = None, challenge_id: UUID | None = None, page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=100), user: User = Depends(admin_user), db: Session = Depends(get_db)):
    query = select(ChallengeSubmission).order_by(ChallengeSubmission.created_at.desc()); filters = []
    if status: filters.append(ChallengeSubmission.status == status)
    if challenge_id: filters.append(ChallengeSubmission.challenge_id == challenge_id)
    if filters: query = query.where(*filters)
    rows = db.scalars(query.offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [{"id": row.id, "challenge_id": row.challenge_id, "user_id": row.user_id, "language": row.language, "status": row.status, "score": row.score, "runtime_ms": row.runtime_ms, "memory_mb": row.memory_mb, "created_at": row.created_at} for row in rows], "page": page, "page_size": page_size}


@router.get("/admin/submissions/{submission_id}")
def admin_submission_detail(submission_id: UUID, user: User = Depends(admin_user), db: Session = Depends(get_db)):
    row = db.get(ChallengeSubmission, submission_id)
    if not row: raise HTTPException(404, "Submission not found")
    return {"id": row.id, "challenge_id": row.challenge_id, "user_id": row.user_id, "language": row.language, "source_code": row.source_code, "status": row.status, "score": row.score, "runtime_ms": row.runtime_ms, "memory_mb": row.memory_mb, "created_at": row.created_at}


@router.patch("/admin/submissions/{submission_id}")
def admin_submission_review(submission_id: UUID, payload: SubmissionReviewIn, user: User = Depends(admin_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(ChallengeSubmission, submission_id)
    if not row: raise HTTPException(404, "Submission not found")
    row.status = payload.status; row.score = payload.score; audit(db, user, "challenge_submission_reviewed", "challenge_submission", row.id); db.commit(); return {"id": row.id, "status": row.status, "score": row.score}


@router.post("/admin", status_code=201)
def admin_create(payload: ChallengeCreate, user: User = Depends(admin_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    slug = payload.slug or make_slug(payload.title)
    if db.scalar(select(Challenge).where(Challenge.slug == slug)): raise HTTPException(409, "Slug already exists")
    if payload.category_id and not db.get(ChallengeCategory, payload.category_id): raise HTTPException(422, "Challenge category not found")
    values = payload.model_dump(); values["slug"] = slug; values["created_by"] = user.id; values["display_order"] = (db.scalar(select(func.max(Challenge.display_order))) or -1) + 1; row = Challenge(); apply_challenge_values(row, values); row.status = "draft"; row.published = False; db.add(row); audit(db, user, "challenge_created", "challenge", row.id); db.commit(); return admin_challenge(row, db)


@router.get("/admin/reorder")
def admin_reorder_get(user: User = Depends(admin_user), db: Session = Depends(get_db)):
    return [{"id": row.id, "position": row.display_order} for row in db.scalars(select(Challenge).order_by(Challenge.display_order, Challenge.title)).all()]


@router.post("/admin/reorder")
def admin_reorder(payload: ReorderIn, user: User = Depends(admin_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    rows = {row.id: row for row in db.scalars(select(Challenge).where(Challenge.id.in_(payload.ids))).all()}
    if set(rows) != set(payload.ids): raise HTTPException(422, "Every challenge id must exist")
    for position, challenge_id in enumerate(payload.ids): rows[challenge_id].display_order = position; audit(db, user, "challenge_reordered", "challenge", challenge_id)
    db.commit(); return {"status": "ok", "ids": payload.ids}


@router.get("/admin/{challenge_id}/tests")
def admin_tests(challenge_id: UUID, user: User = Depends(admin_user), db: Session = Depends(get_db)):
    if not db.get(Challenge, challenge_id): raise HTTPException(404, "Challenge not found")
    return [{"id": t.id, "input_data": t.input_data, "expected_output": t.expected_output, "is_hidden": t.is_hidden, "points": t.points, "position": t.position} for t in db.scalars(select(ChallengeTestCase).where(ChallengeTestCase.challenge_id == challenge_id).order_by(ChallengeTestCase.position, ChallengeTestCase.created_at)).all()]


@router.post("/admin/{challenge_id}/hints", status_code=201)
def admin_hint_create(challenge_id: UUID, payload: HintIn, user: User = Depends(admin_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if not db.get(Challenge, challenge_id): raise HTTPException(404, "Challenge not found")
    row = ChallengeHint(challenge_id=challenge_id, **payload.model_dump()); db.add(row); db.commit(); return {"id": row.id, "body_en": row.body_en, "position": row.position}


@router.patch("/admin/{challenge_id}/hints/{hint_id}")
def admin_hint_update(challenge_id: UUID, hint_id: UUID, payload: HintIn, user: User = Depends(admin_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.scalar(select(ChallengeHint).where(ChallengeHint.id == hint_id, ChallengeHint.challenge_id == challenge_id))
    if not row: raise HTTPException(404, "Hint not found")
    row.body_en = payload.body_en; row.position = payload.position; db.commit(); return {"id": row.id, "body_en": row.body_en, "position": row.position}


@router.delete("/admin/{challenge_id}/hints/{hint_id}")
def admin_hint_delete(challenge_id: UUID, hint_id: UUID, user: User = Depends(admin_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.scalar(select(ChallengeHint).where(ChallengeHint.id == hint_id, ChallengeHint.challenge_id == challenge_id))
    if not row: raise HTTPException(404, "Hint not found")
    db.delete(row); db.commit(); return {"status": "deleted"}


@router.post("/admin/{challenge_id}/tests", status_code=201)
def admin_test(challenge_id: UUID, payload: TestIn, user: User = Depends(admin_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if not db.get(Challenge, challenge_id): raise HTTPException(404, "Challenge not found")
    row = ChallengeTestCase(challenge_id=challenge_id, **payload.model_dump()); db.add(row); db.commit(); return {"id": row.id, "is_hidden": row.is_hidden, "position": row.position}


@router.patch("/admin/{challenge_id}/tests/{test_id}")
def admin_test_update(challenge_id: UUID, test_id: UUID, payload: TestUpdate, user: User = Depends(admin_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.scalar(select(ChallengeTestCase).where(ChallengeTestCase.id == test_id, ChallengeTestCase.challenge_id == challenge_id))
    if not row: raise HTTPException(404, "Test case not found")
    for key, value in payload.model_dump(exclude_unset=True).items(): setattr(row, key, value)
    db.commit(); return {"id": row.id, "is_hidden": row.is_hidden, "position": row.position}


@router.delete("/admin/{challenge_id}/tests/{test_id}")
def admin_test_delete(challenge_id: UUID, test_id: UUID, user: User = Depends(admin_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.scalar(select(ChallengeTestCase).where(ChallengeTestCase.id == test_id, ChallengeTestCase.challenge_id == challenge_id))
    if not row: raise HTTPException(404, "Test case not found")
    db.delete(row); db.commit(); return {"status": "deleted"}


@router.get("/admin/{challenge_id}/languages")
def admin_languages(challenge_id: UUID, user: User = Depends(admin_user), db: Session = Depends(get_db)):
    if not db.get(Challenge, challenge_id): raise HTTPException(404, "Challenge not found")
    return db.scalars(select(ChallengeLanguageConfig).where(ChallengeLanguageConfig.challenge_id == challenge_id).order_by(ChallengeLanguageConfig.language)).all()


@router.post("/admin/{challenge_id}/languages", status_code=201)
def admin_language(challenge_id: UUID, payload: LanguageIn, user: User = Depends(admin_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if not db.get(Challenge, challenge_id): raise HTTPException(404, "Challenge not found")
    if db.scalar(select(ChallengeLanguageConfig).where(ChallengeLanguageConfig.challenge_id == challenge_id, ChallengeLanguageConfig.language == payload.language)): raise HTTPException(409, "Language already configured")
    row = ChallengeLanguageConfig(challenge_id=challenge_id, **payload.model_dump()); db.add(row); db.commit(); return row


@router.patch("/admin/{challenge_id}/languages/{language_id}")
def admin_language_update(challenge_id: UUID, language_id: UUID, payload: LanguageUpdate, user: User = Depends(admin_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.scalar(select(ChallengeLanguageConfig).where(ChallengeLanguageConfig.id == language_id, ChallengeLanguageConfig.challenge_id == challenge_id))
    if not row: raise HTTPException(404, "Language configuration not found")
    values = payload.model_dump(exclude_unset=True)
    if values.get("language") and db.scalar(select(ChallengeLanguageConfig).where(ChallengeLanguageConfig.challenge_id == challenge_id, ChallengeLanguageConfig.language == values["language"], ChallengeLanguageConfig.id != language_id)): raise HTTPException(409, "Language already configured")
    for key, value in values.items(): setattr(row, key, value)
    db.commit(); return row


@router.delete("/admin/{challenge_id}/languages/{language_id}")
def admin_language_delete(challenge_id: UUID, language_id: UUID, user: User = Depends(admin_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.scalar(select(ChallengeLanguageConfig).where(ChallengeLanguageConfig.id == language_id, ChallengeLanguageConfig.challenge_id == challenge_id))
    if not row: raise HTTPException(404, "Language configuration not found")
    db.delete(row); db.commit(); return {"status": "deleted"}


@router.get("/admin/{challenge_id}")
def admin_detail(challenge_id: UUID, user: User = Depends(admin_user), db: Session = Depends(get_db)):
    row = db.get(Challenge, challenge_id)
    if not row: raise HTTPException(404, "Challenge not found")
    return admin_challenge(row, db)


@router.patch("/admin/{challenge_id}")
def admin_update(challenge_id: UUID, payload: ChallengeUpdate, user: User = Depends(admin_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(Challenge, challenge_id)
    if not row: raise HTTPException(404, "Challenge not found")
    values = payload.model_dump(exclude_unset=True)
    if "slug" in values and values["slug"] != row.slug and db.scalar(select(Challenge).where(Challenge.slug == values["slug"], Challenge.id != challenge_id)): raise HTTPException(409, "Slug already exists")
    if "category_id" in values and values["category_id"] and not db.get(ChallengeCategory, values["category_id"]): raise HTTPException(422, "Challenge category not found")
    if values.get("challenge_type") and values["challenge_type"] not in CHALLENGE_TYPES: raise HTTPException(422, "Invalid challenge type")
    if values.get("difficulty") and values["difficulty"] not in DIFFICULTIES: raise HTTPException(422, "Invalid difficulty")
    if values.get("execution_mode") and values["execution_mode"] not in EXECUTION_MODES: raise HTTPException(422, "Invalid execution mode")
    apply_challenge_values(row, values); audit(db, user, "challenge_updated", "challenge", row.id); db.commit(); return admin_challenge(row, db)


@router.post("/admin/{challenge_id}/duplicate", status_code=201)
def admin_duplicate(challenge_id: UUID, user: User = Depends(admin_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    source = db.get(Challenge, challenge_id)
    if not source: raise HTTPException(404, "Challenge not found")
    row = Challenge(title=f"{source.title} copy", slug=make_slug(source.title), description_en=source.description_en, description_mm=source.description_mm, examples_json=source.examples_json, constraints_json=source.constraints_json, difficulty=source.difficulty, category_id=source.category_id, created_by=user.id, challenge_type=source.challenge_type, tags_json=source.tags_json, estimated_minutes=source.estimated_minutes, input_format=source.input_format, output_format=source.output_format, explanation_en=source.explanation_en, execution_mode=source.execution_mode, reference_solution=source.reference_solution, quiz_mode=source.quiz_mode, quiz_options_json=source.quiz_options_json, quiz_correct_answer=source.quiz_correct_answer, quiz_explanation=source.quiz_explanation, status="draft", published=False)
    db.add(row); db.flush()
    for language in db.scalars(select(ChallengeLanguageConfig).where(ChallengeLanguageConfig.challenge_id == source.id)).all(): db.add(ChallengeLanguageConfig(challenge_id=row.id, language=language.language, starter_code=language.starter_code, time_limit_ms=language.time_limit_ms, memory_limit_mb=language.memory_limit_mb))
    for test in db.scalars(select(ChallengeTestCase).where(ChallengeTestCase.challenge_id == source.id)).all(): db.add(ChallengeTestCase(challenge_id=row.id, input_data=test.input_data, expected_output=test.expected_output, is_hidden=test.is_hidden, points=test.points, position=test.position))
    audit(db, user, "challenge_duplicated", "challenge", row.id); db.commit(); return admin_challenge(row, db)


@router.post("/admin/{challenge_id}/validate")
def admin_validate(challenge_id: UUID, user: User = Depends(admin_user), db: Session = Depends(get_db)):
    row = db.get(Challenge, challenge_id)
    if not row: raise HTTPException(404, "Challenge not found")
    errors = validate_content(row, db, require_runner=bool(row.reference_solution))
    return {"valid": not errors, "errors": errors, "secure_runner_available": settings.runner_enabled}


@router.post("/admin/{challenge_id}/preview")
def admin_preview(challenge_id: UUID, user: User = Depends(admin_user), db: Session = Depends(get_db)):
    row = db.get(Challenge, challenge_id)
    if not row: raise HTTPException(404, "Challenge not found")
    result = public_challenge(row, db); result["preview"] = True; result["description_en"] = row.description_en; result["hints"] = [{"body_en": h.body_en} for h in db.scalars(select(ChallengeHint).where(ChallengeHint.challenge_id == row.id).order_by(ChallengeHint.position)).all()]; result["public_tests"] = [{"input": t.input_data, "expected_output": t.expected_output, "points": t.points} for t in db.scalars(select(ChallengeTestCase).where(ChallengeTestCase.challenge_id == row.id, ChallengeTestCase.is_hidden.is_(False)).order_by(ChallengeTestCase.position)).all()]; return result


@router.post("/admin/{challenge_id}/publish")
def admin_publish(challenge_id: UUID, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(Challenge, challenge_id)
    if not row: raise HTTPException(404, "Challenge not found")
    errors = validate_content(row, db, require_runner=True)
    if errors: raise HTTPException(422, "; ".join(errors))
    row.published = True; row.status = "published"; audit(db, user, "challenge_published", "challenge", row.id); db.commit(); return {"id": row.id, "status": row.status, "published": row.published}


@router.post("/admin/{challenge_id}/unpublish")
def admin_unpublish(challenge_id: UUID, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(Challenge, challenge_id)
    if not row: raise HTTPException(404, "Challenge not found")
    row.published = False; row.status = "draft"; audit(db, user, "challenge_unpublished", "challenge", row.id); db.commit(); return {"id": row.id, "status": row.status, "published": row.published}


@router.post("/admin/{challenge_id}/archive")
def admin_archive(challenge_id: UUID, user: User = Depends(admin_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(Challenge, challenge_id)
    if not row: raise HTTPException(404, "Challenge not found")
    row.published = False; row.status = "archived"; audit(db, user, "challenge_archived", "challenge", row.id); db.commit(); return {"id": row.id, "status": row.status, "published": row.published}


@router.delete("/admin/{challenge_id}")
def admin_delete(challenge_id: UUID, user: User = Depends(admin_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(Challenge, challenge_id)
    if not row: raise HTTPException(404, "Challenge not found")
    row.published = False; row.status = "archived"; audit(db, user, "challenge_archived", "challenge", row.id); db.commit(); return {"id": row.id, "status": row.status}


@router.get("/{slug}")
def get_challenge(slug: str, db: Session = Depends(get_db)):
    row = db.scalar(select(Challenge).where(Challenge.slug == slug, Challenge.published.is_(True)))
    if not row: raise HTTPException(404, "Challenge not found")
    hints = db.scalars(select(ChallengeHint).where(ChallengeHint.challenge_id == row.id).order_by(ChallengeHint.position)).all(); result = public_challenge(row, db); result["hints"] = [{"body_en": h.body_en, "body_mm": h.body_mm} for h in hints]; result["public_tests"] = [{"input": t.input_data, "expected_output": t.expected_output, "points": t.points} for t in db.scalars(select(ChallengeTestCase).where(ChallengeTestCase.challenge_id == row.id, ChallengeTestCase.is_hidden.is_(False)).order_by(ChallengeTestCase.position)).all()]; return result


def create_submission(challenge, payload, user, db):
    try: get_runtime(payload.language)
    except ValueError: raise HTTPException(422, "Unsupported language")
    config = db.scalar(select(ChallengeLanguageConfig).where(ChallengeLanguageConfig.challenge_id == challenge.id, ChallengeLanguageConfig.language == payload.language))
    if not config: raise HTTPException(422, "Language is not enabled for this challenge")
    job = CodeExecutionJob(user_id=user.id, exercise_id=None, language=payload.language, source_code=payload.source_code, status="queued", expires_at=datetime.now(timezone.utc) + timedelta(minutes=10)); db.add(job); db.flush(); submission = ChallengeSubmission(user_id=user.id, challenge_id=challenge.id, job_id=job.id, language=payload.language, source_code=payload.source_code, status="queued"); db.add(submission); db.flush()
    if not queue.enqueue(str(job.id)):
        job.status = "runner_unavailable"; submission.status = "runner_unavailable"; job.finished_at = datetime.now(timezone.utc); db.add(CodeExecutionResult(job_id=job.id, stderr="The secure execution runner is unavailable.", error_code="RUNNER_UNAVAILABLE"))
    db.commit(); return {"id": submission.id, "status": submission.status, "score": submission.score, "job_id": job.id}


@router.post("/{challenge_id}/run", status_code=202)
def run_samples(challenge_id: UUID, payload: SubmissionIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    challenge = db.scalar(select(Challenge).where(Challenge.id == challenge_id, Challenge.published.is_(True)))
    if not challenge: raise HTTPException(404, "Challenge not found")
    if challenge.challenge_type == "quiz": raise HTTPException(422, "Quiz challenges use answer submission, not code execution")
    return create_submission(challenge, payload, user, db)


@router.post("/{challenge_id}/submit", status_code=202)
def submit(challenge_id: UUID, payload: SubmissionIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    challenge = db.scalar(select(Challenge).where(Challenge.id == challenge_id, Challenge.published.is_(True)))
    if not challenge: raise HTTPException(404, "Challenge not found")
    if challenge.challenge_type == "quiz": raise HTTPException(422, "Quiz challenges use answer submission, not code execution")
    return create_submission(challenge, payload, user, db)


@router.post("/{challenge_id}/answer", status_code=201)
def submit_quiz_answer(challenge_id: UUID, payload: QuizAnswerIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    challenge = db.scalar(select(Challenge).where(Challenge.id == challenge_id, Challenge.published.is_(True)))
    if not challenge: raise HTTPException(404, "Challenge not found")
    if challenge.challenge_type != "quiz": raise HTTPException(422, "Only quiz challenges accept answer submissions")
    correct = payload.answer == challenge.quiz_correct_answer; submission = ChallengeSubmission(user_id=user.id, challenge_id=challenge.id, language="quiz", source_code=payload.answer, status="accepted" if correct else "rejected", score=100 if correct else 0); db.add(submission); progress_row = db.scalar(select(StudentChallengeProgress).where(StudentChallengeProgress.user_id == user.id, StudentChallengeProgress.challenge_id == challenge.id)) or StudentChallengeProgress(user_id=user.id, challenge_id=challenge.id); progress_row.attempts = (progress_row.attempts or 0) + 1; progress_row.solved = correct; progress_row.solved_at = datetime.now(timezone.utc) if correct else None; db.add(progress_row); db.commit(); return {"id": submission.id, "status": submission.status, "score": submission.score}
