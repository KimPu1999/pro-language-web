"""Evidence-based curriculum audit APIs for the admin quality center.

The audit is deliberately read-only. It reports what is present in the database
and never changes a published course or invents a completion percentage.
"""
import re
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from .auth import current_user, require_csrf
from .db import get_db
from .models import (
    Challenge,
    CodingExercise,
    ContentReviewEvent,
    ContentReviewItem,
    Course,
    CourseModule,
    Lesson,
    LessonQuiz,
    ProjectTemplate,
    QuizQuestion,
    SyntaxReference,
    User,
)
from .rbac import PLATFORM_ADMIN_ROLES


router = APIRouter(prefix="/api/v1/admin/curriculum-quality", tags=["curriculum-quality"])

LESSON_REQUIREMENTS = (
    ("learning_objectives", ("learning objectives", "objectives")),
    ("prerequisites", ("prerequisites", "before you start")),
    ("theory", ("detailed theory", "concept introduction", "theory")),
    ("syntax", ("syntax", "syntax explanation")),
    ("code_examples", ("code example", "working example")),
    ("expected_output", ("expected output", "expected behavior", "preview")),
    ("explanation", ("line-by-line", "step-by-step", "explanation")),
    ("common_mistakes", ("common mistakes", "pitfalls")),
    ("best_practices", ("best practices", "professional practices")),
    ("exercises", ("practical exercises", "exercise", "practice")),
    ("homework", ("homework", "assignment")),
    ("key_takeaways", ("key takeaways", "summary", "what you learned")),
    ("next_lesson", ("next lesson", "continue")),
)

BURMESE_TEXT = re.compile(r"[\u1000-\u109f]")

