"""Import the reviewable Spring Boot curriculum batch."""
import argparse
from sqlalchemy import func, select
from app.db import SessionLocal
from app.models import Course, CourseModule, Lesson
from app.spring_boot_complete_curriculum import LESSONS, MODULES
from app.spring_boot_course_content import seed_spring_boot_course

def main() -> None:
    parser = argparse.ArgumentParser(description="Import the reviewable Spring Boot curriculum batch")
    parser.add_argument("--dry-run", action="store_true", help="roll back after reporting counts")
    args = parser.parse_args()
    with SessionLocal() as db:
        course = db.scalar(select(Course).where(Course.slug == "spring-boot"))
        if course is None:
            raise SystemExit("Course slug 'spring-boot' was not found; no records were changed.")
        before_modules = db.scalar(select(func.count(CourseModule.id)).where(CourseModule.course_id == course.id)) or 0
        before_lessons = db.scalar(select(func.count(Lesson.id)).join(CourseModule).where(CourseModule.course_id == course.id)) or 0
        report = seed_spring_boot_course(db, course)
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
            db.rollback(); print("transaction=rolled_back")
        else:
            db.commit(); print("transaction=committed")

if __name__ == "__main__":
    main()
