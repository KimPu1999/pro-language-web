"""Persist the Phase 03 Docker Module 01 authored content as reviewable drafts.

The script is idempotent and never changes a published Lesson row. Run from
``backend`` after applying migrations:

    PYTHONPATH=. .venv/bin/python scripts/phase03_docker_module_one.py

Use ``--dry-run`` to validate the canonical course/module/lesson mapping
without committing any rows.
"""
from __future__ import annotations

import argparse
import json

from sqlalchemy import select

from app.db import SessionLocal
from app.docker_module_one_draft import DOCKER_COURSE_ID, seed_docker_module_one
from app.models import Course


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    db = SessionLocal()
    try:
        course = db.get(Course, DOCKER_COURSE_ID)
        if not course or course.slug != "docker":
            raise SystemExit("Canonical Docker course was not found; refusing to seed.")
        result = seed_docker_module_one(db, course)
        if args.dry_run:
            db.rollback()
            result["persisted"] = False
        else:
            db.commit()
            result["persisted"] = True
        print(json.dumps(result, indent=2, default=str))
        return 0
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    raise SystemExit(main())
