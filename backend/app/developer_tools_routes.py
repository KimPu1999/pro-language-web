import json
import math
from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from .admin_routes import admin_user, audit, full_admin
from .auth import current_user, require_csrf
from .db import get_db
from .models import DeveloperTool, ToolAuditLog, ToolCategory, ToolFavorite, User
from .schemas import AdminToolCategoryIn, AdminToolIn, AdminToolOut, DeveloperToolOut, ToolCategoryOut, ToolCatalogPage
from .tool_registry import APPROVED_IMPLEMENTATION_KEYS

router = APIRouter(tags=["developer-tools"])


def tags_for(value: str | None) -> list[str]:
    return [item.strip() for item in (value or "").split("|") if item.strip()]


def public_tool(row: DeveloperTool) -> dict:
    return {
        "id": row.id, "name": row.name, "slug": row.slug,
        "short_description": row.short_description or "", "full_description": row.full_description or "",
        "icon_key": row.icon_key, "route_path": row.route_path, "tags": tags_for(row.tags),
        "display_order": row.display_order, "is_featured": row.is_featured, "is_enabled": row.is_enabled,
        "category": row.category, "implementation": row.implementation_key if row.implementation_key in APPROVED_IMPLEMENTATION_KEYS else "", "implementation_available": row.implementation_key in APPROVED_IMPLEMENTATION_KEYS,
    }


def admin_tool(row: DeveloperTool) -> dict:
    return {**public_tool(row), "implementation_key": row.implementation_key, "status": row.status, "published_at": row.published_at, "created_at": row.created_at, "updated_at": row.updated_at}


def public_filter(category: str | None = None, tag: str | None = None, search: str | None = None, featured: bool = False):
    conditions = [DeveloperTool.status == "published", DeveloperTool.is_enabled.is_(True), ToolCategory.is_active.is_(True)]
    if category:
        conditions.append(ToolCategory.slug == category)
    if tag:
        conditions.append(DeveloperTool.tags.ilike(f"%{tag.strip()}%"))
    if search:
        pattern = f"%{search.strip()}%"
        conditions.append(or_(DeveloperTool.name.ilike(pattern), DeveloperTool.short_description.ilike(pattern), DeveloperTool.full_description.ilike(pattern), DeveloperTool.tags.ilike(pattern)))
    if featured:
        conditions.append(DeveloperTool.is_featured.is_(True))
    return conditions


@router.get("/api/v1/tools/categories", response_model=list[ToolCategoryOut])
def tool_categories(db: Session = Depends(get_db)):
    return db.scalars(select(ToolCategory).where(ToolCategory.is_active.is_(True)).order_by(ToolCategory.display_order, ToolCategory.name, ToolCategory.id)).all()


@router.get("/api/v1/tools", response_model=ToolCatalogPage)
def tools(search: str | None = None, category: str | None = None, tag: str | None = None, featured: bool = False, page: int = Query(1, ge=1), page_size: int = Query(12, ge=1, le=50), db: Session = Depends(get_db)):
    conditions = public_filter(category, tag, search, featured)
    query = select(DeveloperTool).join(DeveloperTool.category).options(selectinload(DeveloperTool.category)).where(*conditions)
    count = select(func.count(DeveloperTool.id)).join(DeveloperTool.category).where(*conditions)
    total = db.scalar(count) or 0
    rows = db.scalars(query.order_by(DeveloperTool.display_order, DeveloperTool.name, DeveloperTool.id).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [public_tool(row) for row in rows], "page": page, "page_size": page_size, "total": total, "pages": math.ceil(total / page_size) if total else 0}


@router.get("/api/v1/tools/{slug}", response_model=DeveloperToolOut)
def tool(slug: str, db: Session = Depends(get_db)):
    row = db.scalar(select(DeveloperTool).join(DeveloperTool.category).options(selectinload(DeveloperTool.category)).where(DeveloperTool.slug == slug, *public_filter()))
    if not row:
        raise HTTPException(404, "Published developer tool not found")
    return public_tool(row)


@router.get("/api/v1/me/tools/favorites")
def my_tool_favorites(user: User = Depends(current_user), db: Session = Depends(get_db)):
    rows = db.scalars(select(DeveloperTool).join(ToolFavorite, ToolFavorite.tool_id == DeveloperTool.id).join(DeveloperTool.category).options(selectinload(DeveloperTool.category)).where(ToolFavorite.user_id == user.id, *public_filter())).all()
    return {"items": [public_tool(row) for row in rows]}


