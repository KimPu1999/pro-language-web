"""Add indexes used by community feeds and detail pages.

This migration is additive only; it does not alter or reset existing records.
"""
from alembic import op

revision = "0027_community_query_indexes"
down_revision = "0026_project_learning_content"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("ix_community_comments_post_status_created", "community_comments", ["post_id", "status", "created_at"])
    op.create_index("ix_community_answers_post_status_created", "community_answers", ["post_id", "status", "created_at"])
    op.create_index("ix_community_post_tags_tag_post", "community_post_tags", ["tag", "post_id"])
    op.create_index("ix_study_group_members_user_group", "study_group_members", ["user_id", "group_id"])


def downgrade():
    op.drop_index("ix_study_group_members_user_group", table_name="study_group_members")
    op.drop_index("ix_community_post_tags_tag_post", table_name="community_post_tags")
    op.drop_index("ix_community_answers_post_status_created", table_name="community_answers")
    op.drop_index("ix_community_comments_post_status_created", table_name="community_comments")
