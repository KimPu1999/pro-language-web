"""phase 28 mobile offline learning records"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0030_mobile_offline"
down_revision = "0029_cybersecurity_training"
branch_labels = None
depends_on = None
u = postgresql.UUID(as_uuid=False)
ts = sa.DateTime(timezone=True)
def fk(name, ondelete="CASCADE"): return sa.ForeignKey(name, ondelete=ondelete)
def common(): return [sa.Column("created_at", ts, server_default=sa.func.now()), sa.Column("updated_at", ts, server_default=sa.func.now())]

def upgrade():
    op.create_table("mobile_device_registrations", sa.Column("id", u, primary_key=True), sa.Column("user_id", u, fk("users.id"), nullable=False), sa.Column("device_id", sa.String(180), nullable=False), sa.Column("platform", sa.String(30), nullable=False), sa.Column("last_seen_at", ts, server_default=sa.func.now()), *common(), sa.UniqueConstraint("user_id", "device_id"))
    op.create_index("ix_mobile_devices_user_last_seen", "mobile_device_registrations", ["user_id", "last_seen_at"])
    op.create_table("mobile_push_subscriptions", sa.Column("id", u, primary_key=True), sa.Column("user_id", u, fk("users.id"), nullable=False), sa.Column("endpoint", sa.String(2000), nullable=False), sa.Column("p256dh", sa.String(500), nullable=False), sa.Column("auth", sa.String(500), nullable=False), sa.Column("active", sa.Boolean, server_default=sa.true()), *common(), sa.UniqueConstraint("user_id", "endpoint"))
    op.create_index("ix_mobile_push_user_active", "mobile_push_subscriptions", ["user_id", "active"])
    op.create_table("mobile_notification_preferences", sa.Column("id", u, primary_key=True), sa.Column("user_id", u, fk("users.id"), nullable=False, unique=True), sa.Column("enabled", sa.Boolean, server_default=sa.false()), sa.Column("quiet_hours_json", sa.Text, server_default="{}"), sa.Column("categories_json", sa.Text, server_default="[]"), *common())
    op.create_table("offline_content_versions", sa.Column("id", u, primary_key=True), sa.Column("course_id", u, fk("courses.id"), nullable=False), sa.Column("version", sa.String(80), nullable=False), sa.Column("checksum", sa.String(128), nullable=False), sa.Column("status", sa.String(30), server_default="published"), *common(), sa.UniqueConstraint("course_id", "version"))
    op.create_table("offline_download_policies", sa.Column("id", u, primary_key=True), sa.Column("course_id", u, fk("courses.id"), nullable=False, unique=True), sa.Column("enabled", sa.Boolean, server_default=sa.true()), sa.Column("max_age_days", sa.Integer, server_default="30"), sa.Column("allow_images", sa.Boolean, server_default=sa.true()), sa.Column("updated_by", u, fk("users.id", "SET NULL")), *common())
    op.create_table("offline_content_manifests", sa.Column("id", u, primary_key=True), sa.Column("user_id", u, fk("users.id"), nullable=False), sa.Column("course_id", u, fk("courses.id"), nullable=False), sa.Column("content_version", sa.String(80), nullable=False), sa.Column("status", sa.String(30), server_default="requested"), sa.Column("size_bytes", sa.Integer, server_default="0"), *common(), sa.UniqueConstraint("user_id", "course_id"))
    op.create_index("ix_offline_manifests_user_status", "offline_content_manifests", ["user_id", "status"])
    op.create_table("offline_sync_events", sa.Column("id", u, primary_key=True), sa.Column("user_id", u, fk("users.id"), nullable=False), sa.Column("event_id", sa.String(180), nullable=False), sa.Column("event_type", sa.String(50), nullable=False), sa.Column("lesson_id", u, fk("lessons.id", "SET NULL")), sa.Column("content_version", sa.String(80)), sa.Column("payload_json", sa.Text, server_default="{}"), sa.Column("status", sa.String(30), server_default="pending"), sa.Column("processed_at", ts), *common(), sa.UniqueConstraint("user_id", "event_id"))
    op.create_index("ix_offline_sync_user_status", "offline_sync_events", ["user_id", "status"])
    op.create_table("offline_sync_conflicts", sa.Column("id", u, primary_key=True), sa.Column("sync_event_id", u, fk("offline_sync_events.id"), nullable=False, unique=True), sa.Column("user_id", u, fk("users.id"), nullable=False), sa.Column("reason", sa.String(60), nullable=False), sa.Column("detail", sa.Text, server_default=""), sa.Column("resolved_at", ts), *common())
    op.create_table("offline_learning_activity", sa.Column("id", u, primary_key=True), sa.Column("user_id", u, fk("users.id"), nullable=False), sa.Column("event_type", sa.String(50), nullable=False), sa.Column("lesson_id", u, fk("lessons.id", "SET NULL")), sa.Column("occurred_at", ts, server_default=sa.func.now()), *common())
    op.create_index("ix_offline_activity_user_day", "offline_learning_activity", ["user_id", "occurred_at"])
    op.create_table("offline_content_bookmarks", sa.Column("id", u, primary_key=True), sa.Column("user_id", u, fk("users.id"), nullable=False), sa.Column("lesson_id", u, fk("lessons.id"), nullable=False), sa.Column("note", sa.String(500), server_default=""), *common(), sa.UniqueConstraint("user_id", "lesson_id"))
    op.create_table("mobile_learning_preferences", sa.Column("id", u, primary_key=True), sa.Column("user_id", u, fk("users.id"), nullable=False, unique=True), sa.Column("language", sa.String(5), server_default="en"), sa.Column("reduced_data", sa.Boolean, server_default=sa.false()), sa.Column("reduced_motion", sa.Boolean, server_default=sa.false()), sa.Column("text_scale", sa.Integer, server_default="100"), *common())
    op.create_table("mobile_usage_aggregates", sa.Column("id", u, primary_key=True), sa.Column("user_id", u, fk("users.id"), nullable=False), sa.Column("day", sa.String(10), nullable=False), sa.Column("metric", sa.String(60), nullable=False), sa.Column("value", sa.Integer, server_default="0"), *common(), sa.UniqueConstraint("user_id", "day", "metric"))
    op.create_table("mobile_delivery_events", sa.Column("id", u, primary_key=True), sa.Column("user_id", u, fk("users.id", "SET NULL")), sa.Column("event_type", sa.String(60), nullable=False), sa.Column("status", sa.String(30), nullable=False), sa.Column("metadata_json", sa.Text, server_default="{}"), *common())
    op.create_table("mobile_platform_audit_logs", sa.Column("id", u, primary_key=True), sa.Column("actor_id", u, fk("users.id", "SET NULL")), sa.Column("action", sa.String(100), nullable=False), sa.Column("metadata_json", sa.Text, server_default="{}"), *common())

def downgrade():
    for table in ["mobile_platform_audit_logs", "mobile_delivery_events", "mobile_usage_aggregates", "mobile_learning_preferences", "offline_content_bookmarks", "offline_learning_activity", "offline_sync_conflicts", "offline_sync_events", "offline_content_manifests", "offline_download_policies", "offline_content_versions", "mobile_notification_preferences", "mobile_push_subscriptions", "mobile_device_registrations"]:
        op.drop_table(table)
