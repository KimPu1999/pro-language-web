"""Persist only Phase 05 Django Module 03 content.

Run from ``backend``.  This script intentionally does not call the broad
legacy Django curriculum importer, which would also seed later modules.
"""

import argparse

from sqlalchemy import select

from app.db import SessionLocal
from app.django_module_three_content import seed_django_module_three
from app.models import Course


def main() -> None:
    parser = argparse.ArgumentParser(description="Persist Django Module 03 only")
    parser.add_argument("--dry-run", action="store_true", help="roll back after reporting the planned result")
    args = parser.parse_args()
    with SessionLocal() as db:
        course = db.scalar(select(Course).where(Course.slug == "django"))
        if course is None:
            raise SystemExit("Course slug 'django' was not found; no records were changed.")
        report = seed_django_module_three(db, course)
        print(f"course_id={course.id}")
        print(f"module_id={report['module'].id}")
        print(f"created_lessons={report['created_lessons']}")
        print(f"lesson_count={report['lesson_count']}")
        print(f"assessment_questions={report['assessment_questions']}")
        print(f"syntax_created={report['syntax_created']}")
        print(f"project_id={report['project'].id}")
        if args.dry_run:
            db.rollback()
            print("transaction=rolled_back")
        else:
            db.commit()
            print("transaction=committed")


if __name__ == "__main__":
    main()
