"""Add project learning reader content and bookmarks.

This migration only adds nullable/defaulted columns and a new table; existing
project templates, milestones, enrollments, and progress are preserved.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0026_project_learning_content"
down_revision = "0025_learning_path_bookmarks"
branch_labels = None
depends_on = None


def upgrade() -> None:
    for name in ("technology_stack", "prerequisites", "architecture_overview", "folder_structure", "testing_guide", "deployment_guide"):
        op.add_column("project_templates", sa.Column(name, sa.Text(), nullable=False, server_default=""))
    op.add_column("project_milestones", sa.Column("slug", sa.String(180), nullable=False, server_default=""))
    op.add_column("project_milestones", sa.Column("content_en", sa.Text(), nullable=False, server_default=""))
    op.add_column("project_milestones", sa.Column("content_mm", sa.Text(), nullable=True))
    op.add_column("project_milestones", sa.Column("code", sa.Text(), nullable=False, server_default=""))
    op.add_column("project_milestones", sa.Column("filename", sa.String(180), nullable=True))
    op.add_column("project_milestones", sa.Column("expected_output", sa.Text(), nullable=False, server_default=""))
    op.add_column("project_milestones", sa.Column("line_explanation", sa.Text(), nullable=False, server_default=""))
    op.create_table(
        "project_bookmarks",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("project_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("project_templates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "project_id", name="uq_project_bookmarks_user_project"),
    )
    op.create_index("ix_project_bookmarks_user_id", "project_bookmarks", ["user_id"])
    op.create_index("ix_project_bookmarks_project_id", "project_bookmarks", ["project_id"])


def downgrade() -> None:
    op.drop_index("ix_project_bookmarks_project_id", table_name="project_bookmarks")
    op.drop_index("ix_project_bookmarks_user_id", table_name="project_bookmarks")
    op.drop_table("project_bookmarks")
    for name in ("line_explanation", "expected_output", "filename", "code", "content_mm", "content_en", "slug"):
        op.drop_column("project_milestones", name)
    for name in ("deployment_guide", "testing_guide", "folder_structure", "architecture_overview", "prerequisites", "technology_stack"):
        op.drop_column("project_templates", name)
