"""Add Burmese learning-path fields and efficient public ordering indexes."""

from alembic import op
import sqlalchemy as sa

revision = "0063_learning_path_localization"
down_revision = "0062_media_library_hardening"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("career_roadmaps", sa.Column("title_mm", sa.String(length=180), nullable=True))
    op.add_column("career_roadmaps", sa.Column("prerequisites_mm", sa.Text(), nullable=True))
    op.add_column("career_roadmaps", sa.Column("outcomes_mm", sa.Text(), nullable=True))
    op.add_column("roadmap_stages", sa.Column("title_mm", sa.String(length=180), nullable=True))
    op.add_column("roadmap_steps", sa.Column("title_mm", sa.String(length=180), nullable=True))
    op.create_index("ix_roadmap_stages_roadmap_position", "roadmap_stages", ["roadmap_id", "position"])
    op.create_index("ix_roadmap_steps_stage_position", "roadmap_steps", ["stage_id", "position"])


def downgrade():
    op.drop_index("ix_roadmap_steps_stage_position", table_name="roadmap_steps")
    op.drop_index("ix_roadmap_stages_roadmap_position", table_name="roadmap_stages")
    op.drop_column("roadmap_steps", "title_mm")
    op.drop_column("roadmap_stages", "title_mm")
    op.drop_column("career_roadmaps", "outcomes_mm")
    op.drop_column("career_roadmaps", "prerequisites_mm")
    op.drop_column("career_roadmaps", "title_mm")
