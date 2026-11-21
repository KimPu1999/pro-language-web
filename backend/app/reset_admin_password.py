"""Reset an existing administrator password through the local operator CLI.

This command never accepts a password argument, does not expose passwords in
logs, revokes the administrator's current sessions, and records an audit row.
It intentionally has no HTTP entry point.
"""

import argparse
import getpass
import json
import sys

from sqlalchemy import select

from .auth import normalize_email, now, password_hasher, validate_password
from .db import SessionLocal
from .models import AdminAuditLog, AuthSession, User
from .rbac import PLATFORM_ADMIN_ROLES


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Reset an existing Learn-Coding administrator password")
    parser.add_argument("--email", required=True)
    args = parser.parse_args(argv)
    email = normalize_email(args.email)

    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.email_normalized == email))
        if not user or user.role not in PLATFORM_ADMIN_ROLES:
            print("Refusing reset: administrator account was not found.", file=sys.stderr)
            return 3
        if user.account_status != "active" or not user.email_verified_at:
            print("Refusing reset: administrator account is not active and verified.", file=sys.stderr)
            return 4

        password = getpass.getpass("New administrator password (8-12 characters): ")
        confirmation = getpass.getpass("Confirm password: ")
        if password != confirmation:
            print("Passwords do not match.", file=sys.stderr)
            return 5
        try:
            validate_password(password)
        except Exception as exc:
            print(str(getattr(exc, "detail", exc)), file=sys.stderr)
            return 6

        user.password_hash = password_hasher.hash(password)
        user.password_changed_at = now()
        for session in db.scalars(
            select(AuthSession).where(
                AuthSession.user_id == user.id,
                AuthSession.revoked_at.is_(None),
            )
        ).all():
            session.revoked_at = now()
        db.add(
            AdminAuditLog(
                actor_id=user.id,
                action="admin_password_reset",
                entity_type="user",
                entity_id=user.id,
                metadata_json=json.dumps({"source": "operator_cli"}),
            )
        )
        db.commit()

    print("Administrator password reset. Existing sessions were revoked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
