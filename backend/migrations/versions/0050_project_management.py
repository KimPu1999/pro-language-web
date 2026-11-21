"""Add structured project management content without changing existing records.

All additions are nullable or have safe defaults. Existing project, student,
submission and review identifiers remain unchanged.
"""
from alembic import op
import sqlalchemy as sa

revision = "0050_project_management"
down_revision = "0049_challenge_display_order"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("project_templates", sa.Column("cover_image", sa.String(length=500), nullable=True))
    op.add_column("project_templates", sa.Column("tags_json", sa.Text(), nullable=False, server_default="[]"))
    op.add_column("project_templates", sa.Column("languages_json", sa.Text(), nullable=False, server_default="[]"))
    op.add_column("project_templates", sa.Column("brief_json", sa.Text(), nullable=False, server_default="{}"))
    op.add_column("project_milestones", sa.Column("completion_criteria", sa.Text(), nullable=False, server_default=""))
    op.add_column("project_milestones", sa.Column("resources_json", sa.Text(), nullable=False, server_default="[]"))
    op.add_column("project_rubric_criteria", sa.Column("description", sa.Text(), nullable=False, server_default=""))
    op.add_column("project_submissions", sa.Column("attachment_key", sa.String(length=500), nullable=True))
    op.add_column("project_submissions", sa.Column("attachment_name", sa.String(length=240), nullable=True))
    op.add_column("project_submissions", sa.Column("attachment_size", sa.Integer(), nullable=True))
    uuid = sa.UUID()
    op.create_table(
        "project_requirements",
        sa.Column("id", uuid, nullable=False),
        sa.Column("project_id", uuid, nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("acceptance_criteria", sa.Text(), nullable=False, server_default=""),
        sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project_templates.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("project_id", "position"),
    )
    op.create_table(
        "project_tasks",
        sa.Column("id", uuid, nullable=False),
        sa.Column("milestone_id", uuid, nullable=False),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("completion_criteria", sa.Text(), nullable=False, server_default=""),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["milestone_id"], ["project_milestones.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("milestone_id", "position"),
    )
    op.create_table(
        "project_resources",
        sa.Column("id", uuid, nullable=False),
        sa.Column("project_id", uuid, nullable=False),
        sa.Column("milestone_id", uuid, nullable=True),
        sa.Column("title", sa.String(length=180), nullable=False),
        sa.Column("resource_type", sa.String(length=30), nullable=False, server_default="link"),
        sa.Column("url", sa.String(length=1000), nullable=True),
        sa.Column("storage_key", sa.String(length=500), nullable=True),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project_templates.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["milestone_id"], ["project_milestones.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_project_requirements_project_position", "project_requirements", ["project_id", "position"])
    op.create_index("ix_project_tasks_milestone_position", "project_tasks", ["milestone_id", "position"])
    op.create_index("ix_project_resources_project_status", "project_resources", ["project_id", "status"])


def downgrade():
    op.drop_index("ix_project_resources_project_status", table_name="project_resources")
    op.drop_index("ix_project_tasks_milestone_position", table_name="project_tasks")
    op.drop_index("ix_project_requirements_project_position", table_name="project_requirements")
    op.drop_table("project_resources")
    op.drop_table("project_tasks")
    op.drop_table("project_requirements")
    op.drop_column("project_submissions", "attachment_size")
    op.drop_column("project_submissions", "attachment_name")
    op.drop_column("project_submissions", "attachment_key")
    op.drop_column("project_rubric_criteria", "description")
    op.drop_column("project_milestones", "resources_json")
    op.drop_column("project_milestones", "completion_criteria")
    op.drop_column("project_templates", "brief_json")
    op.drop_column("project_templates", "languages_json")
    op.drop_column("project_templates", "tags_json")
    op.drop_column("project_templates", "cover_image")
