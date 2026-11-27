from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from .auth import current_user, require_csrf
from .db import get_db
from .models import User
from .platform_settings_service import get_settings_group, history, list_settings, public_config, save_settings_group
from .rbac import require_platform_admin
from .schemas import PlatformSettingsPatch

router = APIRouter(prefix="/api/v1/admin/platform/settings", tags=["platform-settings"])
public_router = APIRouter(tags=["public-platform-config"])


def read_admin(user: User = Depends(current_user)) -> User:
    return require_platform_admin(user)


@router.get("")
def get_all_settings(user: User = Depends(read_admin), db: Session = Depends(get_db)):
    return list_settings(db)


@router.get("/history")
def get_settings_history(
    page: int = Query(1, ge=1, le=10000),
    page_size: int = Query(25, ge=1, le=100),
    group: str | None = Query(None),
    user: User = Depends(read_admin),
    db: Session = Depends(get_db),
):
    return history(db, page, page_size, group)


@router.get("/{group}")
def get_group_settings(group: str, user: User = Depends(read_admin), db: Session = Depends(get_db)):
    return get_settings_group(db, group)


@router.patch("/{group}")
def update_group_settings(
    group: str,
    payload: PlatformSettingsPatch,
    request: Request,
    user: User = Depends(require_platform_admin),
    _: None = Depends(require_csrf),
    db: Session = Depends(get_db),
):
    saved = save_settings_group(db, user, group, payload.values, payload.expected_version, payload.change_reason, getattr(request.state, "request_id", None))
    db.commit()
    return saved


@public_router.get("/api/v1/public/platform-config")
@public_router.get("/api/v1/site/platform-config")
def get_public_platform_config(db: Session = Depends(get_db)):
    return public_config(db)
