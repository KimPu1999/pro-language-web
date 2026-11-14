import re
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from .admin_routes import full_admin
from .auth import current_user, require_csrf, check_rate_limit
from .db import get_db
from .models import CommunityAnswer, CommunityBookmark, CommunityComment, CommunityNotification, CommunityPost, CommunityPostTag, CommunityReport, CommunitySnippet, CommunityVote, StudyGroup, StudyGroupMember, User, UserProfile

router = APIRouter(prefix="/api/v1/community", tags=["community"])
POST_TYPES = {"question", "discussion", "tutorial", "project_showcase", "study_group"}
LANGUAGES = {"html", "css", "javascript", "typescript", "c", "cpp", "java", "python", "php", "sql", "json", "bash", "go", "rust"}

def clean(value: str) -> str:
    return re.sub(r"(?is)<script[^>]*>.*?</script>|javascript:", "", value).strip()
def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")

class PostIn(BaseModel):
    title: str = Field(min_length=3, max_length=220)
    body: str = Field(min_length=1, max_length=30000)
    post_type: str = "discussion"
    tags: list[str] = Field(default_factory=list, max_length=8)
    @field_validator("post_type")
    @classmethod
    def valid_type(cls, value: str) -> str:
        if value not in POST_TYPES: raise ValueError("Unsupported discussion type")
        return value
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

def post_out(row: CommunityPost, db: Session) -> dict:
    tags = db.scalars(select(CommunityPostTag.tag).where(CommunityPostTag.post_id == row.id)).all()
    votes = db.scalar(select(func.count()).select_from(CommunityVote).where(CommunityVote.target_type == "post", CommunityVote.target_id == row.id)) or 0
    comments = db.scalar(select(func.count()).select_from(CommunityComment).where(CommunityComment.post_id == row.id, CommunityComment.status == "published")) or 0
    return {"id": str(row.id), "slug": row.slug, "title": row.title, "body": row.body, "post_type": row.post_type, "author_id": str(row.author_id), "created_at": row.created_at, "updated_at": row.updated_at, "tags": tags, "vote_count": votes, "comment_count": comments, "accepted_answer_id": str(row.accepted_answer_id) if row.accepted_answer_id else None}
def visible_posts(): return select(CommunityPost).where(CommunityPost.status == "published", CommunityPost.visibility == "public")

