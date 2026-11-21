"""Create the first local super admin through an operator-run CLI.

This command never exposes a password in arguments or logs, refuses to run if
an administrator already exists, and records the bootstrap in the audit log.
It is intentionally not an HTTP endpoint.
"""

import argparse
import getpass
import sys

from sqlalchemy import select

from .auth import normalize_email, now, password_hasher, validate_password
from .db import SessionLocal
from .models import AdminAuditLog, User
from .rbac import PLATFORM_ADMIN_ROLES


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create the first Learn-Coding super admin")
    parser.add_argument("--email", required=True)
    parser.add_argument("--name", required=True, help="Administrator display name")
    args = parser.parse_args(argv)
    email = normalize_email(args.email)
    name = args.name.strip()
    if not name:
        print("Administrator name cannot be empty.", file=sys.stderr)
        return 2
    with SessionLocal() as db:
        if db.scalar(select(User).where(User.role.in_(PLATFORM_ADMIN_ROLES))):
            print("Refusing bootstrap: an administrator already exists.", file=sys.stderr)
            return 3
        if db.scalar(select(User).where(User.email_normalized == email)):
            print("Refusing bootstrap: that email already belongs to an account.", file=sys.stderr)
            return 4
        password = getpass.getpass("New super admin password (8-12 characters): ")
        confirmation = getpass.getpass("Confirm password: ")
        if password != confirmation:
            print("Passwords do not match.", file=sys.stderr)
            return 5
        try:
            validate_password(password)
        except Exception as exc:
            print(str(getattr(exc, "detail", exc)), file=sys.stderr)
            return 6
        user = User(
            email=email,
            email_normalized=email,
            password_hash=password_hasher.hash(password),
            display_name=name,
            role="super_admin",
            account_status="active",
            email_verified_at=now(),
            password_changed_at=now(),
        )
        db.add(user)
        db.flush()
        db.add(AdminAuditLog(actor_id=user.id, action="super_admin_bootstrapped", entity_type="user", entity_id=user.id, metadata_json='{"source":"operator_cli"}'))
        db.commit()
    print("Super admin created. You can now sign in to the Admin Panel.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
