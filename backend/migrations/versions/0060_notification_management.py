"""Add durable platform notification management tables."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0060_notification_management"
down_revision = "0059_platform_settings_history"
branch_labels = None
depends_on = None
u = postgresql.UUID(as_uuid=False)


def _timestamps():
    return [sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now())]


def upgrade():
    op.create_table("notification_templates",
        sa.Column("id", u, primary_key=True), sa.Column("template_key", sa.String(120), nullable=False), sa.Column("name", sa.String(180), nullable=False),
        sa.Column("category", sa.String(60), nullable=False, server_default="general"), sa.Column("channel", sa.String(20), nullable=False, server_default="in_app"),
        sa.Column("locale", sa.String(10), nullable=False, server_default="en"), sa.Column("status", sa.String(20), nullable=False, server_default="draft"), sa.Column("current_version", sa.Integer(), nullable=False, server_default="1"), *_timestamps(),
        sa.UniqueConstraint("template_key", "channel", "locale"))
    op.create_index("ix_notification_templates_status", "notification_templates", ["status"])
    op.create_table("notification_template_versions",
        sa.Column("id", u, primary_key=True), sa.Column("template_id", u, sa.ForeignKey("notification_templates.id", ondelete="CASCADE"), nullable=False), sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("subject", sa.String(240), nullable=False, server_default=""), sa.Column("body", sa.Text(), nullable=False), sa.Column("variables_json", sa.Text(), nullable=False, server_default="[]"),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"), sa.Column("created_by", u, sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("reviewed_by", u, sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("published_by", u, sa.ForeignKey("users.id", ondelete="SET NULL")), *_timestamps(),
        sa.UniqueConstraint("template_id", "version"))
    op.create_index("ix_notification_template_versions_template_id", "notification_template_versions", ["template_id"])
    op.create_index("ix_notification_template_versions_template_status", "notification_template_versions", ["template_id", "status"])
    op.create_table("notification_announcements",
        sa.Column("id", u, primary_key=True), sa.Column("title_en", sa.String(240), nullable=False), sa.Column("title_mm", sa.String(240), nullable=False, server_default=""), sa.Column("body_en", sa.Text(), nullable=False), sa.Column("body_mm", sa.Text(), nullable=False, server_default=""),
        sa.Column("audience_type", sa.String(40), nullable=False, server_default="all_students"), sa.Column("audience_json", sa.Text(), nullable=False, server_default="{}"), sa.Column("channels_json", sa.Text(), nullable=False, server_default='["in_app"]'), sa.Column("status", sa.String(20), nullable=False, server_default="draft"), sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", u, sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False), sa.Column("approved_by", u, sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("published_by", u, sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("published_at", sa.DateTime(timezone=True)), sa.Column("correlation_id", sa.String(120)), *_timestamps())
    op.create_index("ix_notification_announcements_status", "notification_announcements", ["status"])
    op.create_index("ix_notification_announcements_status_schedule", "notification_announcements", ["status", "scheduled_at"])
    op.create_index("ix_notification_announcements_scheduled_at", "notification_announcements", ["scheduled_at"])
    op.create_index("ix_notification_announcements_correlation_id", "notification_announcements", ["correlation_id"])
    op.create_table("notification_messages",
        sa.Column("id", u, primary_key=True), sa.Column("announcement_id", u, sa.ForeignKey("notification_announcements.id", ondelete="SET NULL")), sa.Column("template_version_id", u, sa.ForeignKey("notification_template_versions.id", ondelete="SET NULL")), sa.Column("recipient_id", u, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("channel", sa.String(20), nullable=False), sa.Column("locale", sa.String(10), nullable=False, server_default="en"), sa.Column("subject", sa.String(240), nullable=False, server_default=""), sa.Column("body", sa.Text(), nullable=False), sa.Column("status", sa.String(30), nullable=False, server_default="queued"), sa.Column("provider", sa.String(60), nullable=False, server_default="in_app"), sa.Column("provider_message_id", sa.String(240)), sa.Column("error_code", sa.String(80)), sa.Column("next_retry_at", sa.DateTime(timezone=True)), sa.Column("idempotency_key", sa.String(240), nullable=False), sa.Column("correlation_id", sa.String(120)), sa.Column("read_at", sa.DateTime(timezone=True)), *_timestamps(), sa.UniqueConstraint("idempotency_key"))
    for name, cols in [("ix_notification_messages_announcement_id", ["announcement_id"]), ("ix_notification_messages_recipient_id", ["recipient_id"]), ("ix_notification_messages_recipient_status", ["recipient_id", "status"]), ("ix_notification_messages_channel_status", ["channel", "status"]), ("ix_notification_messages_status", ["status"]), ("ix_notification_messages_provider_message_id", ["provider_message_id"]), ("ix_notification_messages_next_retry_at", ["next_retry_at"]), ("ix_notification_messages_correlation_id", ["correlation_id"])]: op.create_index(name, "notification_messages", cols)
    op.create_table("notification_delivery_attempts",
        sa.Column("id", u, primary_key=True), sa.Column("message_id", u, sa.ForeignKey("notification_messages.id", ondelete="CASCADE"), nullable=False), sa.Column("attempt_number", sa.Integer(), nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("provider_message_id", sa.String(240)), sa.Column("error_code", sa.String(80)), sa.Column("correlation_id", sa.String(120)), *_timestamps(), sa.UniqueConstraint("message_id", "attempt_number"))
    op.create_index("ix_notification_delivery_attempts_message_id", "notification_delivery_attempts", ["message_id"])
    op.create_index("ix_notification_delivery_attempts_message_created", "notification_delivery_attempts", ["message_id", "created_at"])
    op.create_index("ix_notification_delivery_attempts_correlation_id", "notification_delivery_attempts", ["correlation_id"])
    op.create_table("notification_provider_events",
        sa.Column("id", u, primary_key=True), sa.Column("provider", sa.String(60), nullable=False), sa.Column("provider_event_id", sa.String(240), nullable=False), sa.Column("provider_message_id", sa.String(240)), sa.Column("event_type", sa.String(60), nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("payload_hash", sa.String(128), nullable=False), sa.Column("occurred_at", sa.DateTime(timezone=True)), *_timestamps(), sa.UniqueConstraint("provider", "provider_event_id"))
    op.create_index("ix_notification_provider_events_message", "notification_provider_events", ["provider_message_id"])
    op.create_table("notification_preferences",
        sa.Column("id", u, primary_key=True), sa.Column("user_id", u, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("preferred_locale", sa.String(10), nullable=False, server_default="en"), sa.Column("in_app_enabled", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("email_enabled", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("course_announcements", sa.Boolean(), nullable=False, server_default=sa.true()), sa.Column("digest_frequency", sa.String(20), nullable=False, server_default="instant"), sa.Column("quiet_hours_start", sa.String(5)), sa.Column("quiet_hours_end", sa.String(5)), *_timestamps(), sa.UniqueConstraint("user_id"))
    op.create_index("ix_notification_preferences_user_id", "notification_preferences", ["user_id"])
    op.create_table("notification_outbox",
        sa.Column("id", u, primary_key=True), sa.Column("message_id", u, sa.ForeignKey("notification_messages.id", ondelete="CASCADE"), nullable=False), sa.Column("status", sa.String(20), nullable=False, server_default="queued"), sa.Column("attempt_count", sa.Integer(), nullable=False, server_default="0"), sa.Column("available_at", sa.DateTime(timezone=True), server_default=sa.func.now()), sa.Column("locked_at", sa.DateTime(timezone=True)), sa.Column("last_error_code", sa.String(80)), *_timestamps(), sa.UniqueConstraint("message_id"))
    op.create_index("ix_notification_outbox_message_id", "notification_outbox", ["message_id"])
    op.create_index("ix_notification_outbox_status", "notification_outbox", ["status"])
    op.create_index("ix_notification_outbox_status_available", "notification_outbox", ["status", "available_at"])
    op.create_index("ix_notification_outbox_available_at", "notification_outbox", ["available_at"])
    op.create_table("notification_audit_events",
        sa.Column("id", u, primary_key=True), sa.Column("actor_id", u, sa.ForeignKey("users.id", ondelete="SET NULL")), sa.Column("action", sa.String(100), nullable=False), sa.Column("resource_type", sa.String(60), nullable=False), sa.Column("resource_id", u), sa.Column("outcome", sa.String(20), nullable=False, server_default="success"), sa.Column("correlation_id", sa.String(120)), sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"), *_timestamps())
    for name, cols in [("ix_notification_audit_events_actor_id", ["actor_id"]), ("ix_notification_audit_events_created", ["created_at"]), ("ix_notification_audit_events_resource", ["resource_type", "resource_id"]), ("ix_notification_audit_events_correlation_id", ["correlation_id"])]: op.create_index(name, "notification_audit_events", cols)


def downgrade():
    for table in ["notification_audit_events", "notification_outbox", "notification_preferences", "notification_provider_events", "notification_delivery_attempts", "notification_messages", "notification_announcements", "notification_template_versions", "notification_templates"]:
        op.drop_table(table)
