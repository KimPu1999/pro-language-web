"""Add private learning path bookmarks."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0025_learning_path_bookmarks"
down_revision = "0024_lesson_bookmarks"
branch_labels = None
depends_on = None

def upgrade():
    uuid = postgresql.UUID(as_uuid=False)
    op.create_table(
        "student_roadmap_bookmarks",
        sa.Column("id", uuid, primary_key=True),
        sa.Column("user_id", uuid, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("roadmap_id", uuid, sa.ForeignKey("career_roadmaps.id", ondelete="CASCADE"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("user_id", "roadmap_id", name="uq_student_roadmap_bookmarks_user_roadmap"),
    )
    op.create_index("ix_student_roadmap_bookmarks_user", "student_roadmap_bookmarks", ["user_id"])

def downgrade():
    op.drop_index("ix_student_roadmap_bookmarks_user", table_name="student_roadmap_bookmarks")
    op.drop_table("student_roadmap_bookmarks")
