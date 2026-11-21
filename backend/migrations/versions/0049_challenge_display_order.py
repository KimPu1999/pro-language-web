"""Persist challenge catalog ordering without changing existing records."""
from alembic import op
import sqlalchemy as sa

revision = "0049_challenge_display_order"
down_revision = "0048_challenge_management"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("challenges", sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"))
    op.create_index("ix_challenges_display_order", "challenges", ["display_order"])


def downgrade():
    op.drop_index("ix_challenges_display_order", table_name="challenges")
    op.drop_column("challenges", "display_order")
