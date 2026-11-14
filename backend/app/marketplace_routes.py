"""Free marketplace and community-content APIs.

Published visibility is explicit. Drafts and moderation records never enter
public search, and contributor/moderation mutations remain server-authorized.
"""
import re
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from .admin_routes import full_admin
from .auth import check_rate_limit, current_user, require_csrf, verified_user
from .db import get_db
from .models import (
    Course, MarketplaceAuditLog, MarketplaceCollection,
    MarketplaceCollectionItem, MarketplaceContentReport, MarketplaceContribution,
    MarketplaceContributorProfile, MarketplaceContributorReputation,
    MarketplaceResource, MarketplaceResourceLicense, MarketplaceResourceReview,
    MarketplaceResourceTag, MarketplaceResourceType, MarketplaceReviewDecision,
    MarketplaceReviewRequest, MarketplaceResourceVersion, User, UserProfile,
)

router = APIRouter(prefix="/api/v1/marketplace", tags=["marketplace"])
MODERATION_ROLES = {"moderator", "admin", "platform_admin", "super_admin"}
CONTRIBUTOR_ROLES = MODERATION_ROLES | {"instructor", "mentor"}
LICENSES = {"CC-BY-4.0", "CC-BY-SA-4.0", "CC0-1.0", "MIT"}


def clean(value: str) -> str:
    return re.sub(r"(?is)<script[^>]*>.*?</script>|javascript:", "", value).strip()


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")


class ResourceIn(BaseModel):
    title: str = Field(min_length=3, max_length=220)
    summary: str = Field(default="", max_length=2000)
    content_markdown: str = Field(min_length=1, max_length=100000)
    resource_type: str = Field(default="tutorial", min_length=2, max_length=80)
    difficulty: str = Field(default="Beginner", max_length=30)
    language: str = Field(default="English", max_length=30)
    duration_minutes: int = Field(default=0, ge=0, le=10000)
    license_code: str = Field(default="CC-BY-4.0", max_length=80)
    attribution: str = Field(default="", max_length=1000)
    tags: list[str] = Field(default_factory=list, max_length=20)


class ReviewIn(BaseModel):
    rating: int = Field(ge=1, le=5)
    body: str = Field(default="", max_length=5000)


class CollectionIn(BaseModel):
    title: str = Field(min_length=2, max_length=180)
    description: str = Field(default="", max_length=2000)
    visibility: str = Field(default="private", pattern="^(private|public)$")


class ReportIn(BaseModel):
    reason: str = Field(min_length=3, max_length=60)
    details: str = Field(default="", max_length=5000)


class DecisionIn(BaseModel):
    decision: str = Field(pattern="^(approved|changes_requested|rejected|published|unpublished|archived)$")
    note: str = Field(default="", max_length=3000)


class VerificationIn(BaseModel):
    evidence: str = Field(min_length=3, max_length=3000)


def audit(db: Session, actor: User | None, action: str, resource_id: UUID | None = None):
    db.add(MarketplaceAuditLog(actor_id=actor.id if actor else None, action=action, resource_id=resource_id))


def resource_out(row: MarketplaceResource, db: Session) -> dict:
    author = db.get(User, row.author_id)
    resource_type = db.get(MarketplaceResourceType, row.resource_type_id)
    tags = db.scalars(select(MarketplaceResourceTag.tag).where(MarketplaceResourceTag.resource_id == row.id)).all()
    rating, reviews = db.execute(select(func.avg(MarketplaceResourceReview.rating), func.count(MarketplaceResourceReview.id)).where(MarketplaceResourceReview.resource_id == row.id, MarketplaceResourceReview.status == "published")).one()
    return {"id": str(row.id), "slug": row.slug, "title": row.title, "summary": row.summary, "content_markdown": row.content_markdown, "resource_type": resource_type.slug if resource_type else "resource", "difficulty": row.difficulty, "language": row.language, "duration_minutes": row.duration_minutes, "license": row.license_code, "attribution": row.attribution, "status": row.status, "visibility": row.visibility, "version": row.version, "author": {"id": str(author.id), "display_name": author.display_name} if author else None, "tags": tags, "rating": round(float(rating), 2) if rating is not None else None, "review_count": reviews or 0}


