"""Add the database-backed Developer Tools catalog.

This migration is additive only.  Catalog records are imported separately by
the idempotent registry importer so existing data is never overwritten.
"""

from alembic import op
import sqlalchemy as sa


revision = "0046_developer_tools_catalog"
down_revision = "0045_course_detail_content"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tool_categories",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("icon_key", sa.String(length=80), nullable=False, server_default="wrench"),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_tool_categories_slug", "tool_categories", ["slug"])
    op.create_index("ix_tool_categories_active_order", "tool_categories", ["is_active", "display_order"])
    op.create_table(
        "developer_tools",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("category_id", sa.UUID(), nullable=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("slug", sa.String(length=160), nullable=False),
        sa.Column("short_description", sa.Text(), nullable=False, server_default=""),
        sa.Column("full_description", sa.Text(), nullable=False, server_default=""),
        sa.Column("icon_key", sa.String(length=80), nullable=False, server_default="wrench"),
        sa.Column("route_path", sa.String(length=240), nullable=False),
        sa.Column("implementation_key", sa.String(length=100), nullable=False),
        sa.Column("tags", sa.Text(), nullable=False, server_default=""),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["category_id"], ["tool_categories.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_developer_tools_slug", "developer_tools", ["slug"])
    op.create_index("ix_developer_tools_category_id", "developer_tools", ["category_id"])
    op.create_index("ix_developer_tools_status", "developer_tools", ["status"])
    op.create_index("ix_developer_tools_public_order", "developer_tools", ["status", "is_enabled", "display_order"])
    op.create_index("ix_developer_tools_category_order", "developer_tools", ["category_id", "display_order"])
    op.create_table(
        "tool_favorites",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("tool_id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tool_id"], ["developer_tools.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "tool_id"),
    )
    op.create_table(
        "tool_audit_logs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("tool_id", sa.UUID(), nullable=True),
        sa.Column("actor_id", sa.UUID(), nullable=True),
        sa.Column("action", sa.String(length=80), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
        sa.ForeignKeyConstraint(["tool_id"], ["developer_tools.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tool_audit_logs_tool_id", "tool_audit_logs", ["tool_id"])
    op.create_index("ix_tool_audit_logs_actor_id", "tool_audit_logs", ["actor_id"])
    op.create_index("ix_tool_audit_logs_timestamp", "tool_audit_logs", ["timestamp"])


def downgrade():
    op.drop_index("ix_tool_audit_logs_timestamp", table_name="tool_audit_logs")
    op.drop_index("ix_tool_audit_logs_actor_id", table_name="tool_audit_logs")
    op.drop_index("ix_tool_audit_logs_tool_id", table_name="tool_audit_logs")
    op.drop_table("tool_audit_logs")
    op.drop_table("tool_favorites")
    op.drop_index("ix_developer_tools_category_order", table_name="developer_tools")
    op.drop_index("ix_developer_tools_public_order", table_name="developer_tools")
    op.drop_index("ix_developer_tools_status", table_name="developer_tools")
    op.drop_index("ix_developer_tools_category_id", table_name="developer_tools")
    op.drop_index("ix_developer_tools_slug", table_name="developer_tools")
    op.drop_table("developer_tools")
    op.drop_index("ix_tool_categories_active_order", table_name="tool_categories")
    op.drop_index("ix_tool_categories_slug", table_name="tool_categories")
    op.drop_table("tool_categories")
