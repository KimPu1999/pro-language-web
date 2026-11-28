"""Course-scoped syntax/reference library APIs."""
import json
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from .auth import require_csrf
from .db import get_db
from .models import (
    AdminAuditLog, Course, CourseModule, Lesson, LessonSyntaxReference,
    SyntaxReference, SyntaxReferenceExample, SyntaxReferenceTranslation,
    SyntaxReferenceVersion, User,
)
from .rbac import require_platform_admin
from .schemas import LessonSyntaxReferencesIn, SyntaxReferenceIn, SyntaxReferenceOut

router = APIRouter(tags=["syntax-references"])
LOCALES = {"en", "my"}
REVIEW_STATES = {"draft", "in_review", "changes_requested", "approved", "published", "archived"}


def _translation(row: SyntaxReference, locale: str):
    if locale not in LOCALES or locale == "en":
        return None
    return next((item for item in row.translations if item.locale == locale and item.status in {"approved", "published"}), None)


def _example_translation(example: SyntaxReferenceExample, locale: str):
    if locale not in LOCALES or locale == "en":
        return None
    return next((item for item in example.translations if item.locale == locale and item.status in {"approved", "published"}), None)


def serialize(row: SyntaxReference, locale: str = "en") -> dict:
    locale = locale if locale in LOCALES else "en"
    translation = _translation(row, locale)
    fields = {
        "title": row.title, "description": row.description, "purpose": row.purpose,
        "syntax_format": row.syntax_format or row.basic_syntax, "parameters": row.parameters,
        "return_value": row.return_value, "version_compatibility": row.version_compatibility,
        "input_output": row.input_output, "common_mistakes": row.common_mistakes,
        "best_practices": row.best_practices, "practice_exercises": row.practice_exercises,
        "further_reading": row.further_reading,
    }
    translation_status = "available" if locale == "en" else ("available" if translation else "missing")
    if translation:
        for key in fields:
            value = getattr(translation, key, "")
            if value:
                fields[key] = value
    elif locale == "my":
        for key in ("description", "purpose", "parameters", "return_value", "version_compatibility", "input_output", "common_mistakes", "best_practices", "practice_exercises", "further_reading"):
            fields[key] = ""
    examples = []
    for item in row.examples:
        item_translation = _example_translation(item, locale)
        examples.append({
            "id": item.id, "example_number": item.example_number,
            "title": item_translation.title if item_translation and item_translation.title else item.title,
            "code": item.code, "language": item.language, "difficulty": item.difficulty,
            "description": item_translation.description if item_translation else (item.description if locale == "en" else ""),
            "setup": item_translation.setup if item_translation else (item.setup if locale == "en" else ""),
            "sample_input": item_translation.sample_input if item_translation else (item.sample_input if locale == "en" else ""),
            "expected_output": item_translation.expected_output if item_translation else (item.expected_output if locale == "en" else ""),
            "explanation": item_translation.explanation if item_translation else (item.explanation if locale == "en" else ""),
            "common_mistakes": item_translation.common_mistakes if item_translation else (item.common_mistakes if locale == "en" else ""),
            "verification_steps": item_translation.verification_steps if item_translation else (item.verification_steps if locale == "en" else ""),
            "translation_status": "available" if locale == "en" or item_translation else "missing",
        })
    return {
        "id": row.id, "course_id": row.course_id, "title": fields["title"], "slug": row.slug,
        "category": row.category, "reference_type": row.reference_type, "difficulty": row.difficulty,
        "description": fields["description"], "basic_syntax": row.basic_syntax, "when_to_use": row.when_to_use,
        "important_notes": row.important_notes, "purpose": fields["purpose"], "syntax_format": fields["syntax_format"],
        "parameters": fields["parameters"], "return_value": fields["return_value"],
        "version_compatibility": fields["version_compatibility"], "input_output": fields["input_output"],
        "common_mistakes": fields["common_mistakes"], "best_practices": fields["best_practices"],
        "practice_exercises": fields["practice_exercises"], "further_reading": fields["further_reading"],
        "minimum_examples": row.minimum_examples, "status": row.status, "display_order": row.display_order,
        "requested_locale": locale, "resolved_locale": locale if locale == "en" or translation else "en",
        "translation_status": translation_status, "examples": examples,
    }


