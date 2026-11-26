"""Platform-scoped content review queue and approval workflow."""
import json
from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from .auth import require_csrf, now
from .db import get_db
from .models import (
    CareerRoadmap,
    Challenge,
    ContentReviewComment,
    ContentReviewEvent,
    ContentReviewItem,
    Course,
    CourseModule,
    Lesson,
    LegalDocumentVersion,
    Organization,
    PlatformSetting,
    ProjectTemplate,
    SyntaxReference,
    User,
)
from .rbac import require_platform_admin

router = APIRouter(prefix="/api/v1/platform/content-review", tags=["content-review"])
PLATFORM_REVIEWERS = {"admin", "platform_admin", "super_admin", "content_editor", "instructor"}
CONTENT_TYPES = {"course", "module", "lesson", "syntax_reference", "challenge", "project", "career_path", "public_page", "legal_page"}
ACTIVE_STATUSES = {"submitted", "in_review"}
TRANSITIONS = {
    "submitted": {"in_review"},
    "in_review": {"approved", "changes_requested", "rejected"},
    "changes_requested": {"submitted"},
    "rejected": {"submitted"},
}


class ReviewSubmitIn(BaseModel):
    content_type: str = Field(pattern=r"^(course|module|lesson|syntax_reference|challenge|project|career_path|public_page|legal_page)$")
    content_key: str = Field(min_length=1, max_length=180)
    organization_id: UUID | None = None


class ReviewerAssignmentIn(BaseModel):
    reviewer_id: UUID


class ReviewTransitionIn(BaseModel):
    status: str = Field(pattern=r"^(in_review|approved|changes_requested|rejected|submitted)$")
    comment: str = Field(default="", max_length=4000)


class ReviewCommentIn(BaseModel):
    comment_type: str = Field(default="general", pattern=r"^(general|correction|code_quality|accuracy|accessibility)$")
    body: str = Field(min_length=1, max_length=4000)


def parse_json(value: str | None, default):
    try:
        return json.loads(value or "")
    except (TypeError, ValueError, json.JSONDecodeError):
        return default


def ensure_content_type(content_type: str) -> None:
    if content_type not in CONTENT_TYPES:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Unsupported content type")


def content_record(db: Session, content_type: str, content_key: str):
    ensure_content_type(content_type)
    if content_type == "public_page":
        return db.scalar(select(PlatformSetting).where(PlatformSetting.key == f"page:{content_key}"))
    if content_type == "legal_page":
        try:
            return db.get(LegalDocumentVersion, UUID(content_key))
        except ValueError:
            return None
    model = {
        "course": Course,
        "module": CourseModule,
        "lesson": Lesson,
        "syntax_reference": SyntaxReference,
        "challenge": Challenge,
        "project": ProjectTemplate,
        "career_path": CareerRoadmap,
    }[content_type]
    try:
        return db.get(model, UUID(content_key))
    except ValueError:
        return None


def content_title(db: Session, content_type: str, record) -> str:
    if content_type == "public_page":
        return parse_json(record.value_json if record else "", {}).get("title", record.key.removeprefix("page:") if record else "Public page")
    if content_type == "legal_page":
        return record.title if record else "Legal page"
    return getattr(record, "title", None) or getattr(record, "name", None) or getattr(record, "slug", None) or content_type.replace("_", " ").title()


def author_id(record, user: User) -> UUID:
    return getattr(record, "created_by", None) or getattr(record, "submitted_by", None) or user.id


