"""Add private lesson bookmarks without changing existing progress."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0024_lesson_bookmarks"
down_revision = "0023_collaboration"
branch_labels = None
depends_on = None


def upgrade():
    uuid = postgresql.UUID(as_uuid=False)
    op.create_table(
        "lesson_bookmarks",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("user_id", uuid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("lesson_id", uuid, sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "lesson_id", name="uq_lesson_bookmarks_user_lesson"),
    )
    op.create_index("ix_lesson_bookmarks_user", "lesson_bookmarks", ["user_id"])


def downgrade():
    op.drop_index("ix_lesson_bookmarks_user", table_name="lesson_bookmarks")
    op.drop_table("lesson_bookmarks")
