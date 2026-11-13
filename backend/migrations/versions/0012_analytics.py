"""platform analytics report history and audit records"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0012_analytics"
down_revision = "0011_live_classes"
branch_labels = None
depends_on = None

def upgrade():
    u = postgresql.UUID(as_uuid=False); ts = sa.DateTime(timezone=True)
    common = [sa.Column("created_at", ts, server_default=sa.func.now()), sa.Column("updated_at", ts, server_default=sa.func.now())]
    op.create_table("analytics_report_exports",
        sa.Column("id", u, primary_key=True), sa.Column("requested_by", u, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("report_type", sa.String(60), nullable=False), sa.Column("filters_json", sa.Text, nullable=False, server_default="{}"),
        sa.Column("row_count", sa.Integer, nullable=False, server_default="0"), sa.Column("status", sa.String(20), nullable=False, server_default="completed"), *common)
    op.create_index("ix_analytics_exports_requested_by_created", "analytics_report_exports", ["requested_by", "created_at"])
    op.create_table("analytics_audit_logs",
        sa.Column("id", u, primary_key=True), sa.Column("actor_id", u, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(80), nullable=False), sa.Column("report_type", sa.String(60)),
        sa.Column("filters_json", sa.Text, nullable=False, server_default="{}"), *common)
    op.create_index("ix_analytics_audit_actor_created", "analytics_audit_logs", ["actor_id", "created_at"])

def downgrade():
    op.drop_table("analytics_audit_logs")
    op.drop_table("analytics_report_exports")
