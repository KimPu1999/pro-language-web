"""post-launch operations records"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0013_operations"
down_revision = "0012_analytics"
branch_labels = None
depends_on = None

def upgrade():
    u = postgresql.UUID(as_uuid=False); ts = sa.DateTime(timezone=True)
    common = [sa.Column("created_at", ts, server_default=sa.func.now()), sa.Column("updated_at", ts, server_default=sa.func.now())]
    op.create_table("platform_incidents", sa.Column("id", u, primary_key=True), sa.Column("title", sa.String(180), nullable=False), sa.Column("description", sa.Text, nullable=False), sa.Column("severity", sa.String(20), nullable=False, server_default="medium"), sa.Column("status", sa.String(30), nullable=False, server_default="detected"), sa.Column("owner_id", u, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True), sa.Column("resolution_notes", sa.Text, nullable=False, server_default=""), *common)
    op.create_index("ix_platform_incidents_status_created", "platform_incidents", ["status", "created_at"])
    op.create_table("incident_events", sa.Column("id", u, primary_key=True), sa.Column("incident_id", u, sa.ForeignKey("platform_incidents.id", ondelete="CASCADE"), nullable=False), sa.Column("actor_id", u, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True), sa.Column("event_type", sa.String(40), nullable=False), sa.Column("body", sa.Text, nullable=False), *common)
    op.create_table("student_feedback", sa.Column("id", u, primary_key=True), sa.Column("user_id", u, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("category", sa.String(40), nullable=False), sa.Column("title", sa.String(180), nullable=False), sa.Column("body", sa.Text, nullable=False), sa.Column("status", sa.String(30), nullable=False, server_default="new"), sa.Column("priority", sa.String(20), nullable=False, server_default="normal"), sa.Column("assigned_to", u, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True), sa.Column("student_response", sa.Text, nullable=False, server_default=""), *common)
    op.create_index("ix_student_feedback_user_created", "student_feedback", ["user_id", "created_at"])
    op.create_table("engineering_issues", sa.Column("id", u, primary_key=True), sa.Column("title", sa.String(180), nullable=False), sa.Column("description", sa.Text, nullable=False), sa.Column("severity", sa.String(20), nullable=False, server_default="medium"), sa.Column("priority", sa.String(20), nullable=False, server_default="normal"), sa.Column("status", sa.String(30), nullable=False, server_default="new"), sa.Column("affected_module", sa.String(100), nullable=False, server_default=""), sa.Column("reporter_id", u, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True), sa.Column("assigned_to", u, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True), sa.Column("fix_version", sa.String(50), nullable=True), sa.Column("github_url", sa.String(500), nullable=True), *common)
    op.create_table("platform_releases", sa.Column("id", u, primary_key=True), sa.Column("version", sa.String(50), unique=True, nullable=False), sa.Column("notes", sa.Text, nullable=False), sa.Column("environment", sa.String(20), nullable=False), sa.Column("status", sa.String(30), nullable=False, server_default="draft"), sa.Column("approved_by", u, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True), sa.Column("rollback_reference", sa.String(120), nullable=True), *common)
    op.create_table("service_health_checks", sa.Column("id", u, primary_key=True), sa.Column("service", sa.String(80), nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("latency_ms", sa.Integer, nullable=True), sa.Column("detail", sa.String(240), nullable=False, server_default=""), *common)
    op.create_index("ix_service_health_service_created", "service_health_checks", ["service", "created_at"])
    op.create_table("maintenance_windows", sa.Column("id", u, primary_key=True), sa.Column("title", sa.String(180), nullable=False), sa.Column("notice", sa.Text, nullable=False), sa.Column("starts_at", ts, nullable=False), sa.Column("ends_at", ts, nullable=False), sa.Column("status", sa.String(20), nullable=False, server_default="scheduled"), sa.Column("created_by", u, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True), *common)
    op.create_table("improvement_items", sa.Column("id", u, primary_key=True), sa.Column("title", sa.String(180), nullable=False), sa.Column("description", sa.Text, nullable=False), sa.Column("priority", sa.String(20), nullable=False, server_default="normal"), sa.Column("status", sa.String(30), nullable=False, server_default="backlog"), sa.Column("owner_id", u, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True), sa.Column("target_release", sa.String(50), nullable=True), *common)

def downgrade():
    for name in ["improvement_items", "maintenance_windows", "service_health_checks", "platform_releases", "engineering_issues", "student_feedback", "incident_events", "platform_incidents"]:
        op.drop_table(name)