def _translation_state(value: str | None, source: str | None = None) -> str:
    translated = len(BURMESE_TEXT.findall(value or ""))
    if translated == 0:
        return "missing"
    source_length = len((source or "").strip())
    return "partial" if source_length and translated < max(20, source_length // 5) else "available"

TOPIC_EXPECTATIONS = {
    "c-programming": ("pointers", "memory management", "structures", "file handling", "data structures", "algorithms", "debugging"),
    "cpp-programming": ("classes", "templates", "stl", "memory", "concurrency", "testing"),
    "javascript": ("dom", "async", "promises", "fetch", "modules", "testing", "node"),
    "typescript": ("types", "generics", "modules", "async", "testing", "tooling"),
    "python": ("functions", "oop", "modules", "exceptions", "testing", "database", "api"),
    "python-for-ai": ("numpy", "pandas", "preprocessing", "classification", "clustering", "pytorch", "transformers", "testing", "deployment"),
    "react": ("components", "props", "state", "hooks", "routing", "data fetching", "testing", "performance"),
    "advanced-java": ("generics", "collections", "concurrency", "jvm", "io", "jdbc", "testing", "performance"),
    "spring-boot": ("foundations", "database", "security", "testing", "deployment", "validation", "transactions"),
    "java": ("classes", "collections", "exceptions", "testing", "build tools"),
    "html": ("semantic", "forms", "accessibility", "seo", "document structure"),
    "css": ("cascade", "selectors", "flexbox", "grid", "responsive", "animation", "accessibility"),
    "node-js": ("modules", "http", "async", "api", "testing", "security"),
    "machine-learning": ("numpy", "pandas", "preprocessing", "regression", "classification", "clustering", "evaluation", "pipelines", "monitoring", "deployment"),
    "express-js": ("routing", "middleware", "validation", "error handling", "testing", "security"),
    "fastapi": ("routing", "pydantic", "validation", "authentication", "testing", "database"),
    "django": ("routing", "templates", "models", "forms", "authentication", "testing", "security", "production"),
    "flutter": ("widgets", "layouts", "state", "navigation", "testing"),
    "dart": ("functions", "collections", "classes", "async", "testing"),
    "sql": ("select", "joins", "group", "transactions", "indexes", "security"),
    "docker": ("images", "containers", "volumes", "networks", "security", "production"),
    "git": ("commit", "branch", "merge", "rebase", "recovery", "workflow"),
    "linux": ("shell", "files", "processes", "permissions", "networking", "diagnostics"),
    "operating-systems": ("processes", "memory", "filesystems", "scheduling", "concurrency", "security"),
}


def _admin(user: User = Depends(current_user)) -> User:
    if user.role not in PLATFORM_ADMIN_ROLES:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Platform admin access required")
    return user

@router.get("/translation-coverage")
def translation_coverage(user: User = Depends(_admin), db: Session = Depends(get_db)):
    """Report stored Burmese coverage without treating English fallback as a translation."""
    courses = db.scalars(select(Course).options(selectinload(Course.modules).selectinload(CourseModule.lessons), selectinload(Course.syntax_references).selectinload(SyntaxReference.examples), selectinload(Course.syntax_references).selectinload(SyntaxReference.translations)).order_by(Course.title)).all()
    challenges = db.scalars(select(Challenge).order_by(Challenge.title)).all()
    projects = db.scalars(select(ProjectTemplate).order_by(ProjectTemplate.title)).all()
    items = []
    for course in courses:
        lessons = [lesson for module in course.modules for lesson in module.lessons]
        for lesson in lessons:
            state = _translation_state(lesson.content_mm, lesson.content_en)
            items.append({"source_type": "lesson", "source_id": str(lesson.id), "course_id": str(course.id), "title": lesson.title, "status": lesson.status, "published": lesson.published, "has_burmese": state == "available", "translation_state": state, "edit_url": f"/admin/courses/{course.id}/builder"})
        for reference in course.syntax_references:
            burmese = next((translation for translation in reference.translations if translation.locale == "my"), None)
            has_burmese = bool(burmese and burmese.status in {"approved", "published"} and burmese.title.strip() and burmese.description.strip())
            items.append({"source_type": "syntax_reference", "source_id": str(reference.id), "course_id": str(course.id), "title": reference.title, "status": reference.status, "published": reference.status == "published", "has_burmese": has_burmese, "translation_state": "available" if has_burmese else "missing", "edit_url": "/admin/syntax"})
    for challenge in challenges:
        state = _translation_state(challenge.description_mm, challenge.description)
        items.append({"source_type": "challenge", "source_id": str(challenge.id), "title": challenge.title, "status": challenge.status, "published": challenge.published, "has_burmese": state == "available", "translation_state": state, "edit_url": "/platform/challenges"})
    for project in projects:
        state = _translation_state(project.description_mm, project.description_en)
        items.append({"source_type": "project", "source_id": str(project.id), "title": project.title, "status": project.status, "published": project.published, "has_burmese": state == "available", "translation_state": state, "edit_url": "/admin/projects"})
    published = [item for item in items if item["published"]]
    return {"items": items, "summary": {"total": len(items), "available": sum(1 for item in items if item["has_burmese"]), "missing": sum(1 for item in items if not item["has_burmese"]), "published_total": len(published), "published_missing": sum(1 for item in published if not item["has_burmese"]), "data_source": "database"}}


@router.get("/translations")
def translations(user: User = Depends(_admin), db: Session = Depends(get_db)):
    """Compatibility alias for the existing Admin translations screen."""
    return translation_coverage(user=user, db=db)


def _tokens(course: Course) -> str:
    parts = [course.slug, course.title, getattr(course.language, "name", "")]
    modules = getattr(course, "modules", [])
    for module in modules:
        parts.append(module.title)
        for lesson in module.lessons:
            parts.extend([lesson.title, lesson.content_en or ""])
    return " ".join(parts).casefold()


def _topic_expectations(course: Course) -> list[str]:
    if course.slug in TOPIC_EXPECTATIONS:
        return list(TOPIC_EXPECTATIONS[course.slug])
    language = (getattr(course.language, "slug", "") or "").casefold()
    if language in {"python", "javascript", "java", "c", "cpp", "c-sharp", "go", "rust", "kotlin", "dart", "php"}:
        return ["fundamentals", "functions", "data structures", "error handling", "testing", "project"]
    if language in {"sql", "mongodb", "redis"}:
        return ["data modeling", "queries", "indexing", "transactions", "security", "project"]
    return ["fundamentals", "practical project", "testing", "security", "professional workflow"]


def _contains(text: str, options: tuple[str, ...]) -> bool:
    return any(re.search(rf"(?<![a-z]){re.escape(option)}(?![a-z])", text, re.I) for option in options)


def _lesson_sections(lesson: Lesson) -> dict[str, bool]:
    text = (lesson.content_en or "").casefold()
    return {key: bool(lesson.code_examples) if key == "code_examples" else _contains(text, options) for key, options in LESSON_REQUIREMENTS}


def _latest_review(db: Session, course: Course, review_cache: dict[str, dict] | None = None) -> dict | None:
    if review_cache is not None:
        return review_cache.get(str(course.id)) or review_cache.get(course.slug)
    row = db.scalar(select(ContentReviewItem).where(ContentReviewItem.content_type == "course", ContentReviewItem.content_key.in_((str(course.id), course.slug))).order_by(ContentReviewItem.version.desc(), ContentReviewItem.updated_at.desc()))
    if not row:
        return None
    return {"id": row.id, "status": row.status, "version": row.version, "updated_at": row.updated_at}


def _course_audit(db: Session, course: Course, detail: bool = False, context: dict | None = None) -> dict:
    modules = list(course.modules)
    lessons = [lesson for module in modules for lesson in module.lessons]
    lesson_ids = [lesson.id for lesson in lessons]
    quiz_counts = context["quiz_counts"] if context is not None else {}
    if lesson_ids and context is None:
        quiz_counts = {lesson_id: count for lesson_id, count in db.execute(select(LessonQuiz.lesson_id, func.count(QuizQuestion.id)).join(QuizQuestion, QuizQuestion.quiz_id == LessonQuiz.id).where(LessonQuiz.lesson_id.in_(lesson_ids)).group_by(LessonQuiz.lesson_id)).all()}
    exercise_counts = context["exercise_counts"] if context is not None else {}
    if lesson_ids and context is None:
        exercise_counts = {lesson_id: count for lesson_id, count in db.execute(select(CodingExercise.lesson_id, func.count(CodingExercise.id)).where(CodingExercise.lesson_id.in_(lesson_ids), CodingExercise.status != "archived").group_by(CodingExercise.lesson_id)).all()}
    missing_modules = [] if modules and [module.order_index for module in modules] == list(range(1, len(modules) + 1)) else ["Module ordering is missing or non-contiguous"]
    missing_lessons = []
    duplicate_slugs = []
    for module in modules:
        order = [lesson.order_index for lesson in module.lessons]
        if not module.lessons:
            missing_lessons.append(f"{module.title}: no lessons")
        elif order != list(range(1, len(order) + 1)):
            missing_lessons.append(f"{module.title}: lesson ordering is missing or non-contiguous")
        seen: set[str] = set()
        for lesson in module.lessons:
            if lesson.slug in seen:
                duplicate_slugs.append(lesson.slug)
            seen.add(lesson.slug)
    lesson_reports = []
    missing_lesson_sections = []
    no_examples = []
    no_quizzes = []
    no_exercises = []
    for lesson in lessons:
        sections = _lesson_sections(lesson)
        missing = [key for key, present in sections.items() if not present]
        if missing:
            missing_lesson_sections.append({"lesson_id": lesson.id, "title": lesson.title, "missing": missing})
        if not lesson.code_examples:
            no_examples.append(lesson.title)
        if not quiz_counts.get(lesson.id):
            no_quizzes.append(lesson.title)
        if not exercise_counts.get(lesson.id):
            no_exercises.append(lesson.title)
        if detail:
            lesson_reports.append({"id": lesson.id, "title": lesson.title, "slug": lesson.slug, "order_index": lesson.order_index, "published": lesson.published, "status": lesson.status, "content_length": len(lesson.content_en or ""), "code_examples": len(lesson.code_examples), "quiz_questions": quiz_counts.get(lesson.id, 0), "exercises": exercise_counts.get(lesson.id, 0), "missing_sections": missing})
    syntax = list(course.syntax_references)
    syntax_gaps = [{"id": item.id, "title": item.title, "status": item.status, "example_count": len(item.examples), "missing_examples": max(0, 5 - len(item.examples))} for item in syntax if item.status == "published" and len(item.examples) != 5]
    published_syntax = [item for item in syntax if item.status == "published"]
    published_projects = context["published_projects"] if context is not None else db.scalars(select(ProjectTemplate).where(ProjectTemplate.published.is_(True))).all()
    course_tokens = {course.slug.casefold(), course.title.casefold()}
    if getattr(course, "language", None):
        course_tokens.add(course.language.slug.casefold())
    matching_projects = [project for project in published_projects if any(token and token in (project.technology_stack or "").casefold() for token in course_tokens)]
    text = _tokens(course)
    level_coverage = {level: any(re.search(rf"\b{level}\b", f"{module.title} {(lesson.title if lesson else '')}".casefold()) for module in modules for lesson in (module.lessons or [None])) for level in ("beginner", "intermediate", "advanced", "professional")}
    missing_topics = [topic for topic in _topic_expectations(course) if topic.casefold() not in text]
    missing_course_metadata = []
    if not (course.description or "").strip(): missing_course_metadata.append("description")
    if not (course.outcomes or "").strip(): missing_course_metadata.append("learning_objectives")
    if not (course.requirements or "").strip(): missing_course_metadata.append("prerequisites")
    gaps = []
    if missing_course_metadata: gaps.append("incomplete_course_metadata")
    if not modules: gaps.append("missing_modules")
    if missing_modules: gaps.append("module_order")
    if missing_lessons: gaps.append("lesson_order_or_empty_module")
    if duplicate_slugs: gaps.append("duplicate_lesson_slugs")
    if missing_lesson_sections: gaps.append("incomplete_lesson_sections")
    if no_examples: gaps.append("missing_code_examples")
    if no_quizzes: gaps.append("missing_quizzes")
    if no_exercises: gaps.append("missing_exercises")
    if syntax_gaps: gaps.append("incomplete_published_syntax")
    if missing_topics: gaps.append("missing_expected_topics")
    review = _latest_review(db, course, context["reviews"] if context is not None else None)
    if gaps:
        audit_status = "published_with_gaps" if course.published else "draft_with_gaps"
    elif review and review["status"] in {"submitted", "in_review", "changes_requested"}:
        audit_status = "review_pending"
    else:
        audit_status = "ready_for_review" if not course.published else "published_ready_for_review"
    result = {
        "id": course.id, "title": course.title, "slug": course.slug, "description_length": len(course.description or ""), "learning_objectives": [item.strip() for item in (course.outcomes or "").split("|") if item.strip()], "prerequisites": course.requirements or "", "missing_course_metadata": missing_course_metadata, "technology": getattr(course.language, "name", None), "technology_slug": getattr(course.language, "slug", None), "course_level": course.level, "status": course.status, "published": course.published, "audit_status": audit_status,
        "module_count": len(modules), "lesson_count": len(lessons), "published_lesson_count": sum(1 for lesson in lessons if lesson.published), "missing_modules": missing_modules, "missing_lessons": missing_lessons, "duplicate_lesson_slugs": duplicate_slugs,
        "missing_lesson_sections": missing_lesson_sections, "missing_code_examples": no_examples, "missing_quizzes": no_quizzes, "missing_exercises": no_exercises, "syntax_reference_count": len(syntax), "published_syntax_reference_count": len(published_syntax), "syntax_gaps": syntax_gaps,
        "level_coverage": level_coverage, "missing_topics": missing_topics, "matching_published_projects": [{"id": project.id, "title": project.title, "slug": project.slug} for project in matching_projects], "project_linkage_note": "ProjectTemplate has no course_id, so matching projects are evidence only and are not treated as course completion.", "review": review,
        "gaps": gaps, "data_source": "live course, module, lesson, syntax, quiz, exercise, project, and review records",
    }
    if detail:
        result["lessons"] = lesson_reports
        result["modules"] = [{"id": module.id, "title": module.title, "order_index": module.order_index, "lesson_count": len(module.lessons)} for module in modules]
    return result


@router.get("/courses")
def quality_courses(
    technology: str | None = None,
    level: str | None = None,
    completeness: str | None = Query(default=None, alias="completeness", pattern=r"^(published_with_gaps|draft_with_gaps|review_pending|ready_for_review|published_ready_for_review)$"),
    review_status: str | None = Query(default=None, pattern=r"^(submitted|in_review|approved|changes_requested|rejected|none)$"),
    search: str | None = None,
    user: User = Depends(_admin),
    db: Session = Depends(get_db),
):
    query = select(Course).options(selectinload(Course.language), selectinload(Course.modules).selectinload(CourseModule.lessons).selectinload(Lesson.code_examples), selectinload(Course.syntax_references).selectinload(SyntaxReference.examples)).order_by(Course.title)
    if level: query = query.where(Course.level.ilike(level.strip()))
    if search: query = query.where(Course.title.ilike(f"%{search.strip()}%") | Course.slug.ilike(f"%{search.strip()}%"))
    courses = db.scalars(query).unique().all()
    lesson_ids = [lesson.id for course in courses for module in course.modules for lesson in module.lessons]
    quiz_counts = {}
    exercise_counts = {}
    if lesson_ids:
        quiz_counts = {lesson_id: count for lesson_id, count in db.execute(select(LessonQuiz.lesson_id, func.count(QuizQuestion.id)).join(QuizQuestion, QuizQuestion.quiz_id == LessonQuiz.id).where(LessonQuiz.lesson_id.in_(lesson_ids)).group_by(LessonQuiz.lesson_id)).all()}
        exercise_counts = {lesson_id: count for lesson_id, count in db.execute(select(CodingExercise.lesson_id, func.count(CodingExercise.id)).where(CodingExercise.lesson_id.in_(lesson_ids), CodingExercise.status != "archived").group_by(CodingExercise.lesson_id)).all()}
    published_projects = db.scalars(select(ProjectTemplate).where(ProjectTemplate.published.is_(True))).all()
    review_keys = [key for course in courses for key in (str(course.id), course.slug)]
    review_cache = {}
    if review_keys:
        review_rows = db.scalars(select(ContentReviewItem).where(ContentReviewItem.content_type == "course", ContentReviewItem.content_key.in_(review_keys)).order_by(ContentReviewItem.version.desc(), ContentReviewItem.updated_at.desc())).all()
        for row in review_rows:
            review_cache.setdefault(row.content_key, {"id": row.id, "status": row.status, "version": row.version, "updated_at": row.updated_at})
    audit_context = {"quiz_counts": quiz_counts, "exercise_counts": exercise_counts, "published_projects": published_projects, "reviews": review_cache}
    items = []
    for course in courses:
        item = _course_audit(db, course, context=audit_context)
        if technology and (item["technology_slug"] or "").casefold() != technology.casefold():
            continue
        if completeness and item["audit_status"] != completeness:
            continue
        current_review = item["review"]["status"] if item["review"] else "none"
        if review_status and current_review != review_status:
            continue
        items.append(item)
    counts = {}
    for item in items: counts[item["audit_status"]] = counts.get(item["audit_status"], 0) + 1
    published_items = [item for item in items if item["published"]]
    return {
        "items": items,
        "total": len(items),
        "counts": counts,
        "summary": {
            "courses": len(items),
            "published_courses": len(published_items),
            "courses_with_gaps": sum(1 for item in items if item["gaps"]),
            "review_pending": counts.get("review_pending", 0),
            "modules": sum(item["module_count"] for item in items),
            "lessons": sum(item["lesson_count"] for item in items),
            "published_lessons": sum(item["published_lesson_count"] for item in items),
            "syntax_references": sum(item["syntax_reference_count"] for item in items),
        },
        "data_source": "live database records",
    }


@router.get("/courses/{course_id}")
def quality_course(course_id: UUID, user: User = Depends(_admin), db: Session = Depends(get_db)):
    course = db.scalar(select(Course).options(selectinload(Course.language), selectinload(Course.modules).selectinload(CourseModule.lessons).selectinload(Lesson.code_examples), selectinload(Course.syntax_references).selectinload(SyntaxReference.examples)).where(Course.id == course_id))
    if not course: raise HTTPException(404, "Course not found")
    return _course_audit(db, course, detail=True)


@router.post("/courses/{course_id}/submit-review", status_code=201)
def submit_quality_review(course_id: UUID, user: User = Depends(_admin), _: None = Depends(require_csrf), db: Session = Depends(get_db)):
    course = db.get(Course, course_id)
    if not course: raise HTTPException(404, "Course not found")
    active = db.scalar(select(ContentReviewItem).where(ContentReviewItem.content_type == "course", ContentReviewItem.content_key == str(course.id), ContentReviewItem.status.in_(("submitted", "in_review"))))
    if active: return {"id": active.id, "status": active.status, "created": False}
    version = (db.scalar(select(func.max(ContentReviewItem.version)).where(ContentReviewItem.content_type == "course", ContentReviewItem.content_key == str(course.id))) or 0) + 1
    item = ContentReviewItem(content_type="course", content_key=str(course.id), title=course.title, submitted_by=user.id, version=version, status="submitted")
    db.add(item); db.flush(); db.add(ContentReviewEvent(review_item_id=item.id, actor_id=user.id, to_status="submitted", comment="Curriculum quality audit submitted for review.")); db.commit()
    return {"id": item.id, "status": item.status, "created": True}
