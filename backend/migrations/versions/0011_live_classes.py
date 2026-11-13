"""live classes, registrations and virtual classroom state"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0011_live_classes";down_revision="0010_community";branch_labels=None;depends_on=None
def upgrade():
 u=postgresql.UUID(as_uuid=True);ts=sa.DateTime(timezone=True)
 def t(n,c,cons=()):op.create_table(n,*[sa.Column(a,b,**x) for a,b,x in c],*cons)
 common=[("created_at",ts,{"server_default":sa.func.now()}),("updated_at",ts,{"server_default":sa.func.now()})]
 t("live_classes",[("id",u,{"primary_key":True}),("created_by",u,{}),("title",sa.String(200),{}),("slug",sa.String(220),{"unique":True}),("description_en",sa.Text,{}),("description_mm",sa.Text,{"nullable":True}),("difficulty",sa.String(30),{}),("capacity",sa.Integer,{"server_default":"30"}),("status",sa.String(20),{"server_default":"draft"}),("published",sa.Boolean,{"server_default":sa.false()})]+common)
 t("live_class_sessions",[("id",u,{"primary_key":True}),("class_id",u,{}),("starts_at",ts,{}),("ends_at",ts,{}),("timezone",sa.String(80),{"server_default":"UTC"}),("status",sa.String(20),{"server_default":"scheduled"})]+common)
 t("live_class_instructors",[("class_id",u,{"primary_key":True}),("user_id",u,{"primary_key":True})])
 t("live_class_registrations",[("id",u,{"primary_key":True}),("session_id",u,{}),("user_id",u,{}),("status",sa.String(20),{"server_default":"registered"})]+common,[sa.UniqueConstraint("session_id","user_id")])
 t("live_class_waitlist",[("id",u,{"primary_key":True}),("session_id",u,{}),("user_id",u,{}),("position",sa.Integer,{}),("status",sa.String(20),{"server_default":"waiting"})]+common,[sa.UniqueConstraint("session_id","user_id")])
 t("live_class_attendance",[("id",u,{"primary_key":True}),("session_id",u,{}),("user_id",u,{}),("joined_at",ts,{"nullable":True}),("left_at",ts,{"nullable":True}),("status",sa.String(20),{"server_default":"present"})]+common,[sa.UniqueConstraint("session_id","user_id")])
 t("live_class_presence_events",[("id",u,{"primary_key":True}),("session_id",u,{}),("user_id",u,{}),("event_key",sa.String(120),{}),("event_type",sa.String(20),{})]+common,[sa.UniqueConstraint("session_id","user_id","event_key")])
 t("live_class_recordings",[("id",u,{"primary_key":True}),("session_id",u,{}),("status",sa.String(20),{"server_default":"processing"}),("storage_key",sa.String(500),{"nullable":True}),("visibility",sa.String(20),{"server_default":"private"})]+common)
 t("live_class_resources",[("id",u,{"primary_key":True}),("class_id",u,{}),("title",sa.String(180),{}),("url",sa.String(500),{})]+common)
 t("live_class_questions",[("id",u,{"primary_key":True}),("session_id",u,{}),("user_id",u,{}),("body",sa.Text,{}),("answered",sa.Boolean,{"server_default":sa.false()}),("pinned",sa.Boolean,{"server_default":sa.false()})]+common)
 t("live_class_chat_messages",[("id",u,{"primary_key":True}),("session_id",u,{}),("user_id",u,{}),("body",sa.Text,{}),("status",sa.String(20),{"server_default":"visible"})]+common)
 t("live_class_code_snapshots",[("id",u,{"primary_key":True}),("session_id",u,{}),("instructor_id",u,{}),("language",sa.String(50),{}),("source_code",sa.Text,{})]+common)
 t("live_class_audit_logs",[("id",u,{"primary_key":True}),("actor_id",u,{"nullable":True}),("session_id",u,{"nullable":True}),("action",sa.String(80),{}),("metadata_json",sa.Text,{"server_default":"{}"})]+common)
 op.create_index("ix_live_class_sessions_start","live_class_sessions",["starts_at","status"]);op.create_index("ix_live_class_chat_session","live_class_chat_messages",["session_id","created_at"])
def downgrade():
 for n in ["live_class_audit_logs","live_class_code_snapshots","live_class_chat_messages","live_class_questions","live_class_resources","live_class_recordings","live_class_presence_events","live_class_attendance","live_class_waitlist","live_class_registrations","live_class_instructors","live_class_sessions","live_classes"]:op.drop_table(n)