def public_filter(query):
    return query.where(MarketplaceResource.status == "published", MarketplaceResource.visibility == "public")


def get_public_resource(slug: str, db: Session):
    row = db.scalar(public_filter(select(MarketplaceResource).where(MarketplaceResource.slug == slug)))
    if not row:
        raise HTTPException(404, "Published resource not found")
    return row


@router.get("")
def marketplace_home(db: Session = Depends(get_db)):
    courses = db.scalars(select(Course).where(Course.published.is_(True)).order_by(Course.updated_at.desc()).limit(12)).all()
    resources = db.scalars(public_filter(select(MarketplaceResource)).order_by(MarketplaceResource.published_at.desc()).limit(12)).all()
    return {"courses": [{"id": str(x.id), "slug": x.slug, "title": x.title, "level": x.level, "duration_minutes": x.duration_minutes} for x in courses], "resources": [resource_out(x, db) for x in resources], "source": "published_database_records", "payments": "not_supported"}


@router.get("/search")
def search(q: str | None = None, programming_language: str | None = None, difficulty: str | None = None, content_type: str | None = None, language: str | None = None, license_code: str | None = None, sort: str = Query("recent", pattern="^(recent|title|rating)$"), page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=50), db: Session = Depends(get_db)):
    if q and len(q) > 200:
        raise HTTPException(422, "Search query is too long")
    query = public_filter(select(MarketplaceResource))
    if q:
        term = f"%{clean(q)}%"
        query = query.where(or_(MarketplaceResource.title.ilike(term), MarketplaceResource.summary.ilike(term), MarketplaceResource.content_markdown.ilike(term)))
    if difficulty: query = query.where(MarketplaceResource.difficulty == difficulty)
    if language: query = query.where(MarketplaceResource.language == language)
    if license_code: query = query.where(MarketplaceResource.license_code == license_code)
    if content_type:
        resource_type = db.scalar(select(MarketplaceResourceType).where(MarketplaceResourceType.slug == content_type))
        if not resource_type: return {"items": [], "total": 0, "page": page, "page_size": page_size, "pages": 0}
        query = query.where(MarketplaceResource.resource_type_id == resource_type.id)
    if programming_language:
        query = query.join(MarketplaceResourceTag, MarketplaceResourceTag.resource_id == MarketplaceResource.id).where(MarketplaceResourceTag.tag == programming_language)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    if sort == "title": query = query.order_by(MarketplaceResource.title)
    else: query = query.order_by(MarketplaceResource.published_at.desc(), MarketplaceResource.id.desc())
    rows = db.scalars(query.offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [resource_out(x, db) for x in rows], "total": total, "page": page, "page_size": page_size, "pages": (total + page_size - 1) // page_size if total else 0}


@router.get("/resources")
def resources(page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=50), db: Session = Depends(get_db)):
    return search(page=page, page_size=page_size, db=db)


@router.get("/resources/{slug}")
def resource_detail(slug: str, db: Session = Depends(get_db)):
    return resource_out(get_public_resource(slug, db), db)


@router.get("/instructors/{slug}")
def instructor_profile(slug: str, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.display_name == slug, User.account_status == "active"))
    if not user: raise HTTPException(404, "Instructor not found")
    profile = db.scalar(select(UserProfile).where(UserProfile.user_id == user.id))
    verified = db.scalar(select(MarketplaceContributorProfile).where(MarketplaceContributorProfile.user_id == user.id, MarketplaceContributorProfile.verification_status == "verified"))
    rows = db.scalars(public_filter(select(MarketplaceResource).where(MarketplaceResource.author_id == user.id)).order_by(MarketplaceResource.published_at.desc())).all()
    courses = db.scalars(select(Course).where(Course.created_by == user.id, Course.published.is_(True))).all()
    return {"display_name": user.display_name, "avatar_url": profile.avatar_url if profile else None, "bio": profile.bio if profile else None, "verified": bool(verified), "resources": [resource_out(x, db) for x in rows], "courses": [{"slug": x.slug, "title": x.title} for x in courses]}


