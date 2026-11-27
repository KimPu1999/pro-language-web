"""Add project version snapshots and canonical course/path links.

The migration is additive. Existing projects, submissions, reviews and grades
remain intact; links are optional and versions are created by later edits.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0065_project_workflow_links"
down_revision = "0064_community_core_hardening"
branch_labels = None
depends_on = None


def upgrade():
    uuid = postgresql.UUID(as_uuid=False)
    op.create_table(
        "project_versions",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("project_id", uuid, sa.ForeignKey("project_templates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("snapshot_json", sa.Text(), nullable=False),
        sa.Column("created_by", uuid, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("project_id", "version"),
    )
    op.create_index("ix_project_versions_project_created", "project_versions", ["project_id", "created_at"])
    op.create_table(
        "project_course_links",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("project_id", uuid, sa.ForeignKey("project_templates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("course_id", uuid, sa.ForeignKey("courses.id", ondelete="CASCADE"), nullable=False),
        sa.Column("module_id", uuid, sa.ForeignKey("course_modules.id", ondelete="CASCADE"), nullable=True),
        sa.Column("lesson_id", uuid, sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("project_id", "course_id", "module_id", "lesson_id"),
    )
    op.create_index("ix_project_course_links_project_position", "project_course_links", ["project_id", "position"])
    op.create_table(
        "project_path_links",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("project_id", uuid, sa.ForeignKey("project_templates.id", ondelete="CASCADE"), nullable=False),
        sa.Column("roadmap_id", uuid, sa.ForeignKey("career_roadmaps.id", ondelete="CASCADE"), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("project_id", "roadmap_id"),
    )
    op.create_index("ix_project_path_links_project_position", "project_path_links", ["project_id", "position"])


def downgrade():
    op.drop_index("ix_project_path_links_project_position", table_name="project_path_links")
    op.drop_table("project_path_links")
    op.drop_index("ix_project_course_links_project_position", table_name="project_course_links")
    op.drop_table("project_course_links")
    op.drop_index("ix_project_versions_project_created", table_name="project_versions")
    op.drop_table("project_versions")