@router.get("/posts")
def list_posts(search: str | None = None, post_type: str | None = None, tag: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=50), db: Session = Depends(get_db)):
    query = visible_posts(); count = select(func.count()).select_from(CommunityPost).where(CommunityPost.status == "published", CommunityPost.visibility == "public")
    if search:
        term = f"%{clean(search)}%"; query = query.where(CommunityPost.title.ilike(term) | CommunityPost.body.ilike(term)); count = count.where(CommunityPost.title.ilike(term) | CommunityPost.body.ilike(term))
    if post_type: query = query.where(CommunityPost.post_type == post_type); count = count.where(CommunityPost.post_type == post_type)
    if tag: query = query.join(CommunityPostTag, CommunityPostTag.post_id == CommunityPost.id).where(CommunityPostTag.tag == tag); count = count.join(CommunityPostTag, CommunityPostTag.post_id == CommunityPost.id).where(CommunityPostTag.tag == tag)
    total = db.scalar(count) or 0; rows = db.scalars(query.order_by(CommunityPost.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [post_out(row, db) for row in rows], "page": page, "page_size": page_size, "total": total, "pages": (total + page_size - 1) // page_size if total else 0}

@router.get("/feed")
def feed(search: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=50), db: Session = Depends(get_db)): return list_posts(search, None, None, page, page_size, db)

@router.post("/posts", status_code=201)
def create_post(payload: PostIn, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    check_rate_limit(f"community-post:{user.id}", 8, 3600); row = CommunityPost(author_id=user.id, title=clean(payload.title), slug=f"{slugify(payload.title) or 'discussion'}-{str(user.id)[:8]}", body=clean(payload.body), post_type=payload.post_type); db.add(row); db.flush()
    for tag in {clean(tag).lower()[:50] for tag in payload.tags if clean(tag)}: db.add(CommunityPostTag(post_id=row.id, tag=tag))
    db.commit(); db.refresh(row); return post_out(row, db)

@router.get("/posts/{slug}")
def get_post(slug: str, db: Session = Depends(get_db)):
    row = db.scalar(visible_posts().where(CommunityPost.slug == slug))
    if not row: raise HTTPException(404, "Post not found")
    answers = db.scalars(select(CommunityAnswer).where(CommunityAnswer.post_id == row.id, CommunityAnswer.status == "published").order_by(CommunityAnswer.created_at)).all(); comments = db.scalars(select(CommunityComment).where(CommunityComment.post_id == row.id, CommunityComment.status == "published").order_by(CommunityComment.created_at)).all()
    return {**post_out(row, db), "answers": [{"id": str(a.id), "body": a.body, "author_id": str(a.author_id), "created_at": a.created_at, "accepted": row.accepted_answer_id == a.id} for a in answers], "comments": [{"id": str(c.id), "body": c.body, "author_id": str(c.author_id), "parent_id": str(c.parent_id) if c.parent_id else None, "created_at": c.created_at} for c in comments]}

def owned_post(post_id: UUID, user: User, db: Session) -> CommunityPost:
    row = db.get(CommunityPost, post_id)
    if not row or row.status == "deleted": raise HTTPException(404, "Post not found")
    if row.author_id != user.id and user.role not in {"admin", "super_admin", "moderator"}: raise HTTPException(403, "You do not own this post")
    return row

@router.patch("/posts/{post_id}")
def update_post(post_id: UUID, payload: PostIn, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = owned_post(post_id, user, db); row.title, row.body, row.post_type = clean(payload.title), clean(payload.body), payload.post_type; db.query(CommunityPostTag).filter(CommunityPostTag.post_id == row.id).delete(synchronize_session=False)
    for tag in {clean(tag).lower()[:50] for tag in payload.tags if clean(tag)}: db.add(CommunityPostTag(post_id=row.id, tag=tag))
    db.commit(); db.refresh(row); return post_out(row, db)
@router.delete("/posts/{post_id}", status_code=204)
def delete_post(post_id: UUID, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = owned_post(post_id, user, db); row.status, row.visibility = "deleted", "private"; db.commit()

@router.post("/posts/{post_id}/answers", status_code=201)
def answer(post_id: UUID, payload: AnswerIn, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    post = db.get(CommunityPost, post_id)
    if not post or post.status != "published": raise HTTPException(404, "Post not found")
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
    if not post or not row or row.post_id != post.id: raise HTTPException(404, "Answer not found")
    if post.author_id != user.id and user.role not in {"admin", "super_admin", "moderator"}: raise HTTPException(403, "Only the question owner or moderator can accept an answer")
    post.accepted_answer_id = row.id
    if row.author_id != user.id: db.add(CommunityNotification(user_id=row.author_id, notification_type="accepted_answer", target_id=post.id, preview="Your answer was accepted."))
    db.commit(); return {"accepted_answer_id": str(row.id)}

@router.post("/posts/{post_id}/comments", status_code=201)
def comment(post_id: UUID, payload: CommentIn, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if not db.get(CommunityPost, post_id): raise HTTPException(404, "Post not found")
    if payload.parent_id:
        parent = db.get(CommunityComment, payload.parent_id)
        if not parent or parent.post_id != post_id or parent.parent_id: raise HTTPException(422, "Comment nesting limit reached")
    row = CommunityComment(post_id=post_id, author_id=user.id, parent_id=payload.parent_id, body=clean(payload.body)); db.add(row); db.commit(); return {"id": str(row.id), "body": row.body, "parent_id": str(row.parent_id) if row.parent_id else None}

def toggle_vote(target_type: str, target_id: UUID, user: User, db: Session):
    row = db.scalar(select(CommunityVote).where(CommunityVote.user_id == user.id, CommunityVote.target_type == target_type, CommunityVote.target_id == target_id))
    if row: db.delete(row); status = "removed"
    else: db.add(CommunityVote(user_id=user.id, target_type=target_type, target_id=target_id)); status = "added"
    db.commit(); return {"status": status}
@router.post("/posts/{post_id}/vote")
def vote(post_id: UUID, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    post = db.get(CommunityPost, post_id)
    if not post: raise HTTPException(404, "Post not found")
    if post.author_id == user.id: raise HTTPException(409, "Self-voting is not allowed")
    return toggle_vote("post", post_id, user, db)
@router.post("/answers/{answer_id}/vote")
def answer_vote(answer_id: UUID, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if not db.get(CommunityAnswer, answer_id): raise HTTPException(404, "Answer not found")
    return toggle_vote("answer", answer_id, user, db)
@router.post("/posts/{post_id}/bookmark")
def bookmark(post_id: UUID, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.scalar(select(CommunityBookmark).where(CommunityBookmark.user_id == user.id, CommunityBookmark.post_id == post_id))
    if row: db.delete(row); status = "removed"
    else: db.add(CommunityBookmark(user_id=user.id, post_id=post_id)); status = "added"
    db.commit(); return {"status": status}

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
    return {"username": row.display_name, "display_name": row.display_name, "bio": profile.bio if profile else None, "skills": (profile.learning_interests.split(",") if profile and profile.learning_interests else []), "public_contributions": posts}
@router.get("/notifications")
def notifications(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [{"id": str(row.id), "notification_type": row.notification_type, "preview": row.preview, "read": row.read_at is not None, "created_at": row.created_at} for row in db.scalars(select(CommunityNotification).where(CommunityNotification.user_id == user.id).order_by(CommunityNotification.created_at.desc()).limit(50)).all()]
@router.post("/reports")
def report(target_type: str, target_id: UUID, reason: str = Query(..., min_length=3, max_length=500), user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if target_type not in {"post", "comment", "user"}: raise HTTPException(422, "Unsupported report target")
    db.add(CommunityReport(reporter_id=user.id, target_type=target_type, target_id=target_id, reason=clean(reason))); db.commit(); return {"status": "reported"}
@router.get("/admin/overview")
def admin_overview(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return {"posts": db.scalar(select(func.count()).select_from(CommunityPost)) or 0, "comments": db.scalar(select(func.count()).select_from(CommunityComment)) or 0, "open_reports": db.scalar(select(func.count()).select_from(CommunityReport).where(CommunityReport.status == "open")) or 0, "groups": db.scalar(select(func.count()).select_from(StudyGroup)) or 0}
@router.get("/admin/reports")
def admin_reports(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return [{"id": str(row.id), "target_type": row.target_type, "target_id": str(row.target_id), "reason": row.reason, "status": row.status, "created_at": row.created_at} for row in db.scalars(select(CommunityReport).order_by(CommunityReport.created_at.desc()).limit(100)).all()]