@router.get("/contributors")
def contributors(db: Session = Depends(get_db)):
    rows = db.scalars(select(MarketplaceContributorProfile).where(MarketplaceContributorProfile.verification_status == "verified")).all()
    return [{"user_id": str(x.user_id), "verification_status": x.verification_status, "reputation": (lambda r: {"score": r.score, "approved_contributions": r.approved_contributions} if r else {"score": 0, "approved_contributions": 0})(db.scalar(select(MarketplaceContributorReputation).where(MarketplaceContributorReputation.user_id == x.user_id)))} for x in rows]


@router.post("/instructors/verification", status_code=202)
def request_verification(payload: VerificationIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    profile = db.scalar(select(MarketplaceContributorProfile).where(MarketplaceContributorProfile.user_id == user.id))
    if not profile:
        profile = MarketplaceContributorProfile(user_id=user.id)
        db.add(profile)
    profile.verification_status, profile.verification_note = "pending", clean(payload.evidence)
    audit(db, user, "verification_requested"); db.commit()
    return {"status": profile.verification_status}


@router.get("/recommended")
def recommended(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(public_filter(select(MarketplaceResource)).order_by(MarketplaceResource.published_at.desc()).limit(10)).all()
    items = [{**resource_out(x, db), "reason": "Published free resource available for your learning journey."} for x in rows]
    return {"items": items, "personalized": False, "evidence": ["published_catalog"], "status": "fallback_catalog"}


@router.post("/resources", status_code=201)
def create_resource(payload: ResourceIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    check_rate_limit(f"marketplace-create:{user.id}", 10, 3600)
    if user.role not in CONTRIBUTOR_ROLES: raise HTTPException(403, "Contributor eligibility required")
    if payload.license_code not in LICENSES: raise HTTPException(422, "Unsupported educational license")
    resource_type = db.scalar(select(MarketplaceResourceType).where(MarketplaceResourceType.slug == payload.resource_type))
    if not resource_type: resource_type = MarketplaceResourceType(slug=payload.resource_type, name=payload.resource_type.title()); db.add(resource_type); db.flush()
    slug = slugify(payload.title) or "resource"
    if db.scalar(select(MarketplaceResource).where(MarketplaceResource.slug == slug)): slug = f"{slug}-{str(user.id)[:8]}"
    row = MarketplaceResource(author_id=user.id, resource_type_id=resource_type.id, title=clean(payload.title), summary=clean(payload.summary), content_markdown=clean(payload.content_markdown), difficulty=payload.difficulty, language=payload.language, duration_minutes=payload.duration_minutes, license_code=payload.license_code, attribution=clean(payload.attribution), slug=slug)
    db.add(row); db.flush(); db.add(MarketplaceResourceVersion(resource_id=row.id, version_number=1, content_markdown=row.content_markdown, created_by=user.id)); db.add(MarketplaceResourceLicense(resource_id=row.id, license_code=row.license_code, attribution_required=True, source_url=""));
    for tag in set(clean(x).lower() for x in payload.tags if clean(x)): db.add(MarketplaceResourceTag(resource_id=row.id, tag=tag[:60]))
    db.add(MarketplaceContribution(resource_id=row.id, contributor_id=user.id)); audit(db, user, "resource_created", row.id); db.commit(); db.refresh(row); return resource_out(row, db)


@router.patch("/resources/{resource_id}")
def update_resource(resource_id: UUID, payload: ResourceIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(MarketplaceResource, resource_id)
    if not row: raise HTTPException(404, "Resource not found")
    if row.author_id != user.id and user.role not in MODERATION_ROLES: raise HTTPException(403, "Resource ownership required")
    if row.status == "published" and user.role not in MODERATION_ROLES: raise HTTPException(409, "Published resources require a new review")
    if payload.license_code not in LICENSES: raise HTTPException(422, "Unsupported educational license")
    row.title, row.summary, row.content_markdown, row.difficulty, row.language, row.duration_minutes, row.license_code, row.attribution = clean(payload.title), clean(payload.summary), clean(payload.content_markdown), payload.difficulty, payload.language, payload.duration_minutes, payload.license_code, clean(payload.attribution)
    row.version += 1; row.status = "draft" if user.role not in MODERATION_ROLES else row.status
    db.add(MarketplaceResourceVersion(resource_id=row.id, version_number=row.version, content_markdown=row.content_markdown, created_by=user.id)); audit(db, user, "resource_updated", row.id); db.commit(); return resource_out(row, db)


@router.post("/resources/{resource_id}/submit", status_code=202)
def submit_resource(resource_id: UUID, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(MarketplaceResource, resource_id)
    if not row or row.author_id != user.id: raise HTTPException(404, "Owned draft not found")
    if not row.attribution and row.license_code != "CC0-1.0": raise HTTPException(422, "Attribution is required for this license")
    row.status = "submitted"; db.add(MarketplaceReviewRequest(resource_id=row.id, requester_id=user.id)); audit(db, user, "resource_submitted", row.id); db.commit(); return {"id": str(row.id), "status": row.status}


@router.post("/resources/{resource_id}/reviews", status_code=201)
def review(resource_id: UUID, payload: ReviewIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    check_rate_limit(f"marketplace-review:{user.id}", 10, 3600)
    row = get_public_resource(str(db.get(MarketplaceResource, resource_id).slug), db) if db.get(MarketplaceResource, resource_id) else None
    if not row: raise HTTPException(404, "Published resource not found")
    if row.author_id == user.id: raise HTTPException(409, "Self-review is not allowed")
    existing = db.scalar(select(MarketplaceResourceReview).where(MarketplaceResourceReview.resource_id == row.id, MarketplaceResourceReview.reviewer_id == user.id))
    if existing: raise HTTPException(409, "You have already reviewed this resource")
    item = MarketplaceResourceReview(resource_id=row.id, reviewer_id=user.id, rating=payload.rating, body=clean(payload.body)); db.add(item); audit(db, user, "resource_review_created", row.id); db.commit(); return {"id": str(item.id), "rating": item.rating, "status": item.status}


@router.post("/resources/{resource_id}/report", status_code=201)
def report(resource_id: UUID, payload: ReportIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if not db.get(MarketplaceResource, resource_id): raise HTTPException(404, "Resource not found")
    check_rate_limit(f"marketplace-report:{user.id}", 10, 3600); item = MarketplaceContentReport(resource_id=resource_id, reporter_id=user.id, reason=clean(payload.reason), details=clean(payload.details)); db.add(item); audit(db, user, "resource_reported", resource_id); db.commit(); return {"id": str(item.id), "status": item.status}


@router.get("/collections")
def collections(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(MarketplaceCollection).where(or_(MarketplaceCollection.owner_id == user.id, MarketplaceCollection.visibility == "public")).order_by(MarketplaceCollection.created_at.desc())).all()
    return [{"id": str(x.id), "title": x.title, "slug": x.slug, "description": x.description, "visibility": x.visibility, "items": db.scalar(select(func.count()).select_from(MarketplaceCollectionItem).where(MarketplaceCollectionItem.collection_id == x.id)) or 0} for x in rows]


@router.post("/collections", status_code=201)
def create_collection(payload: CollectionIn, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    slug = slugify(payload.title) or "collection"; slug = f"{slug}-{str(user.id)[:8]}"; row = MarketplaceCollection(owner_id=user.id, title=clean(payload.title), slug=slug, description=clean(payload.description), visibility=payload.visibility); db.add(row); audit(db, user, "collection_created", None); db.commit(); return {"id": str(row.id), "slug": row.slug, "visibility": row.visibility}


@router.post("/collections/{collection_id}/items", status_code=201)
def add_collection_item(collection_id: UUID, resource_id: UUID, user: User = Depends(verified_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    collection = db.get(MarketplaceCollection, collection_id); resource = db.get(MarketplaceResource, resource_id)
    if not collection or collection.owner_id != user.id: raise HTTPException(404, "Owned collection not found")
    if not resource or resource.status != "published" or resource.visibility != "public": raise HTTPException(404, "Published resource not found")
    db.add(MarketplaceCollectionItem(collection_id=collection.id, resource_id=resource.id, position=0)); db.commit(); return {"status": "saved"}


@router.get("/moderation/queue")
def moderation_queue(user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role not in MODERATION_ROLES: raise HTTPException(403, "Moderator permission required")
    return {"reviews": [{"id": str(x.id), "resource_id": str(x.resource_id), "status": x.status} for x in db.scalars(select(MarketplaceReviewRequest).where(MarketplaceReviewRequest.status.in_(["submitted", "under_review"])).order_by(MarketplaceReviewRequest.created_at)).all()], "reports": [{"id": str(x.id), "resource_id": str(x.resource_id), "reason": x.reason, "details": x.details, "status": x.status} for x in db.scalars(select(MarketplaceContentReport).where(MarketplaceContentReport.status == "open").order_by(MarketplaceContentReport.created_at)).all()]}


@router.get("/moderation/verification")
def verification_queue(user: User = Depends(current_user), db: Session = Depends(get_db)):
    if user.role not in MODERATION_ROLES: raise HTTPException(403, "Moderator permission required")
    return [{"user_id": str(x.user_id), "status": x.verification_status, "evidence": x.verification_note} for x in db.scalars(select(MarketplaceContributorProfile).where(MarketplaceContributorProfile.verification_status == "pending")).all()]


@router.post("/moderation/verification/{user_id}")
def decide_verification(user_id: UUID, payload: DecisionIn, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if user.role not in MODERATION_ROLES: raise HTTPException(403, "Moderator permission required")
    if payload.decision not in {"approved", "rejected"}: raise HTTPException(422, "Verification decision must be approved or rejected")
    profile = db.scalar(select(MarketplaceContributorProfile).where(MarketplaceContributorProfile.user_id == user_id))
    if not profile: raise HTTPException(404, "Verification request not found")
    profile.verification_status = "verified" if payload.decision == "approved" else "rejected"; profile.verification_note = clean(payload.note); audit(db, user, f"verification_{payload.decision}"); db.commit()
    return {"user_id": str(user_id), "status": profile.verification_status}


@router.post("/moderation/reviews/{request_id}")
def decide(request_id: UUID, payload: DecisionIn, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if user.role not in MODERATION_ROLES: raise HTTPException(403, "Moderator permission required")
    request = db.get(MarketplaceReviewRequest, request_id)
    if not request: raise HTTPException(404, "Review request not found")
    resource = db.get(MarketplaceResource, request.resource_id); request.status = payload.decision; db.add(MarketplaceReviewDecision(request_id=request.id, reviewer_id=user.id, decision=payload.decision, note=clean(payload.note)))
    if payload.decision in {"approved", "published"}: resource.status, resource.visibility, resource.published_at = "published", "public", datetime.now(timezone.utc)
    elif payload.decision in {"rejected", "changes_requested", "archived", "unpublished"}: resource.status = payload.decision; resource.visibility = "private"
    audit(db, user, f"resource_{payload.decision}", resource.id); db.commit(); return {"status": request.status, "resource_status": resource.status}


@router.get("/analytics")
def analytics(user: User = Depends(full_admin), db: Session = Depends(get_db)):
    return {"published_resources": db.scalar(select(func.count()).select_from(MarketplaceResource).where(MarketplaceResource.status == "published")) or 0, "contributors": db.scalar(select(func.count(func.distinct(MarketplaceResource.author_id))).select_from(MarketplaceResource).where(MarketplaceResource.status == "published")) or 0, "pending_reviews": db.scalar(select(func.count()).select_from(MarketplaceReviewRequest).where(MarketplaceReviewRequest.status.in_(["submitted", "under_review"]))) or 0, "open_reports": db.scalar(select(func.count()).select_from(MarketplaceContentReport).where(MarketplaceContentReport.status == "open")) or 0, "data_source": "persisted_marketplace_records"}


@router.get("/instructor/analytics")
def instructor_analytics(user: User = Depends(verified_user), db: Session = Depends(get_db)):
    if user.role not in CONTRIBUTOR_ROLES: raise HTTPException(403, "Instructor or contributor permission required")
    return {"published_resources": db.scalar(select(func.count()).select_from(MarketplaceResource).where(MarketplaceResource.author_id == user.id, MarketplaceResource.status == "published")) or 0, "reviews": db.scalar(select(func.count()).select_from(MarketplaceResourceReview).join(MarketplaceResource, MarketplaceResourceReview.resource_id == MarketplaceResource.id).where(MarketplaceResource.author_id == user.id)) or 0, "data_source": "persisted_marketplace_records"}
