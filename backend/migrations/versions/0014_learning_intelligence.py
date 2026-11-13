"""phase 16 learning intelligence records"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0014_learning_intelligence"
down_revision = "0013_operations"
branch_labels = None
depends_on = None

def upgrade():
    u = postgresql.UUID(as_uuid=False); ts = sa.DateTime(timezone=True)
    common = [sa.Column("created_at", ts, server_default=sa.func.now()), sa.Column("updated_at", ts, server_default=sa.func.now())]
    op.create_table("learning_skill_prerequisites", sa.Column("id", u, primary_key=True), sa.Column("skill_id", u, sa.ForeignKey("skill_definitions.id", ondelete="CASCADE"), nullable=False), sa.Column("prerequisite_skill_id", u, sa.ForeignKey("skill_definitions.id", ondelete="CASCADE"), nullable=False), *common, sa.UniqueConstraint("skill_id", "prerequisite_skill_id"))
    op.create_index("ix_learning_skill_prereq_skill", "learning_skill_prerequisites", ["skill_id"])
    op.create_index("ix_learning_skill_prereq_parent", "learning_skill_prerequisites", ["prerequisite_skill_id"])
    op.create_table("learning_skill_snapshots", sa.Column("id", u, primary_key=True), sa.Column("user_id", u, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("skill_id", u, sa.ForeignKey("skill_definitions.id", ondelete="CASCADE"), nullable=False), sa.Column("score", sa.Integer), sa.Column("confidence", sa.String(30), nullable=False, server_default="not_yet_assessed"), sa.Column("evidence_count", sa.Integer, nullable=False, server_default="0"), sa.Column("explanation", sa.Text, nullable=False, server_default=""), sa.Column("last_assessed_at", ts), *common, sa.UniqueConstraint("user_id", "skill_id"))
    op.create_index("ix_learning_skill_snapshots_user", "learning_skill_snapshots", ["user_id"])
    op.create_table("learning_recommendation_feedback", sa.Column("id", u, primary_key=True), sa.Column("recommendation_id", u, sa.ForeignKey("learning_recommendations.id", ondelete="CASCADE"), nullable=False), sa.Column("user_id", u, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("action", sa.String(30), nullable=False), *common, sa.UniqueConstraint("recommendation_id", "user_id"))
    op.create_table("learning_study_plans", sa.Column("id", u, primary_key=True), sa.Column("user_id", u, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("title", sa.String(180), nullable=False), sa.Column("status", sa.String(20), nullable=False, server_default="active"), sa.Column("week_start", ts, nullable=False), *common)
    op.create_index("ix_learning_study_plans_user", "learning_study_plans", ["user_id"])
    op.create_table("learning_study_plan_items", sa.Column("id", u, primary_key=True), sa.Column("plan_id", u, sa.ForeignKey("learning_study_plans.id", ondelete="CASCADE"), nullable=False), sa.Column("activity_type", sa.String(30), nullable=False), sa.Column("resource_id", u), sa.Column("scheduled_for", ts, nullable=False), sa.Column("minutes", sa.Integer, nullable=False, server_default="30"), sa.Column("completed", sa.Boolean, nullable=False, server_default=sa.false()), sa.Column("completed_at", ts), *common)
    op.create_index("ix_learning_plan_items_plan_date", "learning_study_plan_items", ["plan_id", "scheduled_for"])
    op.create_table("learning_revision_items", sa.Column("id", u, primary_key=True), sa.Column("user_id", u, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("lesson_id", u, sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False), sa.Column("next_review_at", ts, nullable=False), sa.Column("interval_days", sa.Integer, nullable=False, server_default="1"), sa.Column("ease_factor", sa.Float, nullable=False, server_default="2.5"), sa.Column("confidence", sa.Integer), *common, sa.UniqueConstraint("user_id", "lesson_id"))
    op.create_index("ix_learning_revision_due", "learning_revision_items", ["user_id", "next_review_at"])
    op.create_table("learning_revision_attempts", sa.Column("id", u, primary_key=True), sa.Column("item_id", u, sa.ForeignKey("learning_revision_items.id", ondelete="CASCADE"), nullable=False), sa.Column("user_id", u, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("confidence", sa.Integer, nullable=False), sa.Column("reviewed_at", ts, server_default=sa.func.now()), *common)
    op.create_table("learning_risk_indicators", sa.Column("id", u, primary_key=True), sa.Column("user_id", u, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("indicator_type", sa.String(50), nullable=False), sa.Column("severity", sa.String(20), nullable=False), sa.Column("explanation", sa.Text, nullable=False), sa.Column("active", sa.Boolean, nullable=False, server_default=sa.true()), *common, sa.UniqueConstraint("user_id", "indicator_type"))
    op.create_table("learning_coach_interactions", sa.Column("id", u, primary_key=True), sa.Column("user_id", u, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("prompt_summary", sa.String(500), nullable=False), sa.Column("response_status", sa.String(30), nullable=False), sa.Column("context_keys", sa.Text, nullable=False, server_default="[]"), *common)

def downgrade():
    for name in ["learning_coach_interactions", "learning_risk_indicators", "learning_revision_attempts", "learning_revision_items", "learning_study_plan_items", "learning_study_plans", "learning_recommendation_feedback", "learning_skill_snapshots", "learning_skill_prerequisites"]:
        op.drop_table(name)