@router.post("/api/v1/tools/{slug}/favorite")
def add_tool_favorite(slug: str, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.scalar(select(DeveloperTool).join(DeveloperTool.category).where(DeveloperTool.slug == slug, *public_filter()))
    if not row:
        raise HTTPException(404, "Published developer tool not found")
    if not db.get(ToolFavorite, {"user_id": user.id, "tool_id": row.id}):
        db.add(ToolFavorite(user_id=user.id, tool_id=row.id))
        db.commit()
    return {"status": "saved"}


@router.delete("/api/v1/tools/{slug}/favorite")
def remove_tool_favorite(slug: str, user: User = Depends(current_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.scalar(select(DeveloperTool).where(DeveloperTool.slug == slug))
    if row:
        favorite = db.get(ToolFavorite, {"user_id": user.id, "tool_id": row.id})
        if favorite:
            db.delete(favorite)
            db.commit()
    return {"status": "removed"}


@router.get("/api/v1/admin/tools/meta")
def tool_admin_meta(user: User = Depends(admin_user), db: Session = Depends(get_db)):
    return {"implementation_keys": sorted(APPROVED_IMPLEMENTATION_KEYS), "categories": [ToolCategoryOut.model_validate(row).model_dump(mode="json") for row in db.scalars(select(ToolCategory).order_by(ToolCategory.display_order, ToolCategory.name)).all()]}


@router.get("/api/v1/admin/tools")
def admin_tools(search: str | None = None, category: str | None = None, status: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), user: User = Depends(admin_user), db: Session = Depends(get_db)):
    conditions = []
    if search:
        pattern = f"%{search.strip()}%"
        conditions.append(or_(DeveloperTool.name.ilike(pattern), DeveloperTool.slug.ilike(pattern), DeveloperTool.tags.ilike(pattern)))
    if category: conditions.append(ToolCategory.slug == category)
    if status: conditions.append(DeveloperTool.status == status)
    query = select(DeveloperTool).outerjoin(DeveloperTool.category).options(selectinload(DeveloperTool.category)).where(*conditions)
    count = select(func.count(DeveloperTool.id)).select_from(DeveloperTool).outerjoin(DeveloperTool.category).where(*conditions)
    total = db.scalar(count) or 0
    rows = db.scalars(query.order_by(DeveloperTool.display_order, DeveloperTool.name, DeveloperTool.id).offset((page - 1) * page_size).limit(page_size)).all()
    return {"items": [admin_tool(row) for row in rows], "page": page, "page_size": page_size, "total": total, "pages": math.ceil(total / page_size) if total else 0}


def validate_category(payload: AdminToolIn, db: Session):
    if payload.category_id and not db.get(ToolCategory, payload.category_id):
        raise HTTPException(422, "Tool category does not exist")


def validate_unique_slug(slug: str, db: Session, tool_id: UUID | None = None):
    row = db.scalar(select(DeveloperTool).where(DeveloperTool.slug == slug, DeveloperTool.id != tool_id if tool_id else True))
    if row: raise HTTPException(409, "A tool with this slug already exists")


@router.get("/api/v1/admin/tools/{tool_id}")
def admin_tool_detail(tool_id: UUID, user: User = Depends(admin_user), db: Session = Depends(get_db)):
    row = db.scalar(select(DeveloperTool).options(selectinload(DeveloperTool.category)).where(DeveloperTool.id == tool_id))
    if not row: raise HTTPException(404, "Tool not found")
    return admin_tool(row)


@router.post("/api/v1/admin/tools", status_code=201)
def create_tool(payload: AdminToolIn, user: User = Depends(admin_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    validate_unique_slug(payload.slug, db); validate_category(payload, db)
    row = DeveloperTool(**payload.model_dump(exclude={"tags", "status"}), tags="|".join(payload.tags), status="draft")
    db.add(row); db.flush(); db.add(ToolAuditLog(tool_id=row.id, actor_id=user.id, action="created")); audit(db, user, "tool_created", "developer_tool", row.id); db.commit(); db.refresh(row)
    return admin_tool(row)


@router.patch("/api/v1/admin/tools/{tool_id}")
def update_tool(tool_id: UUID, payload: AdminToolIn, user: User = Depends(admin_user), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(DeveloperTool, tool_id)
    if not row: raise HTTPException(404, "Tool not found")
    if payload.status == "published" and user.role not in {"platform_admin", "super_admin", "admin"}:
        raise HTTPException(403, "Administrator publishing permission required")
    validate_unique_slug(payload.slug, db, tool_id); validate_category(payload, db)
    for key, value in payload.model_dump(exclude={"tags", "status"}).items(): setattr(row, key, value)
    row.tags = "|".join(payload.tags)
    if payload.status != "published" and row.status == "published": row.published_at = None
    row.status = payload.status
    db.add(ToolAuditLog(tool_id=row.id, actor_id=user.id, action="updated")); audit(db, user, "tool_updated", "developer_tool", row.id); db.commit(); db.refresh(row)
    return admin_tool(row)


def set_tool_status(tool_id: UUID, status: str, user: User, db: Session):
    row = db.get(DeveloperTool, tool_id)
    if not row: raise HTTPException(404, "Tool not found")
    if status == "published":
        if not row.is_enabled: raise HTTPException(422, "Enable the tool before publishing")
        if row.implementation_key not in APPROVED_IMPLEMENTATION_KEYS: raise HTTPException(422, "Implementation key is not registered")
        row.published_at = datetime.now(timezone.utc)
    else: row.published_at = None
    row.status = status
    db.add(ToolAuditLog(tool_id=row.id, actor_id=user.id, action=status)); audit(db, user, f"tool_{status}", "developer_tool", row.id); db.commit(); db.refresh(row)
    return admin_tool(row)


@router.post("/api/v1/admin/tools/{tool_id}/publish")
def publish_tool(tool_id: UUID, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    return set_tool_status(tool_id, "published", user, db)


@router.post("/api/v1/admin/tools/{tool_id}/unpublish")
def unpublish_tool(tool_id: UUID, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    return set_tool_status(tool_id, "draft", user, db)


@router.post("/api/v1/admin/tools/{tool_id}/archive")
def archive_tool(tool_id: UUID, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    return set_tool_status(tool_id, "archived", user, db)


@router.post("/api/v1/admin/tools/reorder")
def reorder_tools(order: list[UUID], user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    for position, tool_id in enumerate(order):
        row = db.get(DeveloperTool, tool_id)
        if row: row.display_order = position * 10
    audit(db, user, "tools_reordered", "developer_tool"); db.commit(); return {"status": "ok"}


@router.get("/api/v1/admin/tool-categories")
def admin_categories(user: User = Depends(admin_user), db: Session = Depends(get_db)):
    return db.scalars(select(ToolCategory).order_by(ToolCategory.display_order, ToolCategory.name)).all()


@router.post("/api/v1/admin/tool-categories", status_code=201)
def create_category(payload: AdminToolCategoryIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    if db.scalar(select(ToolCategory).where(or_(ToolCategory.slug == payload.slug, ToolCategory.name == payload.name))): raise HTTPException(409, "Category name or slug already exists")
    row = ToolCategory(**payload.model_dump()); db.add(row); db.flush(); audit(db, user, "tool_category_created", "tool_category", row.id); db.commit(); db.refresh(row); return row


@router.patch("/api/v1/admin/tool-categories/{category_id}")
def update_category(category_id: UUID, payload: AdminToolCategoryIn, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(ToolCategory, category_id)
    if not row: raise HTTPException(404, "Category not found")
    duplicate = db.scalar(select(ToolCategory).where(or_(ToolCategory.slug == payload.slug, ToolCategory.name == payload.name), ToolCategory.id != category_id))
    if duplicate: raise HTTPException(409, "Category name or slug already exists")
    for key, value in payload.model_dump().items(): setattr(row, key, value)
    audit(db, user, "tool_category_updated", "tool_category", row.id); db.commit(); db.refresh(row); return row


@router.post("/api/v1/admin/tool-categories/{category_id}/disable")
def disable_category(category_id: UUID, user: User = Depends(full_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    row = db.get(ToolCategory, category_id)
    if not row: raise HTTPException(404, "Category not found")
    row.is_active = False
    audit(db, user, "tool_category_disabled", "tool_category", row.id); db.commit(); return {"status": "disabled"}
