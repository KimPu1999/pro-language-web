"""phase 25 durable collaboration state"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0023_collaboration"
down_revision = "0022_learning_labs"
branch_labels = None
depends_on = None

def upgrade():
    u = postgresql.UUID(as_uuid=False)
    ts = sa.DateTime(timezone=True)
    def fk(target, delete=None): return sa.ForeignKey(target, ondelete=delete)
    def table(name, cols, uniques=(), indexes=()):
        op.create_table(name, sa.Column("id", u, primary_key=True), *cols,
                        sa.Column("created_at", ts, server_default=sa.func.now()),
                        sa.Column("updated_at", ts, server_default=sa.func.now()),
                        *[sa.UniqueConstraint(*x) for x in uniques])
        for columns in indexes:
            op.create_index("ix_" + name + "_" + "_".join(columns), name, list(columns))
    table("collaboration_rooms", [sa.Column("organization_id",u,fk("organizations.id","CASCADE")),sa.Column("owner_id",u,fk("users.id","CASCADE"),nullable=False),sa.Column("name",sa.String(180),nullable=False),sa.Column("description",sa.Text,server_default=""),sa.Column("visibility",sa.String(20),server_default="private"),sa.Column("status",sa.String(20),server_default="active")], indexes=[("organization_id","status")])
    table("collaboration_room_members", [sa.Column("room_id",u,fk("collaboration_rooms.id","CASCADE"),nullable=False),sa.Column("user_id",u,fk("users.id","CASCADE"),nullable=False),sa.Column("role",sa.String(30),server_default="member"),sa.Column("status",sa.String(20),server_default="active")], uniques=[("room_id","user_id")])
    table("collaboration_invitations", [sa.Column("room_id",u,fk("collaboration_rooms.id","CASCADE"),nullable=False),sa.Column("invited_user_id",u,fk("users.id","CASCADE"),nullable=False),sa.Column("invited_by",u,fk("users.id","CASCADE"),nullable=False),sa.Column("status",sa.String(20),server_default="pending"),sa.Column("expires_at",ts,nullable=False)], indexes=[("room_id","status")])
    table("collaboration_sessions", [sa.Column("room_id",u,fk("collaboration_rooms.id","CASCADE"),nullable=False),sa.Column("started_by",u,fk("users.id","CASCADE"),nullable=False),sa.Column("status",sa.String(20),server_default="active"),sa.Column("ended_at",ts)])
    table("collaboration_documents", [sa.Column("room_id",u,fk("collaboration_rooms.id","CASCADE"),nullable=False),sa.Column("path",sa.String(240),nullable=False),sa.Column("language",sa.String(40),nullable=False),sa.Column("state_bytes",sa.LargeBinary,server_default=sa.text("'\\x'")),sa.Column("version",sa.Integer,server_default="0")], uniques=[("room_id","path")])
    table("collaboration_document_updates", [sa.Column("document_id",u,fk("collaboration_documents.id","CASCADE"),nullable=False),sa.Column("actor_id",u,fk("users.id","CASCADE"),nullable=False),sa.Column("sequence",sa.Integer,nullable=False),sa.Column("update_bytes",sa.LargeBinary,nullable=False)], indexes=[("document_id","sequence")])
    table("collaboration_snapshots", [sa.Column("document_id",u,fk("collaboration_documents.id","CASCADE"),nullable=False),sa.Column("created_by",u,fk("users.id","CASCADE"),nullable=False),sa.Column("version",sa.Integer,nullable=False),sa.Column("state_bytes",sa.LargeBinary,nullable=False)], indexes=[("document_id","version")])
    table("collaboration_presence_events", [sa.Column("room_id",u,fk("collaboration_rooms.id","CASCADE"),nullable=False),sa.Column("user_id",u,fk("users.id","CASCADE"),nullable=False),sa.Column("event_type",sa.String(30),nullable=False),sa.Column("payload_json",sa.Text,server_default="{}")], indexes=[("room_id","created_at")])
    table("collaboration_chat_messages", [sa.Column("room_id",u,fk("collaboration_rooms.id","CASCADE"),nullable=False),sa.Column("sender_id",u,fk("users.id","CASCADE"),nullable=False),sa.Column("body",sa.Text,nullable=False),sa.Column("removed_at",ts)], indexes=[("room_id","created_at")])
    table("collaboration_pair_sessions", [sa.Column("room_id",u,fk("collaboration_rooms.id","CASCADE"),nullable=False),sa.Column("driver_id",u,fk("users.id","CASCADE"),nullable=False),sa.Column("navigator_id",u,fk("users.id","SET NULL")),sa.Column("status",sa.String(20),server_default="active")])
    table("collaboration_pair_role_events", [sa.Column("pair_session_id",u,fk("collaboration_pair_sessions.id","CASCADE"),nullable=False),sa.Column("actor_id",u,fk("users.id","CASCADE"),nullable=False),sa.Column("from_user_id",u,fk("users.id","SET NULL")),sa.Column("to_user_id",u,fk("users.id","SET NULL"))])
    table("collaboration_execution_jobs", [sa.Column("room_id",u,fk("collaboration_rooms.id","CASCADE"),nullable=False),sa.Column("requested_by",u,fk("users.id","CASCADE"),nullable=False),sa.Column("idempotency_key",sa.String(180),nullable=False),sa.Column("status",sa.String(30),server_default="runner_unavailable"),sa.Column("failure_reason",sa.Text)], uniques=[("room_id","idempotency_key")], indexes=[("room_id","status")])
    table("collaboration_debugging_notes", [sa.Column("room_id",u,fk("collaboration_rooms.id","CASCADE"),nullable=False),sa.Column("author_id",u,fk("users.id","CASCADE"),nullable=False),sa.Column("body",sa.Text,nullable=False)], indexes=[("room_id","created_at")])
    table("collaboration_ai_interactions", [sa.Column("room_id",u,fk("collaboration_rooms.id","CASCADE"),nullable=False),sa.Column("requested_by",u,fk("users.id","CASCADE"),nullable=False),sa.Column("request_type",sa.String(40),nullable=False),sa.Column("status",sa.String(30),server_default="unavailable")])
    table("collaboration_recording_consents", [sa.Column("session_id",u,fk("collaboration_sessions.id","CASCADE"),nullable=False),sa.Column("user_id",u,fk("users.id","CASCADE"),nullable=False),sa.Column("consented",sa.Boolean,server_default=sa.false()),sa.Column("withdrawn_at",ts)], uniques=[("session_id","user_id")])
    table("collaboration_recordings", [sa.Column("session_id",u,fk("collaboration_sessions.id","CASCADE"),nullable=False),sa.Column("status",sa.String(20),server_default="disabled"),sa.Column("storage_key",sa.String(500)),sa.Column("retention_until",ts)])
    table("collaboration_session_feedback", [sa.Column("session_id",u,fk("collaboration_sessions.id","CASCADE"),nullable=False),sa.Column("author_id",u,fk("users.id","CASCADE"),nullable=False),sa.Column("rating",sa.Integer),sa.Column("comment",sa.Text,server_default="")], uniques=[("session_id","author_id")])
    table("collaboration_audit_logs", [sa.Column("organization_id",u,fk("organizations.id","SET NULL")),sa.Column("room_id",u,fk("collaboration_rooms.id","SET NULL")),sa.Column("actor_id",u,fk("users.id","SET NULL")),sa.Column("action",sa.String(100),nullable=False),sa.Column("metadata_json",sa.Text,server_default="{}")], indexes=[("room_id","created_at")])

def downgrade():
    for name in ["collaboration_audit_logs","collaboration_session_feedback","collaboration_recordings","collaboration_recording_consents","collaboration_ai_interactions","collaboration_debugging_notes","collaboration_execution_jobs","collaboration_pair_role_events","collaboration_pair_sessions","collaboration_chat_messages","collaboration_presence_events","collaboration_snapshots","collaboration_document_updates","collaboration_documents","collaboration_sessions","collaboration_invitations","collaboration_room_members","collaboration_rooms"]:
        op.drop_table(name)
