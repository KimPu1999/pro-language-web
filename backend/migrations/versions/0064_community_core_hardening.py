"""Add context, revision, follow and moderation fields to core community data."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0064_community_core_hardening"
down_revision = "0063_learning_path_localization"
branch_labels = None
depends_on = None


def upgrade():
    uuid = postgresql.UUID(as_uuid=False)
    op.add_column("community_posts", sa.Column("course_id", uuid, sa.ForeignKey("courses.id", ondelete="SET NULL"), nullable=True))
    op.add_column("community_posts", sa.Column("module_id", uuid, sa.ForeignKey("course_modules.id", ondelete="SET NULL"), nullable=True))
    op.add_column("community_posts", sa.Column("lesson_id", uuid, sa.ForeignKey("lessons.id", ondelete="SET NULL"), nullable=True))
    op.add_column("community_posts", sa.Column("language", sa.String(10), server_default="en", nullable=False))
    op.add_column("community_posts", sa.Column("expected_behavior", sa.Text, server_default="", nullable=False))
    op.add_column("community_posts", sa.Column("actual_behavior", sa.Text, server_default="", nullable=False))
    op.add_column("community_posts", sa.Column("code_language", sa.String(50), server_default="", nullable=False))
    op.add_column("community_posts", sa.Column("code_snippet", sa.Text, server_default="", nullable=False))
    op.add_column("community_posts", sa.Column("locked", sa.Boolean, server_default=sa.false(), nullable=False))
    op.create_index("ix_community_posts_context", "community_posts", ["course_id", "module_id", "lesson_id"])

    op.create_table(
        "community_post_revisions",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("post_id", uuid, sa.ForeignKey("community_posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("changed_by", uuid, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("revision_number", sa.Integer, nullable=False),
        sa.Column("title", sa.String(220), nullable=False),
        sa.Column("body", sa.Text, nullable=False),
        sa.Column("metadata_json", sa.Text, server_default="{}", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("post_id", "revision_number"),
    )
    op.create_index("ix_community_post_revisions_post_created", "community_post_revisions", ["post_id", "created_at"])
    op.create_table(
        "community_post_follows",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("user_id", uuid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("post_id", uuid, sa.ForeignKey("community_posts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "post_id"),
    )
    op.create_index("ix_community_post_follows_post", "community_post_follows", ["post_id"])
    op.create_table(
        "community_tag_follows",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("user_id", uuid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tag", sa.String(50), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "tag"),
    )
    op.add_column("community_reports", sa.Column("reviewed_by", uuid, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True))
    op.add_column("community_reports", sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("community_reports", sa.Column("resolution_note", sa.Text, server_default="", nullable=False))
    op.create_index("ix_community_reports_status_created", "community_reports", ["status", "created_at"])


def downgrade():
    op.drop_index("ix_community_reports_status_created", table_name="community_reports")
    op.drop_column("community_reports", "resolution_note")
    op.drop_column("community_reports", "reviewed_at")
    op.drop_column("community_reports", "reviewed_by")
    op.drop_table("community_tag_follows")
    op.drop_index("ix_community_post_follows_post", table_name="community_post_follows")
    op.drop_table("community_post_follows")
    op.drop_index("ix_community_post_revisions_post_created", table_name="community_post_revisions")
    op.drop_table("community_post_revisions")
    op.drop_index("ix_community_posts_context", table_name="community_posts")
    for name in ("locked", "code_snippet", "code_language", "actual_behavior", "expected_behavior", "language", "lesson_id", "module_id", "course_id"):
        op.drop_column("community_posts", name)
