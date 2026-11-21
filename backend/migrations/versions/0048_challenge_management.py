"""Add challenge builder fields without changing existing challenge records.

All columns are additive and have safe defaults so existing challenges remain
published and usable.  Existing IDs, submissions, test cases and progress are
not modified.
"""
from alembic import op
import sqlalchemy as sa

revision = "0048_challenge_management"
down_revision = "0047_course_builder_revisions"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("challenges", sa.Column("challenge_type", sa.String(length=30), nullable=False, server_default="coding"))
    op.add_column("challenges", sa.Column("tags_json", sa.Text(), nullable=False, server_default="[]"))
    op.add_column("challenges", sa.Column("estimated_minutes", sa.Integer(), nullable=False, server_default="30"))
    op.add_column("challenges", sa.Column("input_format", sa.Text(), nullable=False, server_default=""))
    op.add_column("challenges", sa.Column("output_format", sa.Text(), nullable=False, server_default=""))
    op.add_column("challenges", sa.Column("explanation_en", sa.Text(), nullable=False, server_default=""))
    op.add_column("challenges", sa.Column("execution_mode", sa.String(length=20), nullable=False, server_default="stdin"))
    op.add_column("challenges", sa.Column("reference_solution", sa.Text(), nullable=True))
    op.add_column("challenges", sa.Column("quiz_mode", sa.String(length=20), nullable=True))
    op.add_column("challenges", sa.Column("quiz_options_json", sa.Text(), nullable=False, server_default="[]"))
    op.add_column("challenges", sa.Column("quiz_correct_answer", sa.Text(), nullable=True))
    op.add_column("challenges", sa.Column("quiz_explanation", sa.Text(), nullable=False, server_default=""))


def downgrade():
    for name in ("quiz_explanation", "quiz_correct_answer", "quiz_options_json", "quiz_mode", "reference_solution", "execution_mode", "explanation_en", "output_format", "input_format", "estimated_minutes", "tags_json", "challenge_type"):
        op.drop_column("challenges", name)
