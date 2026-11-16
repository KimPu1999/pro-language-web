"""Add database-backed platform settings for admin-managed branding."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0042_platform_settings"
down_revision = "0041_c_course_quizzes"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        "platform_settings",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("key", sa.String(120), nullable=False, unique=True),
        sa.Column("value_json", sa.Text, nullable=False, server_default="{}"),
        sa.Column("updated_by", postgresql.UUID(as_uuid=False), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_platform_settings_key", "platform_settings", ["key"])

def downgrade():
    op.drop_index("ix_platform_settings_key", table_name="platform_settings")
    op.drop_table("platform_settings")
