"""phase 27 cybersecurity learning and secure coding records"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0029_cybersecurity_training"
down_revision = "0028_cloud_lab_indexes"
branch_labels = None
depends_on = None


def upgrade():
    u = postgresql.UUID(as_uuid=False)
    ts = sa.DateTime(timezone=True)
    common = [sa.Column("created_at", ts, server_default=sa.func.now()), sa.Column("updated_at", ts, server_default=sa.func.now())]
    fk = lambda target, delete="CASCADE": sa.ForeignKey(target, ondelete=delete)
    op.create_table("cybersecurity_lab_definitions", sa.Column("id", u, primary_key=True), sa.Column("organization_id", u, fk("organizations.id")), sa.Column("created_by", u, fk("users.id", "SET NULL")), sa.Column("title", sa.String(180), nullable=False), sa.Column("slug", sa.String(180), nullable=False), sa.Column("category", sa.String(60), server_default="secure_coding"), sa.Column("difficulty", sa.String(30), server_default="beginner"), sa.Column("language", sa.String(40), server_default="python"), sa.Column("description_en", sa.Text, nullable=False), sa.Column("description_mm", sa.Text), sa.Column("objectives_json", sa.Text, server_default="[]"), sa.Column("mode", sa.String(30), server_default="isolated_runner"), sa.Column("status", sa.String(20), server_default="draft"), sa.Column("published", sa.Boolean, server_default=sa.false()), *common, sa.UniqueConstraint("organization_id", "slug"))
    op.create_index("ix_cyber_lab_defs_published", "cybersecurity_lab_definitions", ["published", "category"])
    op.create_table("cybersecurity_lab_attempts", sa.Column("id", u, primary_key=True), sa.Column("lab_id", u, fk("cybersecurity_lab_definitions.id"), nullable=False), sa.Column("user_id", u, fk("users.id"), nullable=False), sa.Column("workspace_id", u, fk("learning_lab_workspaces.id", "SET NULL")), sa.Column("status", sa.String(30), server_default="started"), sa.Column("score", sa.Integer), sa.Column("verified", sa.Boolean, server_default=sa.false()), sa.Column("findings_json", sa.Text, server_default="[]"), *common)
    op.create_index("ix_cyber_lab_attempts_user_status", "cybersecurity_lab_attempts", ["user_id", "status"])
    op.create_table("cybersecurity_vulnerability_findings", sa.Column("id", u, primary_key=True), sa.Column("attempt_id", u, fk("cybersecurity_lab_attempts.id"), nullable=False), sa.Column("title", sa.String(240), nullable=False), sa.Column("severity", sa.String(20), nullable=False), sa.Column("evidence", sa.Text, server_default=""), sa.Column("status", sa.String(20), server_default="open"), *common)
    op.create_index("ix_cyber_findings_attempt", "cybersecurity_vulnerability_findings", ["attempt_id"])
    op.create_table("cybersecurity_remediation_records", sa.Column("id", u, primary_key=True), sa.Column("finding_id", u, fk("cybersecurity_vulnerability_findings.id"), nullable=False), sa.Column("user_id", u, fk("users.id"), nullable=False), sa.Column("explanation", sa.Text, server_default=""), sa.Column("verified", sa.Boolean, server_default=sa.false()), *common)
    op.create_table("cybersecurity_threat_models", sa.Column("id", u, primary_key=True), sa.Column("organization_id", u, fk("organizations.id")), sa.Column("owner_id", u, fk("users.id"), nullable=False), sa.Column("title", sa.String(180), nullable=False), sa.Column("status", sa.String(20), server_default="draft"), sa.Column("current_version", sa.Integer, server_default="1"), *common)
    op.create_table("cybersecurity_threat_model_versions", sa.Column("id", u, primary_key=True), sa.Column("threat_model_id", u, fk("cybersecurity_threat_models.id"), nullable=False), sa.Column("created_by", u, fk("users.id"), nullable=False), sa.Column("version_number", sa.Integer, nullable=False), sa.Column("status", sa.String(20), server_default="draft"), sa.Column("content_json", sa.Text, server_default="{}"), *common, sa.UniqueConstraint("threat_model_id", "version_number"))
    op.create_table("cybersecurity_ai_interactions", sa.Column("id", u, primary_key=True), sa.Column("user_id", u, fk("users.id"), nullable=False), sa.Column("lab_id", u, fk("cybersecurity_lab_definitions.id", "SET NULL")), sa.Column("request_type", sa.String(50), nullable=False), sa.Column("status", sa.String(30), server_default="unavailable"), sa.Column("prompt_summary", sa.String(500), server_default=""), *common)
    op.create_table("cybersecurity_security_events", sa.Column("id", u, primary_key=True), sa.Column("organization_id", u, fk("organizations.id", "SET NULL")), sa.Column("actor_id", u, fk("users.id", "SET NULL")), sa.Column("event_type", sa.String(80), nullable=False), sa.Column("severity", sa.String(20), server_default="info"), sa.Column("metadata_json", sa.Text, server_default="{}"), *common)
    op.create_table("cybersecurity_audit_logs", sa.Column("id", u, primary_key=True), sa.Column("organization_id", u, fk("organizations.id", "SET NULL")), sa.Column("actor_id", u, fk("users.id", "SET NULL")), sa.Column("action", sa.String(100), nullable=False), sa.Column("resource_type", sa.String(60), nullable=False), sa.Column("resource_id", u), sa.Column("metadata_json", sa.Text, server_default="{}"), *common)
    op.create_index("ix_cyber_audit_resource", "cybersecurity_audit_logs", ["resource_type", "resource_id"])


def downgrade():
    op.drop_index("ix_cyber_audit_resource", table_name="cybersecurity_audit_logs")
    for name in ["cybersecurity_audit_logs", "cybersecurity_security_events", "cybersecurity_ai_interactions", "cybersecurity_threat_model_versions", "cybersecurity_threat_models", "cybersecurity_remediation_records", "cybersecurity_vulnerability_findings", "cybersecurity_lab_attempts"]:
        op.drop_table(name)
    op.drop_index("ix_cyber_lab_defs_published", table_name="cybersecurity_lab_definitions")
    op.drop_table("cybersecurity_lab_definitions")
