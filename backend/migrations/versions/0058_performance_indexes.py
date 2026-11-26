"""Add indexes for the measured course, progress, and dashboard access paths."""

from alembic import op


revision = "0058_performance_indexes"
down_revision = "0057_personal_notebook"
branch_labels = None
depends_on = None


def upgrade():
    # The live schema predates several ORM constraints, so these are explicit
    # non-unique indexes and remain safe additive changes for existing rows.
    indexes = {
        "courses": (
            ("ix_courses_published_title", ["published", "title"]),
        ),
        "course_modules": (
            ("ix_course_modules_course_order", ["course_id", "order_index"]),
        ),
        "lessons": (
            ("ix_lessons_module_published_order", ["module_id", "published", "order_index"]),
        ),
        "enrollments": (
            ("ix_enrollments_user_course", ["user_id", "course_id"]),
        ),
        "lesson_progress": (
            ("ix_lesson_progress_user_lesson", ["user_id", "lesson_id"]),
            ("ix_lesson_progress_user_completed_visited", ["user_id", "completed", "last_visited_at"]),
        ),
        "quiz_attempts": (
            ("ix_quiz_attempts_user_created", ["user_id", "created_at"]),
        ),
    }
    for table, table_indexes in indexes.items():
        for name, columns in table_indexes:
            op.create_index(name, table, columns)


def downgrade():
    for name, table in (
        ("ix_quiz_attempts_user_created", "quiz_attempts"),
        ("ix_lesson_progress_user_completed_visited", "lesson_progress"),
        ("ix_lesson_progress_user_lesson", "lesson_progress"),
        ("ix_enrollments_user_course", "enrollments"),
        ("ix_lessons_module_published_order", "lessons"),
        ("ix_course_modules_course_order", "course_modules"),
        ("ix_courses_published_title", "courses"),
    ):
        op.drop_index(name, table_name=table)