def preview_content(db: Session, content_type: str, record) -> dict:
    if content_type == "course":
        return {"title": record.title, "description": record.description, "short_description": record.short_description, "status": record.status, "published": record.published, "thumbnail": record.thumbnail, "modules": [{"id": module.id, "title": module.title, "lessons": [{"id": lesson.id, "title": lesson.title, "status": lesson.status} for lesson in module.lessons]} for module in db.scalars(select(CourseModule).where(CourseModule.course_id == record.id).order_by(CourseModule.order_index)).all()]}
    if content_type == "module":
        lessons = db.scalars(select(Lesson).where(Lesson.module_id == record.id).order_by(Lesson.order_index)).all()
        return {"title": record.title, "course_id": record.course_id, "lessons": [{"id": lesson.id, "title": lesson.title, "content": lesson.content_en, "status": lesson.status} for lesson in lessons]}
    if content_type == "lesson":
        examples = [{"title": item.title, "language": item.language, "code": item.code, "description": item.description} for item in record.code_examples]
        return {"title": record.title, "description": record.description, "content_en": record.content_en, "content_mm": record.content_mm, "status": record.status, "code_examples": examples}
    if content_type == "syntax_reference":
        return {"title": record.title, "category": record.category, "description": record.description, "basic_syntax": record.basic_syntax, "when_to_use": record.when_to_use, "important_notes": record.important_notes, "status": record.status, "examples": [{"number": item.example_number, "title": item.title, "language": item.language, "code": item.code, "expected_output": item.expected_output, "explanation": item.explanation} for item in record.examples]}
    if content_type == "challenge":
        return {"title": record.title, "description": record.description_en, "difficulty": record.difficulty, "status": record.status, "published": record.published, "examples": parse_json(record.examples_json, []), "constraints": parse_json(record.constraints_json, []), "input_format": record.input_format, "output_format": record.output_format, "explanation": record.explanation_en}
    if content_type == "project":
        return {"title": record.title, "description": record.description_en, "difficulty": record.difficulty, "status": record.status, "published": record.published, "technology_stack": record.technology_stack, "requirements": record.requirements, "learning_outcomes": record.learning_outcomes, "cover_image": record.cover_image}
    if content_type == "career_path":
        return {"title": record.title, "description": record.description_en, "career_category": record.career_category, "status": record.status, "published": record.published, "estimated_hours": record.estimated_hours, "cover_image": record.cover_image}
    if content_type == "legal_page":
        return {"title": record.title, "document_type": record.document_id, "version": record.version, "content": record.content, "review_status": record.review_status, "publication_status": record.publication_status}
    return {"title": content_title(db, content_type, record), "value": parse_json(record.value_json if record else "", {})}


def user_summary(db: Session, user_id: UUID | None) -> dict | None:
    user = db.get(User, user_id) if user_id else None
    return {"id": user.id, "name": user.display_name, "email": user.email, "role": user.role} if user else None


def organization_summary(db: Session, organization_id: UUID | None) -> dict | None:
    organization = db.get(Organization, organization_id) if organization_id else None
    return {"id": organization.id, "name": organization.name, "slug": organization.slug} if organization else None


def item_summary(db: Session, row: ContentReviewItem) -> dict:
    return {"id": row.id, "content_type": row.content_type, "content_key": row.content_key, "title": row.title, "organization_id": row.organization_id, "organization": organization_summary(db, row.organization_id), "version": row.version, "status": row.status, "submitted_by": user_summary(db, row.submitted_by), "reviewer": user_summary(db, row.reviewer_id), "submitted_at": row.submitted_at, "reviewed_at": row.reviewed_at, "published_at": row.published_at, "updated_at": row.updated_at}


def get_item(db: Session, review_id: UUID, lock: bool = False) -> ContentReviewItem:
    query = select(ContentReviewItem).where(ContentReviewItem.id == review_id)
    if lock:
        query = query.with_for_update()
    row = db.scalar(query)
    if not row:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Review item not found")
    return row


def add_event(db: Session, row: ContentReviewItem, actor: User, to_status: str, comment: str = "", from_status: str | None = None) -> None:
    db.add(ContentReviewEvent(review_item_id=row.id, actor_id=actor.id, from_status=from_status, to_status=to_status, comment=comment.strip()))


@router.get("/dashboard")
def dashboard(user: User = Depends(require_platform_admin), db: Session = Depends(get_db)):
    counts = {key: db.scalar(select(func.count()).select_from(ContentReviewItem).where(ContentReviewItem.status == key)) or 0 for key in ("submitted", "in_review", "approved", "changes_requested", "rejected")}
    return {"pending_review": counts["submitted"], "in_review": counts["in_review"], "approved": counts["approved"], "changes_requested": counts["changes_requested"], "rejected": counts["rejected"], "total": sum(counts.values()), "data_source": "content_review_items"}


@router.get("/reviewers")
def reviewers(user: User = Depends(require_platform_admin), db: Session = Depends(get_db)):
    rows = db.scalars(select(User).where(User.role.in_(PLATFORM_REVIEWERS), User.account_status == "active", User.email_verified_at.is_not(None)).order_by(User.display_name, User.email)).all()
    return [{"id": row.id, "name": row.display_name, "email": row.email, "role": row.role} for row in rows]


@router.get("/authors")
def authors(user: User = Depends(require_platform_admin), db: Session = Depends(get_db)):
    author_ids = [value for (value,) in db.execute(select(ContentReviewItem.submitted_by).where(ContentReviewItem.submitted_by.is_not(None)).distinct()).all()]
    if not author_ids:
        return []
    rows = db.scalars(select(User).where(User.id.in_(author_ids)).order_by(User.display_name, User.email)).all()
    return [{"id": row.id, "name": row.display_name, "email": row.email, "role": row.role} for row in rows]


