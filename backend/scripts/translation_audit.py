"""Read-only translation coverage audit for Learn-Coding.

This command intentionally never writes to PostgreSQL. It combines persisted
content coverage with a conservative source scan so missing translations are
reported instead of being mistaken for completed Burmese content.

Run from ``backend``:
    PYTHONPATH=. .venv/bin/python scripts/translation_audit.py --json
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.db import SessionLocal
from app.models import Challenge, CodingExercise, Course, CourseModule, Lesson, LessonQuiz, ProjectTemplate, QuizQuestion, SyntaxReference


ROOT = Path(__file__).resolve().parents[2]
FRONTEND_ROOTS = (ROOT / "frontend", ROOT / "apps" / "platform", ROOT / "apps" / "admin")
BURMESE_TEXT = re.compile(r"[\u1000-\u109f]")

def translation_state(value: str | None, source: str | None = None) -> str:
    translated = len(BURMESE_TEXT.findall(value or ""))
    if translated == 0:
        return "missing"
    source_length = len((source or "").strip())
    return "partial" if source_length and translated < max(20, source_length // 5) else "available"


def _non_generated_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file() or any(part in {"node_modules", ".next", ".next-dev"} or part.endswith("tsbuildinfo") for part in path.parts):
            continue
        if path.suffix in {".ts", ".tsx", ".js", ".jsx"}:
            yield path


def source_audit() -> dict[str, Any]:
    files = list(path for root in FRONTEND_ROOTS for path in _non_generated_files(root))
    page_files = [path for path in files if path.name == "page.tsx"]
    hardcoded = []
    pattern = re.compile(r">\s*([A-Z][^<{\n]{2,})<")
    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        for match in pattern.finditer(text):
            value = " ".join(match.group(1).split())
            if value and not value.startswith(("http", "©")):
                hardcoded.append({"file": str(path.relative_to(ROOT)), "text": value[:120]})
    i18n_path = ROOT / "frontend" / "lib" / "i18n.tsx"
    i18n_text = i18n_path.read_text(encoding="utf-8")
    blocks = {}
    for locale in ("en", "my"):
        match = re.search(rf"\b{locale}: \{{(.*?)\n\s*\}},", i18n_text, re.S)
        blocks[locale] = set(re.findall(r"(?:^|,\s*)([A-Za-z][A-Za-z0-9_]*)\s*:", match.group(1))) if match else set()
    return {
        "routes": {str(root.relative_to(ROOT)): sum(1 for path in page_files if root in path.parents) for root in FRONTEND_ROOTS},
        "source_files_scanned": len(files),
        "hardcoded_ui_candidates": len(hardcoded),
        "hardcoded_ui_sample": hardcoded[:50],
        "dictionary": {"en_keys": len(blocks["en"]), "my_keys": len(blocks["my"]), "missing_my_keys": sorted(blocks["en"] - blocks["my"]), "duplicate_keys": []},
    }


def database_audit() -> dict[str, Any]:
    with SessionLocal() as db:
        courses = db.scalars(select(Course).options(selectinload(Course.modules).selectinload(CourseModule.lessons))).all()
        modules = db.scalar(select(func.count(CourseModule.id))) or 0
        lessons = db.scalars(select(Lesson)).all()
        challenges = db.scalars(select(Challenge)).all()
        projects = db.scalars(select(ProjectTemplate)).all()
        syntax_references = db.scalars(select(SyntaxReference)).all()
        exercises = db.scalars(select(CodingExercise)).all()
        quizzes = db.scalars(select(LessonQuiz)).all()
        questions = db.scalar(select(func.count(QuizQuestion.id))) or 0

        def count_field(rows, field: str) -> int:
            return sum(translation_state(getattr(row, field, None)) == "available" for row in rows)

        published_lessons = [row for row in lessons if row.published]
        published_challenges = [row for row in challenges if row.published]
        published_projects = [row for row in projects if row.published]
        lesson_rows = []
        for course in courses:
            for module in course.modules:
                for lesson in module.lessons:
                    state = translation_state(lesson.content_mm, lesson.content_en)
                    lesson_rows.append({"course_id": str(course.id), "course_slug": course.slug, "course_title": course.title, "level": course.level, "module_id": str(module.id), "module_title": module.title, "lesson_id": str(lesson.id), "lesson_slug": lesson.slug, "title": lesson.title, "published": lesson.published, "status": lesson.status, "translation_state": state, "english_characters": len((lesson.content_en or "").strip()), "burmese_characters": len(BURMESE_TEXT.findall(lesson.content_mm or ""))})
        published_lesson_rows = [row for row in lesson_rows if row["published"]]
        return {
            "courses": {"total": len(courses), "published": sum(row.published for row in courses), "slugs": sorted(row.slug for row in courses)},
            "modules": {"total": modules},
            "lessons": {"total": len(lessons), "published": len(published_lessons), "available": sum(row["translation_state"] == "available" for row in lesson_rows), "partial": sum(row["translation_state"] == "partial" for row in lesson_rows), "missing": sum(row["translation_state"] == "missing" for row in lesson_rows), "published_available": sum(row["translation_state"] == "available" for row in published_lesson_rows), "published_partial": sum(row["translation_state"] == "partial" for row in published_lesson_rows), "published_missing": sum(row["translation_state"] == "missing" for row in published_lesson_rows)},
            "lesson_gaps": [row for row in lesson_rows if row["translation_state"] != "available"],
            "challenges": {"total": len(challenges), "published": len(published_challenges), "burmese_description": count_field(challenges, "description_mm"), "published_burmese_description": count_field(published_challenges, "description_mm")},
            "projects": {"total": len(projects), "published": len(published_projects), "burmese_description": count_field(projects, "description_mm"), "published_burmese_description": count_field(published_projects, "description_mm")},
            "syntax_references": {"total": len(syntax_references), "published": sum(row.status == "published" for row in syntax_references), "bilingual_fields": False},
            "exercises": {"total": len(exercises), "burmese_description": count_field(exercises, "description_mm")},
            "quizzes": {"total": len(quizzes), "questions": questions, "bilingual_fields": False},
            "policy": "Only persisted Burmese fields count. English fallback and unpublished drafts are excluded from completion.",
        }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = {"source": source_audit(), "database": database_audit()}
    payload = json.dumps(report, ensure_ascii=False, indent=2) if args.as_json or args.output else json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