def is_complete(row: SyntaxReference) -> bool:
    required = max(1, min(5, row.minimum_examples or 5))
    examples = sorted(row.examples, key=lambda item: item.example_number)
    if len(examples) < required or [item.example_number for item in examples[:required]] != list(range(1, required + 1)):
        return False
    return all(item.code.strip() and item.explanation.strip() and item.expected_output.strip() for item in examples[:required])


def content_ready(row: SyntaxReference) -> bool:
    return bool(row.title.strip() and row.description.strip() and row.basic_syntax.strip() and row.when_to_use.strip() and row.important_notes.strip() and is_complete(row))


def public_course(course_slug: str, db: Session) -> Course:
    course = db.scalar(select(Course).where(Course.slug == course_slug, Course.published.is_(True)))
    if not course:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Published course not found")
    return course


def _reference_query(where):
    return select(SyntaxReference).options(selectinload(SyntaxReference.examples).selectinload(SyntaxReferenceExample.translations), selectinload(SyntaxReference.translations)).where(*where)


def public_reference(course_slug: str, reference_slug: str, db: Session) -> SyntaxReference:
    course = public_course(course_slug, db)
    row = db.scalar(_reference_query([SyntaxReference.course_id == course.id, SyntaxReference.slug == reference_slug, SyntaxReference.status == "published"]))
    if not row or not is_complete(row):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Published syntax reference not found")
    return row


@router.get("/api/v1/courses/{course_slug}/syntax-references", response_model=list[SyntaxReferenceOut])
@router.get("/api/v1/courses/{course_slug}/syntax", response_model=list[SyntaxReferenceOut])
def list_public_references(course_slug: str, category: str | None = None, difficulty: str | None = None, reference_type: str | None = None, search: str | None = None, locale: Literal["en", "my"] = "en", db: Session = Depends(get_db)):
    course = public_course(course_slug, db)
    rows = db.scalars(_reference_query([SyntaxReference.course_id == course.id, SyntaxReference.status == "published"]).order_by(SyntaxReference.display_order, SyntaxReference.title)).all()
    rows = [row for row in rows if is_complete(row)]
    if category: rows = [row for row in rows if row.category.casefold() == category.casefold()]
    if difficulty: rows = [row for row in rows if row.difficulty.casefold() == difficulty.casefold()]
    if reference_type: rows = [row for row in rows if row.reference_type.casefold() == reference_type.casefold()]
    if search:
        term = search.casefold().strip()
        rows = [row for row in rows if term in row.title.casefold() or term in row.description.casefold() or term in row.category.casefold()]
    return [serialize(row, locale) for row in rows]


@router.get("/api/v1/courses/{course_slug}/syntax-references/{reference_slug}", response_model=SyntaxReferenceOut)
@router.get("/api/v1/courses/{course_slug}/syntax/{reference_slug}", response_model=SyntaxReferenceOut)
def get_public_reference(course_slug: str, reference_slug: str, locale: Literal["en", "my"] = "en", db: Session = Depends(get_db)):
    return serialize(public_reference(course_slug, reference_slug, db), locale)


@router.get("/api/v1/courses/{course_slug}/lessons/{lesson_slug}/syntax-references", response_model=list[SyntaxReferenceOut])
def lesson_references(course_slug: str, lesson_slug: str, locale: Literal["en", "my"] = "en", db: Session = Depends(get_db)):
    course = public_course(course_slug, db)
    lesson = db.scalar(select(Lesson).join(CourseModule).where(CourseModule.course_id == course.id, Lesson.slug == lesson_slug, Lesson.published.is_(True)))
    if not lesson: raise HTTPException(status.HTTP_404_NOT_FOUND, "Published lesson not found")
    rows = db.scalars(select(SyntaxReference).join(LessonSyntaxReference, LessonSyntaxReference.reference_id == SyntaxReference.id).options(selectinload(SyntaxReference.examples).selectinload(SyntaxReferenceExample.translations), selectinload(SyntaxReference.translations)).where(LessonSyntaxReference.lesson_id == lesson.id, SyntaxReference.status == "published").order_by(LessonSyntaxReference.position)).all()
    return [serialize(row, locale) for row in rows if is_complete(row)]


