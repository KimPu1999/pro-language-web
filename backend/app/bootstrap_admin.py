"""One-time, operator-run bootstrap for the first platform super admin.

This module intentionally has no HTTP entry point and never accepts a
password. It can only promote an already-created, active, verified account.
"""

import argparse
import json
import sys

from sqlalchemy import select

from .auth import normalize_email
from .db import SessionLocal
from .models import AdminAuditLog, User
from .rbac import SUPER_ADMIN_ROLES


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bootstrap the first CodeMaster super admin")
    parser.add_argument("--email", required=True, help="Existing verified account to promote")
    parser.add_argument(
        "--confirm",
        required=True,
        help="Must exactly equal: PROMOTE <email> TO SUPER_ADMIN",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    email = normalize_email(args.email)
    expected = f"PROMOTE {email} TO SUPER_ADMIN"
    if args.confirm != expected:
        print("Refusing promotion: confirmation text did not match.", file=sys.stderr)
        return 2

    with SessionLocal() as db:
        existing = db.scalar(select(User).where(User.role.in_(SUPER_ADMIN_ROLES)))
        if existing:
            print("Refusing promotion: a super admin already exists.", file=sys.stderr)
            return 3

        user = db.scalar(select(User).where(User.email_normalized == email))
        if not user:
            print("Refusing promotion: account was not found.", file=sys.stderr)
            return 4
        if user.account_status != "active":
            print("Refusing promotion: account is not active.", file=sys.stderr)
            return 5
        if not user.email_verified_at:
            print("Refusing promotion: account email is not verified.", file=sys.stderr)
            return 6

        previous_role = user.role
        user.role = "super_admin"
        # The initial bootstrap has no pre-existing administrator actor. The
        # promoted account is recorded as the auditable bootstrap subject.
        db.add(
            AdminAuditLog(
                actor_id=user.id,
                action="super_admin_bootstrapped",
                entity_type="user",
                entity_id=user.id,
                metadata_json=json.dumps(
                    {"previous_role": previous_role, "source": "operator_cli"}
                ),
            )
        )
        db.commit()
        print("Super admin promotion completed for the verified account.")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
