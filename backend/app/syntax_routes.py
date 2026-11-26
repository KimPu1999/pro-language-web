"""Course-scoped syntax reference APIs.

Syntax references are deliberately separate from lesson code examples. A
published reference is public only when its course is published and it has
exactly five ordered examples numbered one through five.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .auth import require_csrf
from .db import get_db
from .models import AdminAuditLog, Course, CourseModule, Lesson, LessonSyntaxReference, SyntaxReference, SyntaxReferenceExample, User
from .rbac import require_platform_admin
from .schemas import LessonSyntaxReferencesIn, SyntaxReferenceIn, SyntaxReferenceOut

router = APIRouter(tags=["syntax-references"])


def serialize(row: SyntaxReference) -> dict:
    return {
        "id": row.id,
        "course_id": row.course_id,
        "title": row.title,
        "slug": row.slug,
        "category": row.category,
        "description": row.description,
        "basic_syntax": row.basic_syntax,
        "when_to_use": row.when_to_use,
        "important_notes": row.important_notes,
        "status": row.status,
        "display_order": row.display_order,
        "examples": [{
            "id": item.id,
            "example_number": item.example_number,
            "title": item.title,
            "code": item.code,
            "language": item.language,
            "expected_output": item.expected_output,
            "explanation": item.explanation,
        } for item in row.examples],
    }


def is_complete(row: SyntaxReference) -> bool:
    return len(row.examples) == 5 and {item.example_number for item in row.examples} == {1, 2, 3, 4, 5}


def public_course(course_slug: str, db: Session) -> Course:
    course = db.scalar(select(Course).where(Course.slug == course_slug, Course.published.is_(True)))
    if not course:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Published course not found")
    return course


def public_reference(course_slug: str, reference_slug: str, db: Session) -> SyntaxReference:
    course = public_course(course_slug, db)
    row = db.scalar(select(SyntaxReference).options(selectinload(SyntaxReference.examples)).where(
        SyntaxReference.course_id == course.id,
        SyntaxReference.slug == reference_slug,
        SyntaxReference.status == "published",
    ))
    if not row or not is_complete(row):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Published syntax reference not found")
    return row


@router.get("/api/v1/courses/{course_slug}/syntax-references", response_model=list[SyntaxReferenceOut])
def list_public_references(course_slug: str, category: str | None = None, search: str | None = None, db: Session = Depends(get_db)):
    course = public_course(course_slug, db)
    query = select(SyntaxReference).options(selectinload(SyntaxReference.examples)).where(SyntaxReference.course_id == course.id, SyntaxReference.status == "published").order_by(SyntaxReference.display_order, SyntaxReference.title)
    rows = db.scalars(query).all()
    rows = [row for row in rows if is_complete(row)]
    if category:
        rows = [row for row in rows if row.category.casefold() == category.casefold()]
    if search:
        term = search.strip().casefold()
        rows = [row for row in rows if term in row.title.casefold() or term in row.description.casefold() or term in row.category.casefold()]
    return [serialize(row) for row in rows]


@router.get("/api/v1/courses/{course_slug}/syntax-references/{reference_slug}", response_model=SyntaxReferenceOut)
def get_public_reference(course_slug: str, reference_slug: str, db: Session = Depends(get_db)):
    return serialize(public_reference(course_slug, reference_slug, db))


@router.get("/api/v1/courses/{course_slug}/lessons/{lesson_slug}/syntax-references", response_model=list[SyntaxReferenceOut])
def lesson_references(course_slug: str, lesson_slug: str, db: Session = Depends(get_db)):
    course = public_course(course_slug, db)
    lesson = db.scalar(select(Lesson).join(CourseModule).where(CourseModule.course_id == course.id, Lesson.slug == lesson_slug, Lesson.published.is_(True)))
    if not lesson:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Published lesson not found")
    rows = db.scalars(select(SyntaxReference).join(LessonSyntaxReference, LessonSyntaxReference.reference_id == SyntaxReference.id).options(selectinload(SyntaxReference.examples)).where(LessonSyntaxReference.lesson_id == lesson.id, SyntaxReference.status == "published").order_by(LessonSyntaxReference.position)).all()
    return [serialize(row) for row in rows if is_complete(row)]


def admin_reference(reference_id: UUID, user: User, db: Session) -> SyntaxReference:
    if user.role not in {"platform_admin", "admin", "super_admin"} or not user.email_verified_at:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Administrator access required")
    row = db.scalar(select(SyntaxReference).options(selectinload(SyntaxReference.examples)).where(SyntaxReference.id == reference_id))
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Syntax reference not found")
    return row


def replace_examples(row: SyntaxReference, payload: SyntaxReferenceIn, db: Session) -> None:
    row.examples.clear()
    db.flush()
    for item in sorted(payload.examples, key=lambda value: value.example_number):
        row.examples.append(SyntaxReferenceExample(**item.model_dump()))


@router.get("/api/v1/admin/courses/{course_id}/syntax-references", response_model=list[SyntaxReferenceOut])
def list_admin_references(course_id: UUID, user: User = Depends(require_platform_admin), db: Session = Depends(get_db)):
    if not db.get(Course, course_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found")
    rows = db.scalars(select(SyntaxReference).options(selectinload(SyntaxReference.examples)).where(SyntaxReference.course_id == course_id).order_by(SyntaxReference.display_order, SyntaxReference.title)).all()
    return [serialize(row) for row in rows]


@router.post("/api/v1/admin/courses/{course_id}/syntax-references", response_model=SyntaxReferenceOut, status_code=201)
def create_reference(course_id: UUID, payload: SyntaxReferenceIn, user: User = Depends(require_platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if not db.get(Course, course_id):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Course not found")
    if db.scalar(select(SyntaxReference).where(SyntaxReference.course_id == course_id, SyntaxReference.slug == payload.slug)):
        raise HTTPException(status.HTTP_409_CONFLICT, "Syntax reference slug already exists for this course")
    row = SyntaxReference(course_id=course_id, **payload.model_dump(exclude={"examples"}))
    db.add(row)
    db.flush()
    replace_examples(row, payload, db)
    db.add(AdminAuditLog(actor_id=user.id, action="syntax_reference_created", entity_type="syntax_reference", entity_id=row.id))
    db.commit()
    db.refresh(row)
    return serialize(row)


@router.get("/api/v1/admin/syntax-references/{reference_id}", response_model=SyntaxReferenceOut)
def get_admin_reference(reference_id: UUID, user: User = Depends(require_platform_admin), db: Session = Depends(get_db)):
    return serialize(admin_reference(reference_id, user, db))


@router.patch("/api/v1/admin/syntax-references/{reference_id}", response_model=SyntaxReferenceOut)
def update_reference(reference_id: UUID, payload: SyntaxReferenceIn, user: User = Depends(require_platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = admin_reference(reference_id, user, db)
    duplicate = db.scalar(select(SyntaxReference).where(SyntaxReference.course_id == row.course_id, SyntaxReference.slug == payload.slug, SyntaxReference.id != row.id))
    if duplicate:
        raise HTTPException(status.HTTP_409_CONFLICT, "Syntax reference slug already exists for this course")
    for key, value in payload.model_dump(exclude={"examples"}).items():
        setattr(row, key, value)
    replace_examples(row, payload, db)
    db.add(AdminAuditLog(actor_id=user.id, action="syntax_reference_updated", entity_type="syntax_reference", entity_id=row.id))
    db.commit()
    db.refresh(row)
    return serialize(row)


@router.post("/api/v1/admin/syntax-references/{reference_id}/publish", response_model=SyntaxReferenceOut)
def publish_reference(reference_id: UUID, user: User = Depends(require_platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = admin_reference(reference_id, user, db)
    if not is_complete(row):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Publishing requires exactly five examples numbered 1 through 5")
    row.status = "published"
    db.add(AdminAuditLog(actor_id=user.id, action="syntax_reference_published", entity_type="syntax_reference", entity_id=row.id))
    db.commit()
    db.refresh(row)
    return serialize(row)


@router.post("/api/v1/admin/syntax-references/{reference_id}/unpublish", response_model=SyntaxReferenceOut)
def unpublish_reference(reference_id: UUID, user: User = Depends(require_platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = admin_reference(reference_id, user, db)
    row.status = "draft"
    db.add(AdminAuditLog(actor_id=user.id, action="syntax_reference_unpublished", entity_type="syntax_reference", entity_id=row.id))
    db.commit()
    db.refresh(row)
    return serialize(row)


@router.delete("/api/v1/admin/syntax-references/{reference_id}", response_model=SyntaxReferenceOut)
def archive_reference(reference_id: UUID, user: User = Depends(require_platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = admin_reference(reference_id, user, db)
    row.status = "archived"
    db.add(AdminAuditLog(actor_id=user.id, action="syntax_reference_archived", entity_type="syntax_reference", entity_id=row.id))
    db.commit()
    db.refresh(row)
    return serialize(row)


@router.put("/api/v1/admin/lessons/{lesson_id}/syntax-references")
def set_lesson_references(lesson_id: UUID, payload: LessonSyntaxReferencesIn, user: User = Depends(require_platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    lesson = db.scalar(select(Lesson).join(CourseModule).where(Lesson.id == lesson_id))
    if not lesson:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Lesson not found")
    course = db.get(CourseModule, lesson.module_id).course_id
    refs = db.scalars(select(SyntaxReference).where(SyntaxReference.id.in_(payload.reference_ids), SyntaxReference.course_id == course)).all() if payload.reference_ids else []
    if len(refs) != len(set(payload.reference_ids)):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Lesson references must belong to the same course")
    db.query(LessonSyntaxReference).filter(LessonSyntaxReference.lesson_id == lesson_id).delete(synchronize_session=False)
    for position, reference_id in enumerate(payload.reference_ids):
        db.add(LessonSyntaxReference(lesson_id=lesson_id, reference_id=reference_id, position=position))
    db.add(AdminAuditLog(actor_id=user.id, action="lesson_syntax_references_updated", entity_type="lesson", entity_id=lesson_id))
    db.commit()
    return {"lesson_id": lesson_id, "reference_ids": payload.reference_ids}
