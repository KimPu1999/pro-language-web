"""Import the Machine Learning curriculum batch without touching other courses.

Usage from ``backend``::

    PYTHONPATH=. .venv/bin/python scripts/import_machine_learning_curriculum.py
    PYTHONPATH=. .venv/bin/python scripts/import_machine_learning_curriculum.py --dry-run

The importer is idempotent. It preserves existing course, module, lesson, and
progress identities, and leaves the newly authored lessons as drafts for
admin review.
"""

import argparse

from sqlalchemy import func, select

from app.db import SessionLocal
from app.machine_learning_complete_curriculum import LESSONS, MODULES
from app.machine_learning_course_content import seed_machine_learning_course
from app.models import Course, CourseModule, Lesson


def main() -> None:
    parser = argparse.ArgumentParser(description="Import the reviewable Machine Learning curriculum batch")
    parser.add_argument("--dry-run", action="store_true", help="roll back after reporting the planned counts")
    args = parser.parse_args()

    with SessionLocal() as db:
        course = db.scalar(select(Course).where(Course.slug == "machine-learning"))
        if course is None:
            raise SystemExit("Course slug 'machine-learning' was not found; no records were changed.")
        before_modules = db.scalar(select(func.count(CourseModule.id)).where(CourseModule.course_id == course.id)) or 0
        before_lessons = db.scalar(select(func.count(Lesson.id)).join(CourseModule).where(CourseModule.course_id == course.id)) or 0
        report = seed_machine_learning_course(db, course)
        after_modules = db.scalar(select(func.count(CourseModule.id)).where(CourseModule.course_id == course.id)) or 0
        after_lessons = db.scalar(select(func.count(Lesson.id)).join(CourseModule).where(CourseModule.course_id == course.id)) or 0
        print(f"course_id={course.id}")
        print(f"modules_before={before_modules} modules_after={after_modules}")
        print(f"lessons_before={before_lessons} lessons_after={after_lessons}")
        print("planned_module_numbers=" + ",".join(str(value) for value in MODULES))
        print("planned_lessons=" + str(sum(len(items) for items in LESSONS.values())))
        print("created_modules=" + str(report["created_modules"]))
        print("created_lessons=" + str(report["created_lessons"]))
        print("new_lessons_status=draft/unpublished")
        if args.dry_run:
            db.rollback()
            print("transaction=rolled_back")
        else:
            db.commit()
            print("transaction=committed")


if __name__ == "__main__":
    main()
