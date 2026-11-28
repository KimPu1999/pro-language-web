"""Read-only Phase 01 audit for every Learn-Coding course.

This command only reads PostgreSQL and writes an audit artifact when
``--output`` is provided. It never creates, updates, publishes, archives, or
deletes course data.

Run from ``backend``::

    PYTHONPATH=. .venv/bin/python scripts/phase01_course_audit.py --output reports/phase01-course-audit.json
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.curriculum_quality_routes import TOPIC_EXPECTATIONS, _course_audit
from app.db import SessionLocal
from app.models import (
    CodeExample,
    CodingExercise,
    Course,
    CourseModule,
    Lesson,
    LessonQuiz,
    ProjectCourseLink,
    ProjectTemplate,
    QuizQuestion,
)


BURMESE = re.compile(r"[\u1000-\u109f]")

SECTION_ALIASES = {
    "introduction": ("introduction", "overview"),
    "learning_objectives": ("learning objectives", "objectives"),
    "prerequisites": ("prerequisites", "before you start"),
    "detailed_theory": ("detailed theory", "complete theory", "theory", "concept introduction"),
    "core_concepts": ("core concepts", "main concepts", "architecture explanation"),
    "syntax_api": ("syntax", "syntax / api", "syntax explanation", "file path and code"),
    "code_examples": ("code example", "working example", "practical examples", "step-by-step example"),
    "expected_output": ("expected output", "expected behavior", "preview"),
    "explanation": ("line-by-line explanation", "step-by-step explanation", "code explanation", "command explanation", "explanation"),
    "common_mistakes": ("common mistakes", "pitfalls"),
    "best_practices": ("best practices", "professional practices"),
    "exercises": ("practical exercises", "practice exercises", "hands-on exercise", "exercises", "exercise"),
    "homework": ("homework", "assignment"),
    "quiz": ("quiz", "knowledge quiz", "assessment"),
    "mini_project": ("mini project", "project"),
    "summary": ("lesson summary", "summary", "key takeaways", "what you learned"),
}

LEVEL_PATTERNS = {
    "beginner": ("beginner", "fundamentals", "foundations", "introduction", "basics", "getting started", "from zero"),
    "intermediate": ("intermediate", "core", "practical", "applied", "working with"),
    "advanced": ("advanced", "optimization", "performance", "scaling", "architecture", "security"),
    "professional": ("professional", "production", "deployment", "enterprise", "capstone", "operations", "mlops"),
}


def _translation_state(value: str | None, source: str | None = None) -> str:
    count = len(BURMESE.findall(value or ""))
    if count == 0:
        return "missing"
    source_length = len((source or "").strip())
    return "partial" if source_length and count < max(20, source_length // 5) else "complete"


def _heading_blocks(content: str | None) -> dict[str, str]:
    """Return non-empty text after recognizable headings.

    The audit accepts both Markdown headings and the legacy plain-text
    headings used by older seeded lessons. A heading with no substantive body
    is not counted as complete.
    """
    lines = (content or "").splitlines()
    normalized = [(index, line.strip().lstrip("#").strip().casefold()) for index, line in enumerate(lines)]
    found: dict[str, str] = {}
    for key, aliases in SECTION_ALIASES.items():
        for index, line in normalized:
            if line in aliases:
                next_heading = len(lines)
                for candidate_index in range(index + 1, len(lines)):
                    candidate = lines[candidate_index].strip()
                    if candidate.startswith("#") or candidate.casefold() in {item for values in SECTION_ALIASES.values() for item in values}:
                        next_heading = candidate_index
                        break
                body = "\n".join(lines[index + 1:next_heading]).strip()
                if len(body) >= 12:
                    found[key] = body
                break
    return found


def _lesson_missing_sections(lesson: Lesson) -> list[str]:
    blocks = _heading_blocks(lesson.content_en)
    required = [key for key in SECTION_ALIASES if key != "mini_project"]
    return [key for key in required if key not in blocks]


def _level_evidence(course: Course) -> dict[str, list[str]]:
    evidence: dict[str, list[str]] = {level: [] for level in LEVEL_PATTERNS}
    for module in course.modules:
        module_text = f"{module.title} " + " ".join(lesson.title for lesson in module.lessons)
        folded = module_text.casefold()
        for level, patterns in LEVEL_PATTERNS.items():
            if any(re.search(rf"(?<![a-z]){re.escape(pattern)}(?![a-z])", folded) for pattern in patterns):
                evidence[level].append(module.title)
    return evidence


def _primary_classification(course: Course, item: dict[str, Any]) -> str:
    if item["status"] == "archived":
        return "Missing Curriculum" if item["lesson_count"] == 0 else "Partially Complete"
    if item["module_count"] == 0 or item["lesson_count"] == 0:
        return "Missing Curriculum"
    if item["module_count"] <= 1 and item["lesson_count"] <= 10:
        return "Introduction Only"
    if item["technical_repairs"]:
        return "Needs Technical Repair"
    if item["mm_completeness"] != "Complete":
        return "Missing Translations"
    if item["strict_complete"]:
        return "Complete"
    return "Partially Complete"


def _priority(item: dict[str, Any]) -> int | None:
    if item["status"] == "archived":
        return None
    if item["classification"] in {"Missing Curriculum", "Introduction Only"}:
        return 1
    missing_levels = set(item["missing_levels"])
    if missing_levels.intersection({"intermediate", "advanced", "professional"}):
        return 2
    if item["technical_repairs"] or item["empty_lesson_count"]:
        return 3
    if item["missing_assessment_or_reference"]:
        return 4
    if item["mm_completeness"] != "Complete":
        return 5
    return 5


def audit() -> dict[str, Any]:
    with SessionLocal() as db:
        courses = db.scalars(
            select(Course)
            .options(selectinload(Course.modules).selectinload(CourseModule.lessons), selectinload(Course.language), selectinload(Course.syntax_references))
            .order_by(Course.title, Course.slug)
        ).all()
        all_lessons = [lesson for course in courses for module in course.modules for lesson in module.lessons]
        lesson_ids = [lesson.id for lesson in all_lessons]
        quiz_ids = db.scalars(select(LessonQuiz.lesson_id)).all()
        exercise_rows = db.scalars(select(CodingExercise).where(CodingExercise.status != "archived")).all()
        example_rows = db.scalars(select(CodeExample)).all()
        linked_projects = db.execute(select(ProjectCourseLink.course_id, ProjectCourseLink.project_id)).all()
        published_projects = {row.id for row in db.scalars(select(ProjectTemplate).where(ProjectTemplate.published.is_(True))).all()}
        quiz_by_lesson = Counter(quiz_ids)
        exercise_by_lesson = Counter(row.lesson_id for row in exercise_rows)
        example_by_lesson = Counter(row.lesson_id for row in example_rows)
        project_by_course: dict[Any, set[Any]] = defaultdict(set)
        for course_id, project_id in linked_projects:
            if project_id in published_projects:
                project_by_course[course_id].add(project_id)

        rows: list[dict[str, Any]] = []
        for course in courses:
            modules = list(course.modules)
            lessons = [lesson for module in modules for lesson in module.lessons]
            audit_result = _course_audit(db, course)
            missing_sections = Counter(section for lesson in lessons for section in _lesson_missing_sections(lesson))
            en_complete = sum(not _lesson_missing_sections(lesson) and bool((lesson.content_en or "").strip()) for lesson in lessons)
            mm_states = Counter(_translation_state(lesson.content_mm, lesson.content_en) for lesson in lessons)
            level_evidence = _level_evidence(course)
            missing_levels = [level for level, evidence in level_evidence.items() if not evidence]
            linked_project_count = len(project_by_course.get(course.id, set()))
            missing_assessment_or_reference = (
                len(lessons) > 0 and (
                    sum(quiz_by_lesson[lesson.id] > 0 for lesson in lessons) < len(lessons)
                    or sum(exercise_by_lesson[lesson.id] > 0 for lesson in lessons) < len(lessons)
                    or linked_project_count == 0
                    or len(course.syntax_references) == 0
                )
            )
            technical_repairs = sorted(set(audit_result["gaps"]).intersection({"module_order", "lesson_order_or_empty_module", "duplicate_lesson_slugs", "missing_code_examples", "missing_quizzes"}))
            strict_complete = bool(lessons) and not audit_result["gaps"] and not missing_levels and en_complete == len(lessons) and mm_states["complete"] == len(lessons) and linked_project_count > 0 and all(quiz_by_lesson[lesson.id] for lesson in lessons) and all(exercise_by_lesson[lesson.id] for lesson in lessons) and bool(course.syntax_references)
            item: dict[str, Any] = {
                "course_id": str(course.id),
                "slug": course.slug,
                "course": course.title,
                "status": course.status,
                "published_course": bool(course.published),
                "module_count": len(modules),
                "lesson_count": len(lessons),
                "published_lesson_count": sum(bool(lesson.published) for lesson in lessons),
                "draft_lesson_count": sum(not bool(lesson.published) for lesson in lessons),
                "empty_lesson_count": sum(not (lesson.content_en or "").strip() for lesson in lessons),
                "english_complete_count": int(en_complete),
                "english_completeness": "Complete" if en_complete == len(lessons) and lessons else "Partial" if en_complete else "Missing",
                "burmese_complete_count": mm_states["complete"],
                "burmese_partial_count": mm_states["partial"],
                "burmese_missing_count": mm_states["missing"],
                "mm_completeness": "Complete" if mm_states["complete"] == len(lessons) and lessons else "Partial" if mm_states["complete"] or mm_states["partial"] else "Missing",
                "exercise_count": sum(exercise_by_lesson[lesson.id] for lesson in lessons),
                "quiz_count": sum(quiz_by_lesson[lesson.id] for lesson in lessons),
                "code_example_count": sum(example_by_lesson[lesson.id] for lesson in lessons),
                "published_project_count": linked_project_count,
                "syntax_reference_count": len(course.syntax_references),
                "level_evidence": level_evidence,
                "missing_levels": missing_levels,
                "missing_lesson_sections": dict(missing_sections),
                "missing_topics": audit_result["missing_topics"],
                "audit_gaps": audit_result["gaps"],
                "technical_repairs": technical_repairs,
                "missing_assessment_or_reference": missing_assessment_or_reference,
                "strict_complete": strict_complete,
                "publication_status": {"course_status": course.status, "course_published": bool(course.published), "published_lessons": sum(bool(lesson.published) for lesson in lessons), "draft_lessons": sum(not bool(lesson.published) for lesson in lessons), "quality_audit": audit_result["audit_status"]},
            }
            item["classification"] = _primary_classification(course, item)
            item["recommended_priority"] = _priority(item)
            rows.append(item)

        active = [row for row in rows if row["status"] != "archived"]
        first = sorted((row for row in active if row["recommended_priority"] is not None), key=lambda row: (row["recommended_priority"], row["course"]))[0]
        plan_modules: list[str] = []
        if first["slug"] == "docker":
            from app.docker_course_content import PLANNED_MODULES

            plan_modules = list(PLANNED_MODULES[1:])
        first["recommended_plan"] = {
            "preserve": ["course/module/lesson IDs", "published Module 1 content", "lesson progress, enrollments, quiz attempts, and project submissions", "existing EN/MM content and publication versions"],
            "missing_modules": plan_modules,
            "required_content_per_lesson": ["Introduction", "Learning objectives", "Prerequisites", "Detailed theory", "Core concepts", "Syntax/API usage", "Code examples", "Expected output", "Step-by-step explanation", "Common mistakes", "Best practices", "Exercises", "Homework", "Quiz", "Mini project where applicable", "Lesson summary"],
            "required_assessments": ["one practical exercise per substantive lesson", "one quiz with answer explanations per lesson", "at least one linked published project after review", "syntax references linked to relevant lessons"],
            "translation_gaps": {"english": first["english_completeness"], "burmese": first["mm_completeness"], "lesson_level": first["missing_levels"]},
            "recommended_batches": ["Batch 1: Module 2-5 foundations and runtime/CLI labs", "Batch 2: Module 6-12 images, Dockerfiles, networking, storage, Compose, and security", "Batch 3: production, CI/CD, Kubernetes, troubleshooting, projects, and capstone", "Review EN/MM, assessments, syntax links, project links, then submit for publication review"],
        }
        summary = {
            "total_courses": len(rows),
            "published_courses": sum(row["published_course"] for row in rows),
            "draft_courses": sum(row["status"] == "draft" for row in rows),
            "archived_courses": sum(row["status"] == "archived" for row in rows),
            "complete_courses": [row["slug"] for row in active if row["classification"] == "Complete"],
            "partially_complete_courses": [row["slug"] for row in active if row["classification"] == "Partially Complete"],
            "introduction_only_courses": [row["slug"] for row in active if row["classification"] == "Introduction Only"],
            "missing_curriculum_courses": [row["slug"] for row in active if row["classification"] == "Missing Curriculum"],
            "archived_empty_records": [row["slug"] for row in rows if row["status"] == "archived" and row["lesson_count"] == 0],
            "missing_translation_courses": [row["slug"] for row in active if row["classification"] == "Missing Translations"],
            "technical_repair_courses": [row["slug"] for row in active if row["classification"] == "Needs Technical Repair"],
            "priority_1": [row["slug"] for row in active if row["recommended_priority"] == 1],
            "priority_2": [row["slug"] for row in active if row["recommended_priority"] == 2],
            "priority_3": [row["slug"] for row in active if row["recommended_priority"] == 3],
            "priority_4": [row["slug"] for row in active if row["recommended_priority"] == 4],
            "priority_5": [row["slug"] for row in active if row["recommended_priority"] == 5],
            "first_incomplete_course": first["slug"],
            "criteria": {"complete_requires": "all four level evidence groups, substantive EN/MM lessons, no audit gaps, per-lesson quizzes/exercises, syntax references, and at least one published course-linked project", "translation_policy": "only persisted Burmese lesson content counts; empty or English fallback is not complete", "project_policy": "only published ProjectCourseLink records count; technology-stack text alone is not treated as a course project link"},
        }
        return {"phase": "01", "mode": "audit_only", "data_source": "live PostgreSQL", "summary": summary, "first_course_plan": first["recommended_plan"], "courses": rows}


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only Phase 01 course and lesson audit")
    parser.add_argument("--output", type=Path, help="write JSON report to this path; PostgreSQL remains read-only")
    args = parser.parse_args()
    report = audit()
    payload = json.dumps(report, ensure_ascii=False, indent=2, default=str)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
