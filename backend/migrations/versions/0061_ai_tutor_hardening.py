"""Add course context, operational metrics, and versioned tutor prompts."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0061_ai_tutor_hardening"
down_revision = "0060_notification_management"
branch_labels = None
depends_on = None


def upgrade():
    u = postgresql.UUID(as_uuid=False)
    for table, columns in {
        "ai_conversations": [
            sa.Column("course_id", u, sa.ForeignKey("courses.id", ondelete="SET NULL"), nullable=True),
            sa.Column("module_id", u, sa.ForeignKey("course_modules.id", ondelete="SET NULL"), nullable=True),
            sa.Column("lesson_id", u, sa.ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True),
            sa.Column("language", sa.String(10), nullable=False, server_default="en"),
        ],
        "ai_usage_records": [
            sa.Column("latency_ms", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("error_code", sa.String(80), nullable=True),
        ],
        "ai_request_logs": [
            sa.Column("latency_ms", sa.Integer(), nullable=False, server_default="0"),
        ],
    }.items():
        for column in columns:
            op.add_column(table, column)
    op.create_index("ix_ai_conversations_course_id", "ai_conversations", ["course_id"])
    op.create_index("ix_ai_conversations_module_id", "ai_conversations", ["module_id"])
    op.create_index("ix_ai_conversations_lesson_id", "ai_conversations", ["lesson_id"])
    op.create_table(
        "ai_tutor_prompt_versions",
        sa.Column("id", u, primary_key=True),
        sa.Column("prompt_key", sa.String(80), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("system_prompt", sa.Text(), nullable=False),
        sa.Column("language", sa.String(10), nullable=False, server_default="en"),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("created_by", u, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("reviewed_by", u, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("activated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.UniqueConstraint("prompt_key", "version"),
    )
    op.create_index("ix_ai_tutor_prompts_status", "ai_tutor_prompt_versions", ["status"])


def downgrade():
    op.drop_index("ix_ai_tutor_prompts_status", table_name="ai_tutor_prompt_versions")
    op.drop_table("ai_tutor_prompt_versions")
    for name, table in (("ix_ai_conversations_lesson_id", "ai_conversations"), ("ix_ai_conversations_module_id", "ai_conversations"), ("ix_ai_conversations_course_id", "ai_conversations")):
        op.drop_index(name, table_name=table)
    for table, names in (("ai_request_logs", ["latency_ms"]), ("ai_usage_records", ["error_code", "latency_ms"]), ("ai_conversations", ["language", "lesson_id", "module_id", "course_id"])):
        for name in names:
            op.drop_column(table, name)
