import json
import re
from datetime import datetime, timezone
from uuid import UUID, uuid4
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import and_, exists, func, or_, select
from sqlalchemy.orm import Session
from .admin_routes import full_admin
from .auth import current_user, require_csrf, check_rate_limit, require_role, verified_user
from .db import get_db
from .models import Course, CourseModule, Lesson, CommunityAnswer, CommunityBookmark, CommunityCategory, CommunityComment, CommunityModerationAction, CommunityNotification, CommunityPost, CommunityPostFollow, CommunityPostRevision, CommunityPostTag, CommunityReport, CommunitySnippet, CommunityTagFollow, CommunityVote, StudyGroup, StudyGroupMember, User, UserProfile
from .rbac import MODERATION_ROLES

router = APIRouter(prefix="/api/v1/community", tags=["community"])
POST_TYPES = {"question", "discussion", "tutorial", "project_showcase", "study_group"}
LANGUAGES = {"html", "css", "javascript", "typescript", "react", "next.js", "node.js", "c", "cpp", "java", "python", "php", "laravel", "sql", "mongodb", "json", "bash", "go", "rust"}
LOCALES = {"en", "my"}
REPORT_STATUSES = {"under_review", "resolved", "dismissed"}
MODERATION_ACTIONS = {"hide", "restore", "lock", "unlock", "remove_spam"}

def clean(value: str) -> str:
    return re.sub(r"(?is)<script[^>]*>.*?</script>|javascript:", "", value).strip()
def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

class PostIn(BaseModel):
    title: str = Field(min_length=3, max_length=220)
    body: str = Field(min_length=1, max_length=30000)
    post_type: str = "discussion"
    tags: list[str] = Field(default_factory=list, max_length=8)
    category_id: UUID | None = None
    language: str = "en"
    course_id: UUID | None = None
    module_id: UUID | None = None
    lesson_id: UUID | None = None
    expected_behavior: str = Field(default="", max_length=10000)
    actual_behavior: str = Field(default="", max_length=10000)
    code_language: str = Field(default="", max_length=50)
    code_snippet: str = Field(default="", max_length=50000)
    @field_validator("post_type")
    @classmethod
    def valid_type(cls, value: str) -> str:
        if value not in POST_TYPES: raise ValueError("Unsupported discussion type")
        return value
    @field_validator("language")
    @classmethod
    def valid_locale(cls, value: str) -> str:
        if value not in LOCALES: raise ValueError("Unsupported content language")
        return value
    @field_validator("code_language")
    @classmethod
    def normalized_code_language(cls, value: str) -> str:
        return value.lower().strip()
class AnswerIn(BaseModel): body: str = Field(min_length=1, max_length=30000)
class CommentIn(BaseModel): body: str = Field(min_length=1, max_length=10000); parent_id: UUID | None = None
class SnippetIn(BaseModel):
    title: str = Field(min_length=1, max_length=180); language: str = Field(min_length=1, max_length=50); source_code: str = Field(min_length=1, max_length=50000); description: str = Field(default="", max_length=10000)
    @field_validator("language")
    @classmethod
    def valid_language(cls, value: str) -> str:
        value = value.lower()
        if value not in LANGUAGES: raise ValueError("Unsupported language")
        return value
class GroupIn(BaseModel):
    name: str = Field(min_length=2, max_length=160); description: str = Field(min_length=1, max_length=10000); visibility: str = "public"
