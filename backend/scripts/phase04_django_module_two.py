"""Persist only Phase 04 Django Module 02 content.

Usage from ``backend``::

    PYTHONPATH=. .venv/bin/python scripts/phase04_django_module_two.py
    PYTHONPATH=. .venv/bin/python scripts/phase04_django_module_two.py --dry-run

This script deliberately does not call the broader Django curriculum importer;
Phase 04 stops after Module 02.
"""

import argparse

from sqlalchemy import select

from app.db import SessionLocal
from app.django_module_two_content import seed_python_foundations_module
from app.models import Course


def main() -> None:
    parser = argparse.ArgumentParser(description="Persist Django Module 02 only")
    parser.add_argument("--dry-run", action="store_true", help="roll back after reporting the planned result")
    args = parser.parse_args()
    with SessionLocal() as db:
        course = db.scalar(select(Course).where(Course.slug == "django"))
        if course is None:
            raise SystemExit("Course slug 'django' was not found; no records were changed.")
        report = seed_python_foundations_module(db, course)
        print(f"course_id={course.id}")
        print(f"module_id={report['module'].id}")
        print(f"created_lessons={report['created_lessons']}")
        print(f"lesson_count={report['lesson_count']}")
        print(f"assessment_questions={report['assessment_questions']}")
        print(f"project_id={report['project'].id}")
        if args.dry_run:
            db.rollback()
            print("transaction=rolled_back")
        else:
            db.commit()
            print("transaction=committed")


if __name__ == "__main__":
    main()