def admin_reference(reference_id: UUID, db: Session) -> SyntaxReference:
    row = db.scalar(select(SyntaxReference).options(selectinload(SyntaxReference.examples).selectinload(SyntaxReferenceExample.translations), selectinload(SyntaxReference.translations), selectinload(SyntaxReference.versions)).where(SyntaxReference.id == reference_id))
    if not row: raise HTTPException(status.HTTP_404_NOT_FOUND, "Syntax reference not found")
    return row


def _snapshot(row: SyntaxReference) -> str:
    return json.dumps({"id": str(row.id), "course_id": str(row.course_id), "title": row.title, "slug": row.slug, "category": row.category, "reference_type": row.reference_type, "difficulty": row.difficulty, "description": row.description, "basic_syntax": row.basic_syntax, "when_to_use": row.when_to_use, "important_notes": row.important_notes, "purpose": row.purpose, "syntax_format": row.syntax_format, "parameters": row.parameters, "return_value": row.return_value, "version_compatibility": row.version_compatibility, "input_output": row.input_output, "common_mistakes": row.common_mistakes, "best_practices": row.best_practices, "practice_exercises": row.practice_exercises, "further_reading": row.further_reading, "minimum_examples": row.minimum_examples, "status": row.status, "examples": [{"number": item.example_number, "title": item.title, "language": item.language, "code": item.code, "expected_output": item.expected_output} for item in row.examples]}, ensure_ascii=False)


def _record_version(row: SyntaxReference, user: User, db: Session) -> None:
    current = db.scalar(select(func.max(SyntaxReferenceVersion.version)).where(SyntaxReferenceVersion.reference_id == row.id)) or 0
    db.add(SyntaxReferenceVersion(reference_id=row.id, version=current + 1, status=row.status, snapshot_json=_snapshot(row), created_by=user.id))


def replace_examples(row: SyntaxReference, payload: SyntaxReferenceIn, db: Session) -> None:
    row.examples.clear()
    db.flush()
    for item in sorted(payload.examples, key=lambda value: value.example_number):
        db.add(SyntaxReferenceExample(reference_id=row.id, **item.model_dump()))


def replace_translations(row: SyntaxReference, payload: SyntaxReferenceIn, db: Session) -> None:
    for item in payload.translations:
        translation = next((value for value in row.translations if value.locale == item.locale), None)
        if not translation:
            translation = SyntaxReferenceTranslation(reference_id=row.id, locale=item.locale)
            db.add(translation)
        for key, value in item.model_dump(exclude={"locale"}).items(): setattr(translation, key, value)


def _save_row(row: SyntaxReference, payload: SyntaxReferenceIn, user: User, db: Session) -> SyntaxReference:
    for key, value in payload.model_dump(exclude={"examples", "translations"}).items(): setattr(row, key, value)
    row.updated_by = user.id
    replace_examples(row, payload, db)
    replace_translations(row, payload, db)
    db.flush()
    _record_version(row, user, db)
    db.add(AdminAuditLog(actor_id=user.id, action="syntax_reference_updated", entity_type="syntax_reference", entity_id=row.id))
    return row