@router.get("/queue")
def queue(
    status_filter: str | None = Query(default=None, alias="status", pattern=r"^(submitted|in_review|approved|changes_requested|rejected|published)$"),
    content_type: str | None = Query(default=None, pattern=r"^(course|module|lesson|syntax_reference|challenge|project|career_path|public_page|legal_page)$"),
    author_id: UUID | None = None,
    reviewer_id: UUID | None = None,
    organization_id: UUID | None = None,
    mine: bool = False,
    needs_attention: bool = False,
    search: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    sort: str = Query(default="submitted_at", pattern=r"^(submitted_at|updated_at|title|status)$"),
    order: str = Query(default="desc", pattern=r"^(asc|desc)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=25, ge=1, le=100),
    user: User = Depends(require_platform_admin),
    db: Session = Depends(get_db),
):
    query = select(ContentReviewItem)
    if status_filter: query = query.where(ContentReviewItem.status == status_filter)
    if content_type: query = query.where(ContentReviewItem.content_type == content_type)
    if author_id: query = query.where(ContentReviewItem.submitted_by == author_id)
    if reviewer_id: query = query.where(ContentReviewItem.reviewer_id == reviewer_id)
    if organization_id: query = query.where(ContentReviewItem.organization_id == organization_id)
    if mine: query = query.where(ContentReviewItem.reviewer_id == user.id)
    if needs_attention: query = query.where(ContentReviewItem.status.in_(("submitted", "changes_requested")))
    if date_from: query = query.where(ContentReviewItem.submitted_at >= date_from)
    if date_to: query = query.where(ContentReviewItem.submitted_at <= date_to)
    if search:
        query = query.where(ContentReviewItem.title.ilike(f"%{search.strip()}%"))
    sort_column = {"submitted_at": ContentReviewItem.submitted_at, "updated_at": ContentReviewItem.updated_at, "title": ContentReviewItem.title, "status": ContentReviewItem.status}[sort]
    query = query.order_by(sort_column.asc() if order == "asc" else sort_column.desc())
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    rows = db.scalars(query.offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [item_summary(db, row) for row in rows], "page": page, "page_size": page_size, "total": total, "pages": (total + page_size - 1) // page_size}


@router.post("/submit", status_code=201)
def submit(payload: ReviewSubmitIn, user: User = Depends(require_platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    record = content_record(db, payload.content_type, payload.content_key)
    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Content record not found")
    if payload.organization_id:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Platform review items are not organization-scoped")
    active = db.scalar(select(ContentReviewItem).where(ContentReviewItem.content_type == payload.content_type, ContentReviewItem.content_key == payload.content_key, ContentReviewItem.status.in_(ACTIVE_STATUSES)))
    if active:
        raise HTTPException(status.HTTP_409_CONFLICT, "This content already has an active review")
    latest = db.scalar(select(func.max(ContentReviewItem.version)).where(ContentReviewItem.content_type == payload.content_type, ContentReviewItem.content_key == payload.content_key)) or 0
    row = ContentReviewItem(content_type=payload.content_type, content_key=payload.content_key, organization_id=None, title=content_title(db, payload.content_type, record), submitted_by=author_id(record, user), version=latest + 1, status="submitted")
    db.add(row); db.flush(); add_event(db, row, user, "submitted", from_status=None)
    db.commit(); db.refresh(row)
    return item_summary(db, row)


@router.get("/{review_id}")
def detail(review_id: UUID, user: User = Depends(require_platform_admin), db: Session = Depends(get_db)):
    row = get_item(db, review_id)
    record = content_record(db, row.content_type, row.content_key)
    comments = db.scalars(select(ContentReviewComment).where(ContentReviewComment.review_item_id == row.id).order_by(ContentReviewComment.created_at.asc())).all()
    events = db.scalars(select(ContentReviewEvent).where(ContentReviewEvent.review_item_id == row.id).order_by(ContentReviewEvent.created_at.asc())).all()
    return {**item_summary(db, row), "preview": preview_content(db, row.content_type, record) if record else None, "comments": [{"id": item.id, "author": user_summary(db, item.author_id), "review_version": item.review_version, "comment_type": item.comment_type, "body": item.body, "created_at": item.created_at} for item in comments], "history": [{"id": item.id, "actor": user_summary(db, item.actor_id), "from_status": item.from_status, "to_status": item.to_status, "comment": item.comment, "created_at": item.created_at} for item in events]}


@router.patch("/{review_id}/assignment")
def assign(review_id: UUID, payload: ReviewerAssignmentIn, user: User = Depends(require_platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = get_item(db, review_id, lock=True)
    reviewer = db.scalar(select(User).where(User.id == payload.reviewer_id, User.role.in_(PLATFORM_REVIEWERS), User.account_status == "active", User.email_verified_at.is_not(None)))
    if not reviewer: raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Reviewer is not eligible")
    if row.submitted_by == reviewer.id: raise HTTPException(status.HTTP_409_CONFLICT, "Authors cannot review their own submission")
    row.reviewer_id = reviewer.id
    db.commit(); db.refresh(row)
    return item_summary(db, row)


@router.post("/{review_id}/transition")
def transition(review_id: UUID, payload: ReviewTransitionIn, user: User = Depends(require_platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = get_item(db, review_id, lock=True)
    if payload.status not in TRANSITIONS.get(row.status, set()):
        raise HTTPException(status.HTTP_409_CONFLICT, f"Cannot move review from {row.status} to {payload.status}")
    if payload.status in {"changes_requested", "rejected"} and not payload.comment.strip():
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "A comment is required for this decision")
    if row.submitted_by == user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Independent review is required")
    if row.reviewer_id and row.reviewer_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This review is assigned to another reviewer")
    row.reviewer_id = row.reviewer_id or user.id
    previous = row.status
    row.status = payload.status
    if payload.status in {"approved", "changes_requested", "rejected"}: row.reviewed_at = now()
    add_event(db, row, user, payload.status, payload.comment, from_status=previous)
    if payload.comment.strip(): db.add(ContentReviewComment(review_item_id=row.id, author_id=user.id, review_version=row.version, comment_type="decision", body=payload.comment.strip()))
    db.commit(); db.refresh(row)
    return {**item_summary(db, row), "previous_status": previous}


@router.post("/{review_id}/publish")
def publish(review_id: UUID, user: User = Depends(require_platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = get_item(db, review_id, lock=True)
    if row.status != "approved": raise HTTPException(status.HTTP_409_CONFLICT, "Only approved content can be published")
    record = content_record(db, row.content_type, row.content_key)
    if not record: raise HTTPException(status.HTTP_404_NOT_FOUND, "Content record not found")
    if row.content_type in {"course", "challenge", "project", "career_path"}:
        record.status = "published"; record.published = True
    elif row.content_type == "lesson":
        record.status = "published"; record.published = True
    elif row.content_type == "syntax_reference":
        record.status = "published"
    elif row.content_type == "public_page":
        data = parse_json(record.value_json, {}); data["status"] = "published"; record.value_json = json.dumps(data, sort_keys=True)
    elif row.content_type == "legal_page":
        record.review_status = "approved"; record.publication_status = "published"; record.published_by = user.id; record.published_at = now()
    else:
        raise HTTPException(status.HTTP_409_CONFLICT, "This content type has no independent publication state")
    previous = row.status; row.status = "published"; row.published_at = now(); add_event(db, row, user, "published", from_status=previous)
    db.commit(); db.refresh(row)
    return item_summary(db, row)


@router.post("/{review_id}/comments", status_code=201)
def comment(review_id: UUID, payload: ReviewCommentIn, user: User = Depends(require_platform_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = get_item(db, review_id)
    item = ContentReviewComment(review_item_id=row.id, author_id=user.id, review_version=row.version, comment_type=payload.comment_type, body=payload.body.strip())
    db.add(item); db.commit(); db.refresh(item)
    return {"id": item.id, "review_item_id": item.review_item_id, "author": user_summary(db, item.author_id), "review_version": item.review_version, "comment_type": item.comment_type, "body": item.body, "created_at": item.created_at}


@router.get("/{review_id}/history")
def history(review_id: UUID, user: User = Depends(require_platform_admin), db: Session = Depends(get_db)):
    row = get_item(db, review_id)
    events = db.scalars(select(ContentReviewEvent).where(ContentReviewEvent.review_item_id == row.id).order_by(ContentReviewEvent.created_at.asc())).all()
    comments = db.scalars(select(ContentReviewComment).where(ContentReviewComment.review_item_id == row.id).order_by(ContentReviewComment.created_at.asc())).all()
    return {"events": [{"id": item.id, "actor": user_summary(db, item.actor_id), "from_status": item.from_status, "to_status": item.to_status, "comment": item.comment, "created_at": item.created_at} for item in events], "comments": [{"id": item.id, "author": user_summary(db, item.author_id), "review_version": item.review_version, "comment_type": item.comment_type, "body": item.body, "created_at": item.created_at} for item in comments]}
