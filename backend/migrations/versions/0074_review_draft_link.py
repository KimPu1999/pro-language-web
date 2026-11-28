"""Link content-review items to an unpublished lesson draft when present."""
from alembic import op
import sqlalchemy as sa

revision = "0074_review_draft_link"
down_revision = "0073_curriculum_draft_versions"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("content_review_items", sa.Column("draft_id", sa.UUID(), nullable=True))
    op.create_index("ix_content_review_items_draft_id", "content_review_items", ["draft_id"])
    op.create_foreign_key("fk_content_review_items_draft_id", "content_review_items", "lesson_content_drafts", ["draft_id"], ["id"], ondelete="SET NULL")


def downgrade():
    op.drop_constraint("fk_content_review_items_draft_id", "content_review_items", type_="foreignkey")
    op.drop_index("ix_content_review_items_draft_id", table_name="content_review_items")
    op.drop_column("content_review_items", "draft_id")
