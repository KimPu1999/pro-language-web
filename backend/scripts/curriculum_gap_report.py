"""Export an evidence-based curriculum gap report from the configured database.

Usage:
    PYTHONPATH=. python scripts/curriculum_gap_report.py
    PYTHONPATH=. python scripts/curriculum_gap_report.py --json

The report intentionally contains counts and observed gaps only. It does not
derive a completion percentage or change publication state.
"""

import argparse
import json

from sqlalchemy import select

from app.curriculum_quality_routes import _course_audit
from app.db import SessionLocal
from app.models import Course


def main() -> None:
    parser = argparse.ArgumentParser(description="Export live course curriculum gaps")
    parser.add_argument("--json", action="store_true", dest="as_json", help="write machine-readable JSON")
    args = parser.parse_args()

    with SessionLocal() as db:
        courses = db.scalars(select(Course).order_by(Course.title)).all()
        report = [_course_audit(db, course) for course in courses]

    if args.as_json:
        print(json.dumps({"total_courses": len(report), "courses": report}, default=str, indent=2))
        return

    print("# Curriculum Gap Analysis")
    print()
    print(f"Courses audited from live database records: {len(report)}")
    print()
    for item in report:
        print(f"## {item['title']} ({item['slug']})")
        print(f"- Technology: {item['technology'] or 'not linked'}")
        print(f"- Status: {item['audit_status']}")
        print(f"- Modules: {item['module_count']}; lessons: {item['lesson_count']}; published lessons: {item['published_lesson_count']}")
        print(f"- Evidence gap categories: {', '.join(item['gaps']) or 'none observed'}")
        print(f"- Missing topics: {', '.join(item['missing_topics']) or 'none observed'}")
        print(f"- Missing lesson sections: {len(item['missing_lesson_sections'])}")
        print(f"- Missing quizzes: {len(item['missing_quizzes'])}; exercises: {len(item['missing_exercises'])}")
        print(f"- Published syntax references with a count other than five: {len(item['syntax_gaps'])}")
        print(f"- Review status: {item['review']['status'] if item['review'] else 'none'}")
        print()


if __name__ == "__main__":
    main()
