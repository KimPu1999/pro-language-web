"""Add lesson editor versioning metadata and revision history.

This migration is additive. Existing lesson IDs, content, enrollments and
progress rows remain unchanged.
"""
from alembic import op
import sqlalchemy as sa

revision = "0047_course_builder_revisions"
down_revision = "0046_developer_tools_catalog"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("lessons", sa.Column("content_version", sa.Integer(), nullable=False, server_default="1"))
    uuid = sa.UUID()
    op.create_table(
        "lesson_revisions",
        sa.Column("id", uuid, nullable=False),
        sa.Column("lesson_id", uuid, nullable=False),
        sa.Column("changed_by", uuid, nullable=False),
        sa.Column("revision_number", sa.Integer(), nullable=False),
        sa.Column("content_snapshot", sa.Text(), nullable=False),
        sa.Column("change_summary", sa.String(length=240), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["changed_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lesson_id", "revision_number"),
    )
    op.create_index("ix_lesson_revisions_lesson_created", "lesson_revisions", ["lesson_id", "created_at"])


def downgrade():
    op.drop_index("ix_lesson_revisions_lesson_created", table_name="lesson_revisions")
    op.drop_table("lesson_revisions")
    op.drop_column("lessons", "content_version")
