"""Add additive Career Path builder metadata and assessment links."""
from alembic import op
import sqlalchemy as sa

revision = "0051_career_path_builder"
down_revision = "0050_project_management"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("career_roadmaps", sa.Column("cover_image", sa.String(length=500), nullable=True))
    op.add_column("career_roadmaps", sa.Column("goals_json", sa.Text(), nullable=False, server_default="[]"))
    op.add_column("career_roadmaps", sa.Column("skills_json", sa.Text(), nullable=False, server_default="[]"))
    op.add_column("career_roadmaps", sa.Column("completion_rules_json", sa.Text(), nullable=False, server_default="{}"))
    op.add_column("roadmap_stages", sa.Column("objectives_json", sa.Text(), nullable=False, server_default="[]"))
    op.add_column("roadmap_stages", sa.Column("skills_json", sa.Text(), nullable=False, server_default="[]"))
    op.add_column("roadmap_stages", sa.Column("completion_rules_json", sa.Text(), nullable=False, server_default="{}"))
    uuid = sa.UUID()
    op.create_table(
        "roadmap_assessments",
        sa.Column("id", uuid, nullable=False),
        sa.Column("roadmap_id", uuid, nullable=False),
        sa.Column("assessment_id", uuid, nullable=False),
        sa.Column("passing_score", sa.Integer(), nullable=False, server_default="70"),
        sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["roadmap_id"], ["career_roadmaps.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessment_definitions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("roadmap_id", "assessment_id"),
    )
    op.create_index("ix_roadmap_assessments_roadmap_position", "roadmap_assessments", ["roadmap_id", "position"])


def downgrade():
    op.drop_index("ix_roadmap_assessments_roadmap_position", table_name="roadmap_assessments")
    op.drop_table("roadmap_assessments")
    op.drop_column("roadmap_stages", "completion_rules_json")
    op.drop_column("roadmap_stages", "skills_json")
    op.drop_column("roadmap_stages", "objectives_json")
    op.drop_column("career_roadmaps", "completion_rules_json")
    op.drop_column("career_roadmaps", "skills_json")
    op.drop_column("career_roadmaps", "goals_json")
    op.drop_column("career_roadmaps", "cover_image")
