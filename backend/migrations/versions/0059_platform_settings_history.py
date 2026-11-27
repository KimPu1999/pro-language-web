"""Add typed platform setting metadata and safe change history."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0059_platform_settings_history"
down_revision = "0058_performance_indexes"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("platform_settings", sa.Column("scope", sa.String(length=40), nullable=False, server_default="platform"))
    op.add_column("platform_settings", sa.Column("category", sa.String(length=60), nullable=False, server_default="general"))
    op.add_column("platform_settings", sa.Column("version", sa.Integer(), nullable=False, server_default="1"))
    op.create_index("ix_platform_settings_category", "platform_settings", ["category"])
    op.create_table(
        "platform_setting_history",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("setting_key", sa.String(length=120), nullable=False),
        sa.Column("category", sa.String(length=60), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("previous_value_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("new_value_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("actor_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("change_reason", sa.String(length=240), nullable=False, server_default=""),
        sa.Column("correlation_id", sa.String(length=120), nullable=True),
        sa.Column("outcome", sa.String(length=20), nullable=False, server_default="success"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index("ix_platform_setting_history_setting_key", "platform_setting_history", ["setting_key"])
    op.create_index("ix_platform_setting_history_category", "platform_setting_history", ["category"])
    op.create_index("ix_platform_setting_history_actor_id", "platform_setting_history", ["actor_id"])
    op.create_index("ix_platform_setting_history_correlation_id", "platform_setting_history", ["correlation_id"])


def downgrade():
    op.drop_index("ix_platform_setting_history_correlation_id", table_name="platform_setting_history")
    op.drop_index("ix_platform_setting_history_actor_id", table_name="platform_setting_history")
    op.drop_index("ix_platform_setting_history_category", table_name="platform_setting_history")
    op.drop_index("ix_platform_setting_history_setting_key", table_name="platform_setting_history")
    op.drop_table("platform_setting_history")
    op.drop_index("ix_platform_settings_category", table_name="platform_settings")
    op.drop_column("platform_settings", "version")
    op.drop_column("platform_settings", "category")
    op.drop_column("platform_settings", "scope")
