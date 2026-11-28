"""Print a live course-by-course syntax reference coverage report."""
import json

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db import SessionLocal
from app.models import Course, LessonSyntaxReference, SyntaxReference
from app.syntax_routes import is_complete

TOPICS = {
    "c-programming": ["variables", "pointers", "file"],
    "cpp-programming": ["classes", "stl", "smart"],
    "java": ["classes", "streams", "completable"],
    "advanced-java": ["classes", "streams", "completable"],
    "python": ["functions", "comprehensions", "context"],
    "javascript": ["map", "promises", "fetch"],
    "typescript": ["map", "promises", "fetch"],
    "html": ["semantic", "forms", "links"],
    "css": ["flexbox", "grid", "custom"],
    "react": ["components", "state", "effects"],
    "sql": ["select", "join", "transactions"],
    "postgresql": ["select", "join", "transactions"],
    "mysql": ["select", "join", "transactions"],
    "linux": ["git", "docker", "shell"],
    "git": ["git", "docker", "shell"],
    "docker": ["git", "docker", "shell"],
    "algorithms": ["binary", "stack", "process"],
    "data-structures": ["binary", "stack", "process"],
    "operating-systems": ["binary", "stack", "process"],
    "cybersecurity-fundamentals": ["parameter", "content", "input"],
    "secure-coding": ["parameter", "content", "input"],
}


def main():
    db = SessionLocal()
    courses = db.scalars(select(Course).options(selectinload(Course.language), selectinload(Course.syntax_references).selectinload(SyntaxReference.examples), selectinload(Course.syntax_references).selectinload(SyntaxReference.translations)).order_by(Course.title)).all()
    rows = []
    for course in courses:
        refs = list(course.syntax_references)
        title_text = " ".join(f"{row.title} {row.category}" for row in refs).casefold()
        linked = db.scalars(select(LessonSyntaxReference.reference_id).where(LessonSyntaxReference.reference_id.in_([row.id for row in refs]))).all() if refs else []
        missing_examples = sum(max(0, (row.minimum_examples or 5) - len(row.examples)) for row in refs)
        incomplete = [row.slug for row in refs if not is_complete(row)]
        mm_ready = [row.slug for row in refs if any(translation.locale == "my" and translation.status in {"approved", "published"} for translation in row.translations)]
        planned = TOPICS.get(course.slug, [])
        missing_topics = [topic for topic in planned if topic.casefold() not in title_text]
        rows.append({"course_id": str(course.id), "course": course.title, "slug": course.slug, "published_course": course.published, "status": course.status, "technology": course.language.slug if course.language else None, "planned_topics": planned, "existing_entries": len(refs), "draft_entries": sum(row.status == "draft" for row in refs), "in_review_entries": sum(row.status in {"in_review", "changes_requested", "approved"} for row in refs), "published_entries": sum(row.status == "published" for row in refs), "archived_entries": sum(row.status == "archived" for row in refs), "incomplete_entries": incomplete, "missing_examples": missing_examples, "missing_topics": missing_topics, "english_complete_entries": sum(is_complete(row) for row in refs), "burmese_translation_entries": len(mm_ready), "lesson_links": len(linked), "data_source": "live database records"})
    print(json.dumps({"items": rows, "summary": {"courses": len(rows), "published_courses": sum(row["published_course"] for row in rows), "courses_with_entries": sum(bool(row["existing_entries"]) for row in rows), "published_entries": sum(row["published_entries"] for row in rows), "draft_entries": sum(row["draft_entries"] for row in rows), "incomplete_entries": sum(len(row["incomplete_entries"]) for row in rows), "burmese_translation_entries": sum(row["burmese_translation_entries"] for row in rows)}, "data_source": "live database records"}, indent=2, default=str, ensure_ascii=False))
    db.close()


if __name__ == "__main__":
    main()
