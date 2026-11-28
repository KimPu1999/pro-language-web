"""Keep curriculum authoring drafts separate from published lessons.

This migration is additive. It does not alter existing lesson, quiz, progress,
or submission rows; a reviewer can later promote a draft through the existing
content-review workflow.
"""
from alembic import op
import sqlalchemy as sa

revision = "0073_curriculum_draft_versions"
down_revision = "0072_syntax_reference_library"
branch_labels = None
depends_on = None


def _uuid():
    return sa.UUID()


def upgrade():
    op.create_table(
        "lesson_content_drafts",
        sa.Column("id", _uuid(), nullable=False),
        sa.Column("lesson_id", _uuid(), nullable=False),
        sa.Column("base_content_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("draft_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("slug", sa.String(180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("content_en", sa.Text(), nullable=False, server_default=""),
        sa.Column("content_mm", sa.Text(), nullable=True),
        sa.Column("duration_minutes", sa.Integer(), nullable=False, server_default="10"),
        sa.Column("status", sa.String(30), nullable=False, server_default="draft"),
        sa.Column("change_summary", sa.String(240), nullable=False, server_default=""),
        sa.Column("created_by", _uuid(), nullable=True),
        sa.Column("updated_by", _uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lesson_id"),
    )
    op.create_index("ix_lesson_content_drafts_lesson_id", "lesson_content_drafts", ["lesson_id"])
    op.create_index("ix_lesson_content_drafts_status_updated", "lesson_content_drafts", ["status", "updated_at"])

    op.create_table(
        "module_quiz_drafts",
        sa.Column("id", _uuid(), nullable=False),
        sa.Column("module_id", _uuid(), nullable=False),
        sa.Column("title_en", sa.String(180), nullable=False),
        sa.Column("title_mm", sa.String(180), nullable=False, server_default=""),
        sa.Column("questions_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("pass_percent", sa.Integer(), nullable=False, server_default="70"),
        sa.Column("status", sa.String(30), nullable=False, server_default="draft"),
        sa.Column("draft_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_by", _uuid(), nullable=True),
        sa.Column("updated_by", _uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["module_id"], ["course_modules.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["updated_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("module_id"),
    )
    op.create_index("ix_module_quiz_drafts_module_id", "module_quiz_drafts", ["module_id"])
    op.create_index("ix_module_quiz_drafts_status_updated", "module_quiz_drafts", ["status", "updated_at"])


def downgrade():
    op.drop_index("ix_module_quiz_drafts_status_updated", table_name="module_quiz_drafts")
    op.drop_index("ix_module_quiz_drafts_module_id", table_name="module_quiz_drafts")
    op.drop_table("module_quiz_drafts")
    op.drop_index("ix_lesson_content_drafts_status_updated", table_name="lesson_content_drafts")
    op.drop_index("ix_lesson_content_drafts_lesson_id", table_name="lesson_content_drafts")
    op.drop_table("lesson_content_drafts")