@router.get("/api/v1/admin/syntax-references")
def list_all_admin_references(course_id: UUID | None = None, category: str | None = None, difficulty: str | None = None, publication: str | None = Query(default=None, alias="status"), search: str | None = None, page: int = Query(default=1, ge=1), page_size: int = Query(default=25, ge=1, le=100), user: User = Depends(require_platform_admin), db: Session = Depends(get_db)):
    query = select(SyntaxReference).options(selectinload(SyntaxReference.examples), selectinload(SyntaxReference.translations)).order_by(SyntaxReference.updated_at.desc(), SyntaxReference.title)
    if course_id: query = query.where(SyntaxReference.course_id == course_id)
    if category: query = query.where(SyntaxReference.category.ilike(category))
    if difficulty: query = query.where(SyntaxReference.difficulty == difficulty)
    if publication in REVIEW_STATES: query = query.where(SyntaxReference.status == publication)
    if search: query = query.where(or_(SyntaxReference.title.ilike(f"%{search.strip()}%"), SyntaxReference.slug.ilike(f"%{search.strip()}%"), SyntaxReference.description.ilike(f"%{search.strip()}%")))
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.scalars(query.offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [serialize(row) for row in rows], "page": page, "page_size": page_size, "total": total, "pages": max(1, (total + page_size - 1) // page_size)}


@router.get("/api/v1/admin/courses/{course_id}/syntax-references", response_model=list[SyntaxReferenceOut])
def list_admin_references(course_id: UUID, user: User = Depends(require_platform_admin), db: Session = Depends(get_db)):
    if not db.get(Course, course_id): raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found")
    rows = db.scalars(select(SyntaxReference).options(selectinload(SyntaxReference.examples), selectinload(SyntaxReference.translations)).where(SyntaxReference.course_id == course_id).order_by(SyntaxReference.display_order, SyntaxReference.title)).all()
    return [serialize(row) for row in rows]


@router.post("/api/v1/admin/courses/{course_id}/syntax-references", response_model=SyntaxReferenceOut, status_code=201)
def create_reference(course_id: UUID, payload: SyntaxReferenceIn, user: User = Depends(require_platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if not db.get(Course, course_id): raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found")
    if db.scalar(select(SyntaxReference).where(SyntaxReference.course_id == course_id, SyntaxReference.slug == payload.slug)): raise HTTPException(status.HTTP_409_CONFLICT, "Syntax reference slug already exists for this course")
    row = SyntaxReference(course_id=course_id, created_by=user.id, updated_by=user.id, **payload.model_dump(exclude={"examples", "translations"}))
    db.add(row); db.flush(); replace_examples(row, payload, db); replace_translations(row, payload, db); db.flush(); _record_version(row, user, db)
    db.add(AdminAuditLog(actor_id=user.id, action="syntax_reference_created", entity_type="syntax_reference", entity_id=row.id)); db.commit()
    return serialize(admin_reference(row.id, db))


@router.get("/api/v1/admin/syntax-references/{reference_id}", response_model=SyntaxReferenceOut)
def get_admin_reference(reference_id: UUID, user: User = Depends(require_platform_admin), db: Session = Depends(get_db)):
    return serialize(admin_reference(reference_id, db))


@router.patch("/api/v1/admin/syntax-references/{reference_id}", response_model=SyntaxReferenceOut)
def update_reference(reference_id: UUID, payload: SyntaxReferenceIn, user: User = Depends(require_platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = admin_reference(reference_id, db)
    duplicate = db.scalar(select(SyntaxReference).where(SyntaxReference.course_id == row.course_id, SyntaxReference.slug == payload.slug, SyntaxReference.id != row.id))
    if duplicate: raise HTTPException(status.HTTP_409_CONFLICT, "Syntax reference slug already exists for this course")
    _save_row(row, payload, user, db); db.commit()
    return serialize(admin_reference(row.id, db))


@router.post("/api/v1/admin/syntax-references/{reference_id}/submit-review", response_model=SyntaxReferenceOut)
def submit_review(reference_id: UUID, user: User = Depends(require_platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = admin_reference(reference_id, db)
    if not content_ready(row): raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Complete the required content and examples before review")
    row.status = "in_review"; _record_version(row, user, db); db.add(AdminAuditLog(actor_id=user.id, action="syntax_reference_submitted", entity_type="syntax_reference", entity_id=row.id)); db.commit()
    return serialize(admin_reference(row.id, db))


@router.post("/api/v1/admin/syntax-references/{reference_id}/request-changes", response_model=SyntaxReferenceOut)
def request_changes(reference_id: UUID, note: str = Query(default="", max_length=2000), user: User = Depends(require_platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = admin_reference(reference_id, db); row.status = "changes_requested"; row.review_notes = note.strip(); row.reviewed_at = datetime.now(timezone.utc); _record_version(row, user, db); db.add(AdminAuditLog(actor_id=user.id, action="syntax_reference_changes_requested", entity_type="syntax_reference", entity_id=row.id)); db.commit()
    return serialize(admin_reference(row.id, db))


@router.post("/api/v1/admin/syntax-references/{reference_id}/approve", response_model=SyntaxReferenceOut)
def approve_reference(reference_id: UUID, user: User = Depends(require_platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = admin_reference(reference_id, db)
    if row.status not in {"in_review", "changes_requested"} or not content_ready(row): raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Only complete entries in review can be approved")
    row.status = "approved"; row.approved_by = user.id; row.reviewed_at = datetime.now(timezone.utc); _record_version(row, user, db); db.add(AdminAuditLog(actor_id=user.id, action="syntax_reference_approved", entity_type="syntax_reference", entity_id=row.id)); db.commit()
    return serialize(admin_reference(row.id, db))


@router.post("/api/v1/admin/syntax-references/{reference_id}/publish", response_model=SyntaxReferenceOut)
def publish_reference(reference_id: UUID, user: User = Depends(require_platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = admin_reference(reference_id, db)
    if row.status not in {"approved", "published"} or not content_ready(row): raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Publishing requires an approved complete entry")
    row.status = "published"; row.published_at = datetime.now(timezone.utc); _record_version(row, user, db); db.add(AdminAuditLog(actor_id=user.id, action="syntax_reference_published", entity_type="syntax_reference", entity_id=row.id)); db.commit()
    return serialize(admin_reference(row.id, db))


@router.post("/api/v1/admin/syntax-references/{reference_id}/unpublish", response_model=SyntaxReferenceOut)
def unpublish_reference(reference_id: UUID, user: User = Depends(require_platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = admin_reference(reference_id, db); row.status = "draft"; row.published_at = None; _record_version(row, user, db); db.add(AdminAuditLog(actor_id=user.id, action="syntax_reference_unpublished", entity_type="syntax_reference", entity_id=row.id)); db.commit()
    return serialize(admin_reference(row.id, db))


@router.delete("/api/v1/admin/syntax-references/{reference_id}", response_model=SyntaxReferenceOut)
def archive_reference(reference_id: UUID, user: User = Depends(require_platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = admin_reference(reference_id, db); row.status = "archived"; _record_version(row, user, db); db.add(AdminAuditLog(actor_id=user.id, action="syntax_reference_archived", entity_type="syntax_reference", entity_id=row.id)); db.commit()
    return serialize(admin_reference(row.id, db))


@router.get("/api/v1/admin/syntax-references/{reference_id}/versions")
def syntax_versions(reference_id: UUID, user: User = Depends(require_platform_admin), db: Session = Depends(get_db)):
    row = admin_reference(reference_id, db)
    return {"items": [{"id": version.id, "version": version.version, "status": version.status, "snapshot": json.loads(version.snapshot_json), "created_at": version.created_at} for version in row.versions]}


@router.put("/api/v1/admin/lessons/{lesson_id}/syntax-references")
def set_lesson_references(lesson_id: UUID, payload: LessonSyntaxReferencesIn, user: User = Depends(require_platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    lesson = db.scalar(select(Lesson).join(CourseModule).where(Lesson.id == lesson_id))
    if not lesson: raise HTTPException(status.HTTP_404_NOT_FOUND, "Lesson not found")
    course_id = db.get(CourseModule, lesson.module_id).course_id
    refs = db.scalars(select(SyntaxReference).where(SyntaxReference.id.in_(payload.reference_ids), SyntaxReference.course_id == course_id)).all() if payload.reference_ids else []
    if len(refs) != len(set(payload.reference_ids)): raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Lesson references must belong to the same course")
    db.query(LessonSyntaxReference).filter(LessonSyntaxReference.lesson_id == lesson_id).delete(synchronize_session=False)
    for position, reference_id in enumerate(payload.reference_ids): db.add(LessonSyntaxReference(lesson_id=lesson_id, reference_id=reference_id, position=position))
    db.add(AdminAuditLog(actor_id=user.id, action="lesson_syntax_references_updated", entity_type="lesson", entity_id=lesson_id)); db.commit()
    return {"lesson_id": lesson_id, "reference_ids": payload.reference_ids}