class CategoryIn(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    slug: str = Field(min_length=2, max_length=100)
    description: str = Field(default="", max_length=2000)
class ReportDecisionIn(BaseModel):
    status: str
    note: str = Field(default="", max_length=2000)
    action: str | None = None
    @field_validator("status")
    @classmethod
    def valid_status(cls, value: str) -> str:
        if value not in REPORT_STATUSES: raise ValueError("Unsupported report status")
        return value
    @field_validator("action")
    @classmethod
    def valid_action(cls, value: str | None) -> str | None:
        if value and value not in MODERATION_ACTIONS: raise ValueError("Unsupported moderation action")
        return value

def _unique_slug(title: str, user_id: UUID, db: Session, post_id: UUID | None = None) -> str:
    base = f"{slugify(title) or 'discussion'}-{str(user_id)[:8]}"
    query = select(CommunityPost.id).where(CommunityPost.slug == base)
    if post_id:
        query = query.where(CommunityPost.id != post_id)
    if not db.scalar(query):
        return base
    return f"{base}-{str(uuid4())[:8]}"

def _validate_context(payload: PostIn, db: Session) -> None:
    if payload.category_id and not db.scalar(select(CommunityCategory.id).where(CommunityCategory.id == payload.category_id)):
        raise HTTPException(422, "Community category not found")
    if payload.lesson_id:
        row = db.execute(select(Lesson, CourseModule, Course).join(CourseModule, Lesson.module_id == CourseModule.id).join(Course, CourseModule.course_id == Course.id).where(Lesson.id == payload.lesson_id)).first()
        if not row or not row[0].published or not row[2].published:
            raise HTTPException(422, "Lesson is not available for community context")
        lesson, module, course = row
        if (payload.module_id and payload.module_id != module.id) or (payload.course_id and payload.course_id != course.id):
            raise HTTPException(422, "Course, module and lesson context do not match")
    elif payload.module_id:
        row = db.execute(select(CourseModule, Course).join(Course, CourseModule.course_id == Course.id).where(CourseModule.id == payload.module_id)).first()
        if not row or not row[1].published or (payload.course_id and payload.course_id != row[1].id):
            raise HTTPException(422, "Module is not available for community context")
    elif payload.course_id and not db.scalar(select(Course.id).where(Course.id == payload.course_id, Course.published.is_(True))):
        raise HTTPException(422, "Course is not available for community context")

def _validate_post_content(payload: PostIn, db: Session) -> None:
    _validate_context(payload, db)
    if payload.code_language and payload.code_language not in LANGUAGES:
        raise HTTPException(422, "Unsupported code language")

def _author_out(db: Session, user_id: UUID) -> dict:
    user = db.get(User, user_id)
    return {"id": str(user_id), "display_name": user.display_name if user else "Community member"}

def _post_payload(row: CommunityPost, *, tags: list[str], vote_count: int, comment_count: int, answer_count: int, author: User | None, category: CommunityCategory | None, course: Course | None, module: CourseModule | None, lesson: Lesson | None) -> dict:
    return {"id": str(row.id), "slug": row.slug, "title": row.title, "body": row.body, "post_type": row.post_type, "language": row.language, "author_id": str(row.author_id), "author": _author_out_from_user(row.author_id, author), "category": {"id": str(category.id), "name": category.name, "slug": category.slug} if category else None, "context": {"course_id": str(course.id), "course_slug": course.slug, "course_title": course.title, "module_id": str(module.id) if module else None, "module_title": module.title if module else None, "lesson_id": str(lesson.id) if lesson else None, "lesson_slug": lesson.slug if lesson else None, "lesson_title": lesson.title if lesson else None} if course else None, "expected_behavior": row.expected_behavior, "actual_behavior": row.actual_behavior, "code_language": row.code_language, "code_snippet": row.code_snippet, "locked": row.locked, "status": row.status, "created_at": row.created_at, "updated_at": row.updated_at, "tags": tags, "vote_count": vote_count, "comment_count": comment_count, "answer_count": answer_count, "accepted_answer_id": str(row.accepted_answer_id) if row.accepted_answer_id else None}

def _author_out_from_user(user_id: UUID, user: User | None) -> dict:
    return {"id": str(user_id), "display_name": user.display_name if user else "Community member"}

def post_out(row: CommunityPost, db: Session) -> dict:
    tags = db.scalars(select(CommunityPostTag.tag).where(CommunityPostTag.post_id == row.id)).all()
    votes = db.scalar(select(func.count()).select_from(CommunityVote).where(CommunityVote.target_type == "post", CommunityVote.target_id == row.id)) or 0
    comments = db.scalar(select(func.count()).select_from(CommunityComment).where(CommunityComment.post_id == row.id, CommunityComment.status == "published")) or 0
    answers = db.scalar(select(func.count()).select_from(CommunityAnswer).where(CommunityAnswer.post_id == row.id, CommunityAnswer.status == "published")) or 0
    module = db.get(CourseModule, row.module_id) if row.module_id else None
    course = db.get(Course, row.course_id) if row.course_id else (db.get(Course, module.course_id) if module else None)
    lesson = db.get(Lesson, row.lesson_id) if row.lesson_id else None
    return _post_payload(row, tags=tags, vote_count=votes, comment_count=comments, answer_count=answers, author=db.get(User, row.author_id), category=db.get(CommunityCategory, row.category_id) if row.category_id else None, course=course, module=module, lesson=lesson)

def post_out_many(rows: list[CommunityPost], db: Session) -> list[dict]:
    if not rows:
        return []
    ids = [row.id for row in rows]
    tags = {post_id: [] for post_id in ids}
    for post_id, tag in db.execute(select(CommunityPostTag.post_id, CommunityPostTag.tag).where(CommunityPostTag.post_id.in_(ids))).all():
        tags[post_id].append(tag)
    votes = {post_id: count for post_id, count in db.execute(select(CommunityVote.target_id, func.count()).where(CommunityVote.target_type == "post", CommunityVote.target_id.in_(ids)).group_by(CommunityVote.target_id)).all()}
    comments = {post_id: count for post_id, count in db.execute(select(CommunityComment.post_id, func.count()).where(CommunityComment.status == "published", CommunityComment.post_id.in_(ids)).group_by(CommunityComment.post_id)).all()}
    answers = {post_id: count for post_id, count in db.execute(select(CommunityAnswer.post_id, func.count()).where(CommunityAnswer.status == "published", CommunityAnswer.post_id.in_(ids)).group_by(CommunityAnswer.post_id)).all()}
    authors = {user.id: user for user in db.scalars(select(User).where(User.id.in_([row.author_id for row in rows]))).all()}
    categories = {category.id: category for category in db.scalars(select(CommunityCategory).where(CommunityCategory.id.in_([row.category_id for row in rows if row.category_id]))).all()}
    modules = {module.id: module for module in db.scalars(select(CourseModule).where(CourseModule.id.in_([row.module_id for row in rows if row.module_id]))).all()}
    courses = {course.id: course for course in db.scalars(select(Course).where(Course.id.in_([row.course_id for row in rows if row.course_id] + [module.course_id for module in modules.values()]))).all()}
    lessons = {lesson.id: lesson for lesson in db.scalars(select(Lesson).where(Lesson.id.in_([row.lesson_id for row in rows if row.lesson_id]))).all()}
    return [_post_payload(row, tags=tags[row.id], vote_count=votes.get(row.id, 0), comment_count=comments.get(row.id, 0), answer_count=answers.get(row.id, 0), author=authors.get(row.author_id), category=categories.get(row.category_id), course=courses.get(row.course_id) or courses.get(modules[row.module_id].course_id) if row.module_id and row.module_id in modules else courses.get(row.course_id), module=modules.get(row.module_id), lesson=lessons.get(row.lesson_id)) for row in rows]

def visible_posts(): return select(CommunityPost).where(CommunityPost.status == "published", CommunityPost.visibility == "public")

@router.get("/posts")
def list_posts(search: str | None = None, post_type: str | None = None, tag: str | None = None, category_id: UUID | None = None, course_id: UUID | None = None, lesson_id: UUID | None = None, question_status: str | None = Query(None, alias="status"), sort: str = Query("latest", pattern="^(latest|active|votes)$"), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=50), db: Session = Depends(get_db)):
    query = visible_posts(); count = select(func.count()).select_from(CommunityPost).where(CommunityPost.status == "published", CommunityPost.visibility == "public")
    if search:
        term = f"%{clean(search)}%"; condition = CommunityPost.title.ilike(term) | CommunityPost.body.ilike(term); query = query.where(condition); count = count.where(condition)
    if post_type: query = query.where(CommunityPost.post_type == post_type); count = count.where(CommunityPost.post_type == post_type)
    if category_id: query = query.where(CommunityPost.category_id == category_id); count = count.where(CommunityPost.category_id == category_id)
    if course_id: query = query.where(CommunityPost.course_id == course_id); count = count.where(CommunityPost.course_id == course_id)
    if lesson_id: query = query.where(CommunityPost.lesson_id == lesson_id); count = count.where(CommunityPost.lesson_id == lesson_id)
    if tag:
        condition = exists(select(1).where(CommunityPostTag.post_id == CommunityPost.id, CommunityPostTag.tag == clean(tag).lower()[:50])); query = query.where(condition); count = count.where(condition)
    if question_status == "unanswered": query = query.where(CommunityPost.accepted_answer_id.is_(None)); count = count.where(CommunityPost.accepted_answer_id.is_(None))
    if question_status == "accepted": query = query.where(CommunityPost.accepted_answer_id.is_not(None)); count = count.where(CommunityPost.accepted_answer_id.is_not(None))
    vote_count = select(func.count()).select_from(CommunityVote).where(CommunityVote.target_type == "post", CommunityVote.target_id == CommunityPost.id).correlate(CommunityPost).scalar_subquery()
    activity_count = (select(func.count()).select_from(CommunityComment).where(CommunityComment.post_id == CommunityPost.id, CommunityComment.status == "published").correlate(CommunityPost).scalar_subquery() + select(func.count()).select_from(CommunityAnswer).where(CommunityAnswer.post_id == CommunityPost.id, CommunityAnswer.status == "published").correlate(CommunityPost).scalar_subquery())
    ordering = vote_count.desc() if sort == "votes" else activity_count.desc() if sort == "active" else CommunityPost.created_at.desc()
    total = db.scalar(count) or 0; rows = db.scalars(query.order_by(ordering, CommunityPost.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": post_out_many(rows, db), "page": page, "page_size": page_size, "total": total, "pages": (total + page_size - 1) // page_size if total else 0}

@router.get("/feed")
def feed(search: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=50), db: Session = Depends(get_db)): return list_posts(search=search, page=page, page_size=page_size, db=db)

@router.get("/categories")
def categories(db: Session = Depends(get_db)):
    return [{"id": str(row.id), "name": row.name, "slug": row.slug, "description": row.description} for row in db.scalars(select(CommunityCategory).order_by(CommunityCategory.name)).all()]

@router.get("/tags")
def tags(search: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(30, ge=1, le=100), db: Session = Depends(get_db)):
    query = select(CommunityPostTag.tag, func.count(CommunityPostTag.post_id).label("post_count")).join(CommunityPost, CommunityPost.id == CommunityPostTag.post_id).where(CommunityPost.status == "published", CommunityPost.visibility == "public")
    if search: query = query.where(CommunityPostTag.tag.ilike(f"%{clean(search).lower()}%"))
    rows = db.execute(query.group_by(CommunityPostTag.tag).order_by(func.count(CommunityPostTag.post_id).desc(), CommunityPostTag.tag).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [{"tag": tag, "post_count": count} for tag, count in rows], "page": page, "page_size": page_size}

@router.post("/posts", status_code=201)
def create_post(payload: PostIn, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    check_rate_limit(f"community-post:{user.id}", 8, 3600); _validate_post_content(payload, db); row = CommunityPost(author_id=user.id, title=clean(payload.title), slug=_unique_slug(payload.title, user.id, db), body=clean(payload.body), category_id=payload.category_id, course_id=payload.course_id, module_id=payload.module_id, lesson_id=payload.lesson_id, language=payload.language, expected_behavior=clean(payload.expected_behavior), actual_behavior=clean(payload.actual_behavior), code_language=payload.code_language, code_snippet=payload.code_snippet, post_type=payload.post_type); db.add(row); db.flush()
    for tag in {clean(tag).lower()[:50] for tag in payload.tags if clean(tag)}: db.add(CommunityPostTag(post_id=row.id, tag=tag))
    db.add(CommunityPostRevision(post_id=row.id, changed_by=user.id, revision_number=1, title=row.title, body=row.body, metadata_json=json.dumps({"post_type": row.post_type, "category_id": str(row.category_id) if row.category_id else None})))
    db.commit(); db.refresh(row); return post_out(row, db)

@router.get("/posts/{slug}")
def get_post(slug: str, answer_page: int = Query(1, ge=1), comment_page: int = Query(1, ge=1), page_size: int = Query(30, ge=1, le=100), db: Session = Depends(get_db)):
    row = db.scalar(visible_posts().where(CommunityPost.slug == slug))
    if not row: raise HTTPException(404, "Post not found")
    answer_count = db.scalar(select(func.count()).select_from(CommunityAnswer).where(CommunityAnswer.post_id == row.id, CommunityAnswer.status == "published")) or 0
    comment_count = db.scalar(select(func.count()).select_from(CommunityComment).where(CommunityComment.post_id == row.id, CommunityComment.status == "published")) or 0
    answers = db.scalars(select(CommunityAnswer).where(CommunityAnswer.post_id == row.id, CommunityAnswer.status == "published").order_by((CommunityAnswer.id == row.accepted_answer_id).desc(), CommunityAnswer.created_at).offset((answer_page - 1) * page_size).limit(page_size)).all(); comments = db.scalars(select(CommunityComment).where(CommunityComment.post_id == row.id, CommunityComment.status == "published").order_by(CommunityComment.created_at).offset((comment_page - 1) * page_size).limit(page_size)).all()
    return {**post_out(row, db), "answers": [{"id": str(a.id), "body": a.body, "author_id": str(a.author_id), "author": _author_out(db, a.author_id), "created_at": a.created_at, "accepted": row.accepted_answer_id == a.id} for a in answers], "comments": [{"id": str(c.id), "body": c.body, "author_id": str(c.author_id), "author": _author_out(db, c.author_id), "parent_id": str(c.parent_id) if c.parent_id else None, "created_at": c.created_at} for c in comments], "answers_page": answer_page, "comments_page": comment_page, "page_size": page_size, "answer_total": answer_count, "comment_total": comment_count}

@router.get("/posts/{post_id}/revisions")
def post_revisions(post_id: UUID, user: User = Depends(current_user), db: Session = Depends(get_db)):
    row = db.get(CommunityPost, post_id)
    if not row: raise HTTPException(404, "Post not found")
    if row.author_id != user.id and user.role not in MODERATION_ROLES: raise HTTPException(403, "You do not have access to these revisions")
    return [{"id": str(revision.id), "revision_number": revision.revision_number, "changed_by": str(revision.changed_by) if revision.changed_by else None, "title": revision.title, "body": revision.body, "metadata": json.loads(revision.metadata_json or "{}"), "created_at": revision.created_at} for revision in db.scalars(select(CommunityPostRevision).where(CommunityPostRevision.post_id == post_id).order_by(CommunityPostRevision.revision_number.desc())).all()]

def owned_post(post_id: UUID, user: User, db: Session) -> CommunityPost:
    row = db.get(CommunityPost, post_id)
    if not row or row.status == "deleted": raise HTTPException(404, "Post not found")
    if row.author_id != user.id and user.role not in {"admin", "super_admin", "moderator"}: raise HTTPException(403, "You do not own this post")
    return row

@router.patch("/posts/{post_id}")
def update_post(post_id: UUID, payload: PostIn, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = owned_post(post_id, user, db); _validate_post_content(payload, db); latest = db.scalar(select(func.max(CommunityPostRevision.revision_number)).where(CommunityPostRevision.post_id == row.id)) or 0; db.add(CommunityPostRevision(post_id=row.id, changed_by=user.id, revision_number=latest + 1, title=row.title, body=row.body, metadata_json=json.dumps({"post_type": row.post_type, "category_id": str(row.category_id) if row.category_id else None}))); row.title, row.body, row.post_type, row.category_id, row.course_id, row.module_id, row.lesson_id, row.language = clean(payload.title), clean(payload.body), payload.post_type, payload.category_id, payload.course_id, payload.module_id, payload.lesson_id, payload.language; row.expected_behavior, row.actual_behavior, row.code_language, row.code_snippet = clean(payload.expected_behavior), clean(payload.actual_behavior), payload.code_language, payload.code_snippet; db.query(CommunityPostTag).filter(CommunityPostTag.post_id == row.id).delete(synchronize_session=False)
    for tag in {clean(tag).lower()[:50] for tag in payload.tags if clean(tag)}: db.add(CommunityPostTag(post_id=row.id, tag=tag))
    db.commit(); db.refresh(row); return post_out(row, db)
@router.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: UUID, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = owned_post(post_id, user, db); row.status, row.visibility = "deleted", "private"; db.commit()

@router.post("/posts/{post_id}/answers", status_code=201)
def answer(post_id: UUID, payload: AnswerIn, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    post = db.get(CommunityPost, post_id)
    if not post or post.status != "published" or post.visibility != "public": raise HTTPException(404, "Post not found")
    if post.locked: raise HTTPException(409, "This discussion is locked")
    row = CommunityAnswer(post_id=post.id, author_id=user.id, body=clean(payload.body)); db.add(row); db.flush()
    if post.author_id != user.id: db.add(CommunityNotification(user_id=post.author_id, notification_type="new_answer", target_id=post.id, preview="Your question received a new answer."))
    db.commit(); return {"id": str(row.id), "body": row.body}
@router.patch("/answers/{answer_id}")
def update_answer(answer_id: UUID, payload: AnswerIn, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(CommunityAnswer, answer_id)
    if not row: raise HTTPException(404, "Answer not found")
    if row.author_id != user.id and user.role not in {"admin", "super_admin", "moderator"}: raise HTTPException(403, "You do not own this answer")
    row.body = clean(payload.body); db.commit(); return {"id": str(row.id), "body": row.body}
@router.post("/posts/{post_id}/accept/{answer_id}")
def accept(post_id: UUID, answer_id: UUID, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    post, row = db.get(CommunityPost, post_id), db.get(CommunityAnswer, answer_id)
    if not post or not row or row.post_id != post.id or row.status != "published": raise HTTPException(404, "Answer not found")
    if post.author_id != user.id and user.role not in {"admin", "super_admin", "moderator"}: raise HTTPException(403, "Only the question owner or moderator can accept an answer")
    post.accepted_answer_id = row.id
    if row.author_id != user.id: db.add(CommunityNotification(user_id=row.author_id, notification_type="accepted_answer", target_id=post.id, preview="Your answer was accepted."))
    db.commit(); return {"accepted_answer_id": str(row.id)}

@router.post("/posts/{post_id}/comments", status_code=201)
def comment(post_id: UUID, payload: CommentIn, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    post = db.get(CommunityPost, post_id)
    if not post or post.status != "published" or post.visibility != "public": raise HTTPException(404, "Post not found")
    if post.locked: raise HTTPException(409, "This discussion is locked")
    if payload.parent_id:
        parent = db.get(CommunityComment, payload.parent_id)
        if not parent or parent.post_id != post_id or parent.parent_id: raise HTTPException(422, "Comment nesting limit reached")
    row = CommunityComment(post_id=post_id, author_id=user.id, parent_id=payload.parent_id, body=clean(payload.body)); db.add(row)
    if post.author_id != user.id: db.add(CommunityNotification(user_id=post.author_id, notification_type="new_comment", target_id=post.id, preview="Your discussion received a new reply."))
    if payload.parent_id and parent.author_id != user.id: db.add(CommunityNotification(user_id=parent.author_id, notification_type="comment_reply", target_id=post.id, preview="Someone replied to your comment."))
    for mention in set(re.findall(r"@([A-Za-z0-9_.-]{2,120})", payload.body)):
        mentioned = db.scalar(select(User).where(User.display_name == mention, User.account_status == "active"))
        if mentioned and mentioned.id not in {user.id, post.author_id}:
            db.add(CommunityNotification(user_id=mentioned.id, notification_type="mention", target_id=post.id, preview="You were mentioned in a community reply."))
    db.commit(); return {"id": str(row.id), "body": row.body, "parent_id": str(row.parent_id) if row.parent_id else None}

def toggle_vote(target_type: str, target_id: UUID, user: User, db: Session):
    row = db.scalar(select(CommunityVote).where(CommunityVote.user_id == user.id, CommunityVote.target_type == target_type, CommunityVote.target_id == target_id))
    if row: db.delete(row); status = "removed"
    else: db.add(CommunityVote(user_id=user.id, target_type=target_type, target_id=target_id)); status = "added"
    db.commit(); return {"status": status}
@router.post("/posts/{post_id}/vote")
def vote(post_id: UUID, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    post = db.get(CommunityPost, post_id)
    if not post or post.status != "published" or post.visibility != "public": raise HTTPException(404, "Post not found")
    if post.author_id == user.id: raise HTTPException(409, "Self-voting is not allowed")
    return toggle_vote("post", post_id, user, db)
@router.post("/answers/{answer_id}/vote")
def answer_vote(answer_id: UUID, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    answer_row = db.get(CommunityAnswer, answer_id); post = db.get(CommunityPost, answer_row.post_id) if answer_row else None
    if not answer_row or answer_row.status != "published" or not post or post.status != "published" or post.visibility != "public": raise HTTPException(404, "Answer not found")
    if answer_row.author_id == user.id: raise HTTPException(409, "Self-voting is not allowed")
    return toggle_vote("answer", answer_id, user, db)
@router.post("/posts/{post_id}/bookmark")
def bookmark(post_id: UUID, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    post = db.get(CommunityPost, post_id)
    if not post or post.status != "published" or post.visibility != "public": raise HTTPException(404, "Post not found")
    row = db.scalar(select(CommunityBookmark).where(CommunityBookmark.user_id == user.id, CommunityBookmark.post_id == post_id))
    if row: db.delete(row); status = "removed"
    else: db.add(CommunityBookmark(user_id=user.id, post_id=post_id)); status = "added"
    db.commit(); return {"status": status}

@router.get("/bookmarks")
def bookmarks(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=50), user: User = Depends(verified_user), db: Session = Depends(get_db)):
    query = visible_posts().join(CommunityBookmark, CommunityBookmark.post_id == CommunityPost.id).where(CommunityBookmark.user_id == user.id)
    total = db.scalar(select(func.count()).select_from(CommunityBookmark).join(CommunityPost, CommunityPost.id == CommunityBookmark.post_id).where(CommunityBookmark.user_id == user.id, CommunityPost.status == "published", CommunityPost.visibility == "public")) or 0
    rows = db.scalars(query.order_by(CommunityPost.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": post_out_many(rows, db), "page": page, "page_size": page_size, "total": total, "pages": (total + page_size - 1) // page_size if total else 0}

@router.post("/posts/{post_id}/follow")
def follow_post(post_id: UUID, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    post = db.get(CommunityPost, post_id)
    if not post or post.status != "published" or post.visibility != "public": raise HTTPException(404, "Post not found")
    row = db.scalar(select(CommunityPostFollow).where(CommunityPostFollow.user_id == user.id, CommunityPostFollow.post_id == post_id))
    if row: db.delete(row); status = "unfollowed"
    else: db.add(CommunityPostFollow(user_id=user.id, post_id=post_id)); status = "followed"
    db.commit(); return {"status": status}

@router.post("/tags/{tag}/follow")
def follow_tag(tag: str, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    normalized = clean(tag).lower()[:50]
    if not normalized: raise HTTPException(422, "Tag is required")
    row = db.scalar(select(CommunityTagFollow).where(CommunityTagFollow.user_id == user.id, CommunityTagFollow.tag == normalized))
    if row: db.delete(row); status = "unfollowed"
    else: db.add(CommunityTagFollow(user_id=user.id, tag=normalized)); status = "followed"
    db.commit(); return {"status": status, "tag": normalized}

@router.get("/snippets")
def snippets(db: Session = Depends(get_db)):
    return [{"id": str(row.id), "title": row.title, "language": row.language, "source_code": row.source_code, "description": row.description} for row in db.scalars(select(CommunitySnippet).where(CommunitySnippet.status == "published", CommunitySnippet.visibility == "public").order_by(CommunitySnippet.created_at.desc())).all()]
@router.post("/snippets", status_code=201)
def create_snippet(payload: SnippetIn, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = CommunitySnippet(author_id=user.id, title=clean(payload.title), language=payload.language, source_code=payload.source_code, description=clean(payload.description)); db.add(row); db.commit(); return {"id": str(row.id), "title": row.title}

def group_out(row: StudyGroup, db: Session) -> dict:
    return {"id": str(row.id), "slug": row.slug, "name": row.name, "description": row.description, "visibility": row.visibility, "owner_id": str(row.owner_id), "member_count": db.scalar(select(func.count()).select_from(StudyGroupMember).where(StudyGroupMember.group_id == row.id)) or 0}
@router.get("/groups")
def groups(db: Session = Depends(get_db)): return [group_out(row, db) for row in db.scalars(select(StudyGroup).where(StudyGroup.visibility == "public", StudyGroup.status == "active").order_by(StudyGroup.name)).all()]
@router.get("/groups/{slug}")
def group_detail(slug: str, db: Session = Depends(get_db)):
    row = db.scalar(select(StudyGroup).where(StudyGroup.slug == slug, StudyGroup.status == "active"))
    if not row: raise HTTPException(404, "Group not found")
    if row.visibility == "private": raise HTTPException(403, "This group is private")
    return group_out(row, db)
@router.post("/groups", status_code=201)
def create_group(payload: GroupIn, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = StudyGroup(owner_id=user.id, name=clean(payload.name), slug=f"{slugify(payload.name) or 'group'}-{str(user.id)[:8]}", description=clean(payload.description), visibility=payload.visibility if payload.visibility in {"public", "private"} else "public"); db.add(row); db.flush(); db.add(StudyGroupMember(group_id=row.id, user_id=user.id, role="owner")); db.commit(); return group_out(row, db)
@router.post("/groups/{group_id}/join")
def join_group(group_id: UUID, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    group = db.get(StudyGroup, group_id)
    if not group or group.status != "active": raise HTTPException(404, "Group not found")
    if group.visibility == "private": raise HTTPException(403, "Private groups require an invitation")
    if not db.scalar(select(StudyGroupMember).where(StudyGroupMember.group_id == group_id, StudyGroupMember.user_id == user.id)): db.add(StudyGroupMember(group_id=group_id, user_id=user.id)); db.commit()
    return {"status": "joined"}

@router.get("/members")
def members(search: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(24, ge=1, le=50), db: Session = Depends(get_db)):
    query = select(User).where(User.account_status == "active"); count = select(func.count()).select_from(User).where(User.account_status == "active")
    if search: term = f"%{clean(search)}%"; query = query.where(User.display_name.ilike(term)); count = count.where(User.display_name.ilike(term))
    total = db.scalar(count) or 0; rows = db.scalars(query.order_by(User.display_name).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [{"username": row.display_name, "display_name": row.display_name, "user_id": str(row.id)} for row in rows], "total": total, "page": page, "pages": (total + page_size - 1) // page_size if total else 0}
@router.get("/members/{username}")
def member_profile(username: str, db: Session = Depends(get_db)):
    row = db.scalar(select(User).where(User.display_name == username, User.account_status == "active"))
    if not row: raise HTTPException(404, "Member not found")
    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == row.id))
    posts = db.scalar(select(func.count()).select_from(CommunityPost).where(CommunityPost.author_id == row.id, CommunityPost.status == "published", CommunityPost.visibility == "public")) or 0
    answers = db.scalar(select(func.count()).select_from(CommunityAnswer).where(CommunityAnswer.author_id == row.id, CommunityAnswer.status == "published")) or 0
    accepted = db.scalar(select(func.count()).select_from(CommunityAnswer).join(CommunityPost, CommunityPost.accepted_answer_id == CommunityAnswer.id).where(CommunityAnswer.author_id == row.id, CommunityAnswer.status == "published", CommunityPost.status == "published")) or 0
    skills = [skill.strip() for skill in profile.learning_interests.split(",")] if profile and profile.learning_interests else []
    return {"username": row.display_name, "display_name": row.display_name, "bio": profile.bio if profile else None, "avatar_url": profile.avatar_url if profile else None, "skills": [skill for skill in skills if skill], "joined_at": row.created_at, "public_posts": posts, "public_answers": answers, "accepted_answers": accepted, "public_contributions": posts + answers}
@router.get("/notifications")
def notifications(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(CommunityNotification).where(CommunityNotification.user_id == user.id).order_by(CommunityNotification.created_at.desc()).limit(50)).all()
    unread = db.scalar(select(func.count()).select_from(CommunityNotification).where(CommunityNotification.user_id == user.id, CommunityNotification.read_at.is_(None))) or 0
    return {"items": [{"id": str(row.id), "notification_type": row.notification_type, "target_id": str(row.target_id) if row.target_id else None, "preview": row.preview, "read": row.read_at is not None, "created_at": row.created_at} for row in rows], "unread": unread}

@router.post("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: UUID, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.scalar(select(CommunityNotification).where(CommunityNotification.id == notification_id, CommunityNotification.user_id == user.id))
    if not row: raise HTTPException(404, "Notification not found")
    row.read_at = datetime.now(timezone.utc); db.commit(); return {"id": str(row.id), "read": True}

@router.post("/notifications/read-all")
def mark_all_notifications_read(user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    rows = db.scalars(select(CommunityNotification).where(CommunityNotification.user_id == user.id, CommunityNotification.read_at.is_(None))).all(); now = datetime.now(timezone.utc)
    for row in rows: row.read_at = now
    db.commit(); return {"updated": len(rows)}

@router.post("/reports")
def report(target_type: str, target_id: UUID, reason: str = Query(..., min_length=3, max_length=500), user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if target_type not in {"post", "comment", "user"}: raise HTTPException(422, "Unsupported report target")
    check_rate_limit(f"community-report:{user.id}", 10, 3600)
    if target_type == "post" and not db.scalar(select(CommunityPost.id).where(CommunityPost.id == target_id, CommunityPost.status != "deleted")): raise HTTPException(404, "Post not found")
    if target_type == "comment" and not db.get(CommunityComment, target_id): raise HTTPException(404, "Comment not found")
    if target_type == "user" and not db.scalar(select(User.id).where(User.id == target_id, User.account_status == "active")): raise HTTPException(404, "Member not found")
    if db.scalar(select(CommunityReport.id).where(CommunityReport.reporter_id == user.id, CommunityReport.target_type == target_type, CommunityReport.target_id == target_id, CommunityReport.status.in_(["open", "under_review"]))): raise HTTPException(409, "You already reported this content")
    db.add(CommunityReport(reporter_id=user.id, target_type=target_type, target_id=target_id, reason=clean(reason))); db.commit(); return {"status": "reported"}
@router.get("/admin/overview")
def admin_overview(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return {"posts": db.scalar(select(func.count()).select_from(CommunityPost)) or 0, "comments": db.scalar(select(func.count()).select_from(CommunityComment)) or 0, "open_reports": db.scalar(select(func.count()).select_from(CommunityReport).where(CommunityReport.status == "open")) or 0, "groups": db.scalar(select(func.count()).select_from(StudyGroup)) or 0}

@router.get("/admin/categories")
def admin_categories(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return categories(db)

@router.post("/admin/categories", status_code=201)
def create_category(payload: CategoryIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    slug = slugify(payload.slug)
    if not slug: raise HTTPException(422, "Category slug is required")
    if db.scalar(select(CommunityCategory.id).where(or_(CommunityCategory.slug == slug, CommunityCategory.name == payload.name.strip()))): raise HTTPException(409, "Category already exists")
    row = CommunityCategory(name=clean(payload.name), slug=slug, description=clean(payload.description)); db.add(row); db.commit(); db.refresh(row); return {"id": str(row.id), "name": row.name, "slug": row.slug, "description": row.description}

@router.patch("/admin/categories/{category_id}")
def update_category(category_id: UUID, payload: CategoryIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(CommunityCategory, category_id)
    if not row: raise HTTPException(404, "Category not found")
    slug = slugify(payload.slug)
    if not slug: raise HTTPException(422, "Category slug is required")
    duplicate = db.scalar(select(CommunityCategory.id).where(or_(CommunityCategory.slug == slug, CommunityCategory.name == payload.name.strip()), CommunityCategory.id != category_id))
    if duplicate: raise HTTPException(409, "Category already exists")
    row.name, row.slug, row.description = clean(payload.name), slug, clean(payload.description); db.commit(); return {"id": str(row.id), "name": row.name, "slug": row.slug, "description": row.description}
@router.get("/admin/reports")
def admin_reports(user: User = Depends(require_role(*MODERATION_ROLES)), status_filter: str | None = Query(None, alias="status"), page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100), db: Session = Depends(get_db)):
    query = select(CommunityReport)
    count = select(func.count()).select_from(CommunityReport)
    if status_filter:
        query = query.where(CommunityReport.status == status_filter); count = count.where(CommunityReport.status == status_filter)
    total = db.scalar(count) or 0
    rows = db.scalars(query.order_by(CommunityReport.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [{"id": str(row.id), "target_type": row.target_type, "target_id": str(row.target_id), "reason": row.reason, "status": row.status, "resolution_note": row.resolution_note, "created_at": row.created_at, "reviewed_at": row.reviewed_at} for row in rows], "page": page, "page_size": page_size, "total": total, "pages": (total + page_size - 1) // page_size if total else 0}

def _moderate_target(target_type: str, target_id: UUID, action: str, db: Session) -> UUID:
    if target_type == "post":
        row = db.get(CommunityPost, target_id)
        if not row: raise HTTPException(404, "Post not found")
        if action in {"hide", "remove_spam"}: row.visibility, row.status = "private", "hidden"
        elif action == "restore": row.visibility, row.status = "public", "published"
        elif action == "lock": row.locked = True
        elif action == "unlock": row.locked = False
    elif target_type == "comment":
        row = db.get(CommunityComment, target_id)
        if not row: raise HTTPException(404, "Comment not found")
        if action in {"hide", "remove_spam"}: row.status = "hidden"
        elif action == "restore": row.status = "published"
    elif target_type == "answer":
        row = db.get(CommunityAnswer, target_id)
        if not row: raise HTTPException(404, "Answer not found")
        if action in {"hide", "remove_spam"}: row.status = "hidden"
        elif action == "restore": row.status = "published"
    else:
        raise HTTPException(422, "Unsupported moderation target")
    return target_id

@router.patch("/admin/reports/{report_id}")
def decide_report(report_id: UUID, payload: ReportDecisionIn, user: User = Depends(require_role(*MODERATION_ROLES)), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(CommunityReport, report_id)
    if not row: raise HTTPException(404, "Report not found")
    if payload.action: _moderate_target(row.target_type, row.target_id, payload.action, db); db.add(CommunityModerationAction(moderator_id=user.id, target_type=row.target_type, target_id=row.target_id, action=payload.action, reason=clean(payload.note)))
    row.status, row.reviewed_by, row.reviewed_at, row.resolution_note = payload.status, user.id, datetime.now(timezone.utc), clean(payload.note); db.commit()
    return {"id": str(row.id), "status": row.status, "action": payload.action}

@router.get("/admin/moderation/history")
def moderation_history(target_type: str | None = None, target_id: UUID | None = None, page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=100), user: User = Depends(require_role(*MODERATION_ROLES)), db: Session = Depends(get_db)):
    query = select(CommunityModerationAction)
    if target_type: query = query.where(CommunityModerationAction.target_type == target_type)
    if target_id: query = query.where(CommunityModerationAction.target_id == target_id)
    rows = db.scalars(query.order_by(CommunityModerationAction.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return [{"id": str(row.id), "moderator_id": str(row.moderator_id), "target_type": row.target_type, "target_id": str(row.target_id), "action": row.action, "reason": row.reason, "created_at": row.created_at} for row in rows]
