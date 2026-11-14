"""Server-side role checks for platform and content administration.

The users table stores the role as a string rather than using a separate
permission table.  Keep the legacy ``admin`` value as a compatibility alias,
but make the supported platform role explicit.
"""

from fastapi import Depends, HTTPException, status

from .auth import current_user
from .models import User

SUPER_ADMIN_ROLES = frozenset({"super_admin"})
PLATFORM_ADMIN_ROLES = frozenset({"platform_admin", "admin", "super_admin"})
CONTENT_ADMIN_ROLES = PLATFORM_ADMIN_ROLES | frozenset({"instructor"})
MODERATION_ROLES = PLATFORM_ADMIN_ROLES | frozenset({"moderator"})


def _require_roles(roles: frozenset[str], message: str):
    def dependency(user: User = Depends(current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, message)
        if not user.email_verified_at:
            raise HTTPException(status.HTTP_403_FORBIDDEN, "Email verification required")
        return user

    return dependency


require_platform_admin = _require_roles(
    PLATFORM_ADMIN_ROLES, "Administrator access required"
)
require_super_admin = _require_roles(SUPER_ADMIN_ROLES, "Super administrator access required")
