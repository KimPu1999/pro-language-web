"""Add platform-scoped content review workflow records."""
from alembic import op
import sqlalchemy as sa

revision = "0056_content_review_workflow"
down_revision = "0055_syntax_references"
branch_labels = None
depends_on = None


def upgrade():
    uuid = sa.UUID()
    op.create_table(
        "content_review_items",
        sa.Column("id", uuid, nullable=False),
        sa.Column("content_type", sa.String(40), nullable=False),
        sa.Column("content_key", sa.String(180), nullable=False),
        sa.Column("organization_id", uuid, nullable=True),
        sa.Column("title", sa.String(240), nullable=False),
        sa.Column("submitted_by", uuid, nullable=True),
        sa.Column("reviewer_id", uuid, nullable=True),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("status", sa.String(30), nullable=False, server_default="submitted"),
        sa.Column("submitted_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["submitted_by"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["reviewer_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("content_type", "content_key", "version"),
    )
    op.create_index("ix_content_review_items_status", "content_review_items", ["status"])
    op.create_index("ix_content_review_items_submitted_by", "content_review_items", ["submitted_by"])
    op.create_index("ix_content_review_items_reviewer_id", "content_review_items", ["reviewer_id"])
    op.create_index("ix_content_review_items_organization_id", "content_review_items", ["organization_id"])
    op.create_index("ix_content_review_items_org_status", "content_review_items", ["organization_id", "status"])
    op.create_index("ix_content_review_items_status_submitted", "content_review_items", ["status", "submitted_at"])
    op.create_index("ix_content_review_items_reviewer_status", "content_review_items", ["reviewer_id", "status"])
    op.create_table(
        "content_review_comments",
        sa.Column("id", uuid, nullable=False),
        sa.Column("review_item_id", uuid, nullable=False),
        sa.Column("author_id", uuid, nullable=False),
        sa.Column("review_version", sa.Integer(), nullable=False),
        sa.Column("comment_type", sa.String(40), nullable=False, server_default="general"),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["review_item_id"], ["content_review_items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_content_review_comments_review_item_id", "content_review_comments", ["review_item_id"])
    op.create_table(
        "content_review_events",
        sa.Column("id", uuid, nullable=False),
        sa.Column("review_item_id", uuid, nullable=False),
        sa.Column("actor_id", uuid, nullable=False),
        sa.Column("from_status", sa.String(30), nullable=True),
        sa.Column("to_status", sa.String(30), nullable=False),
        sa.Column("comment", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["review_item_id"], ["content_review_items.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_content_review_events_review_item_id", "content_review_events", ["review_item_id"])
    # Preserve the latest legacy course review records in the new global queue.
    # These rows already represent real admin submissions; no synthetic review data is created.
    op.execute(sa.text("""
        WITH latest AS (
            SELECT pr.*, ROW_NUMBER() OVER (PARTITION BY pr.course_id ORDER BY pr.created_at DESC, pr.id DESC) AS row_number
            FROM publishing_reviews pr
        )
        INSERT INTO content_review_items (
            id, content_type, content_key, title, submitted_by, reviewer_id, version, status,
            submitted_at, created_at, updated_at
        )
        SELECT latest.id, 'course', CAST(latest.course_id AS TEXT), courses.title, courses.created_by,
               NULL, 1, 'submitted', latest.created_at, latest.created_at, latest.updated_at
        FROM latest
        JOIN courses ON courses.id = latest.course_id
        WHERE latest.row_number = 1
          AND latest.decision = 'in_review'
    """))


def downgrade():
    op.drop_index("ix_content_review_events_review_item_id", table_name="content_review_events")
    op.drop_table("content_review_events")
    op.drop_index("ix_content_review_comments_review_item_id", table_name="content_review_comments")
    op.drop_table("content_review_comments")
    op.drop_index("ix_content_review_items_reviewer_status", table_name="content_review_items")
    op.drop_index("ix_content_review_items_status_submitted", table_name="content_review_items")
    op.drop_index("ix_content_review_items_org_status", table_name="content_review_items")
    op.drop_index("ix_content_review_items_organization_id", table_name="content_review_items")
    op.drop_index("ix_content_review_items_reviewer_id", table_name="content_review_items")
    op.drop_index("ix_content_review_items_submitted_by", table_name="content_review_items")
    op.drop_index("ix_content_review_items_status", table_name="content_review_items")
    op.drop_table("content_review_items")
