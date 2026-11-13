"""AI tutor conversations, provider policies and usage controls"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0008_ai_tutor"; down_revision="0007_projects_portfolio"; branch_labels=None; depends_on=None
def upgrade():
    uuid=postgresql.UUID(as_uuid=False); ts=sa.DateTime(timezone=True); original=op.create_foreign_key
    def fk(*a,**k): return None if op.get_bind().dialect.name=="sqlite" else original(*a,**k)
    op.create_foreign_key=fk
    def table(name,cols,unique=()): op.create_table(name,*[sa.Column(c[0],c[1],**(c[2] if len(c)>2 else {})) for c in cols],*unique,sa.Column("created_at",ts,server_default=sa.func.now()),sa.Column("updated_at",ts,server_default=sa.func.now()))
    table("ai_conversations",[("id",uuid,{"primary_key":True}),("user_id",uuid,{"nullable":False}),("title",sa.String(180),{"server_default":"New conversation"}),("status",sa.String(20),{"server_default":"active"})]);op.create_index("ix_ai_conversations_user_updated","ai_conversations",["user_id","updated_at"])
    table("ai_messages",[("id",uuid,{"primary_key":True}),("conversation_id",uuid,{"nullable":False}),("role",sa.String(20),{"nullable":False}),("content",sa.Text,{"nullable":False}),("status",sa.String(20),{"server_default":"complete"}),("sequence",sa.Integer,{"server_default":"0"})])
    table("ai_message_contexts",[("id",uuid,{"primary_key":True}),("message_id",uuid,{"nullable":False}),("source_type",sa.String(40),{"nullable":False}),("source_id",uuid,{}),("excerpt",sa.Text,{"server_default":""})])
    table("ai_usage_records",[("id",uuid,{"primary_key":True}),("user_id",uuid,{"nullable":False}),("conversation_id",uuid,{}),("provider",sa.String(50),{"nullable":False}),("model",sa.String(100),{"nullable":False}),("prompt_tokens",sa.Integer,{"server_default":"0"}),("completion_tokens",sa.Integer,{"server_default":"0"}),("estimated_cost",sa.Integer,{"server_default":"0"}),("status",sa.String(30),{"server_default":"complete"})])
    table("ai_provider_configs",[("id",uuid,{"primary_key":True}),("provider",sa.String(50),{"unique":True}),("model",sa.String(100),{}),("enabled",sa.Boolean,{"server_default":sa.false()}),("secret_ref",sa.String(180),{"server_default":"environment-only"})])
    table("ai_model_policies",[("id",uuid,{"primary_key":True}),("model",sa.String(100),{"unique":True}),("enabled",sa.Boolean,{"server_default":sa.false()}),("max_input_tokens",sa.Integer,{"server_default":"4000"}),("max_output_tokens",sa.Integer,{"server_default":"1200"})])
    table("ai_tutor_preferences",[("id",uuid,{"primary_key":True}),("user_id",uuid,{"unique":True}),("language",sa.String(10),{"server_default":"en"}),("show_myanmar",sa.Boolean,{"server_default":sa.false()})])
    table("ai_feedback",[("id",uuid,{"primary_key":True}),("user_id",uuid,{"nullable":False}),("message_id",uuid,{"nullable":False}),("rating",sa.Integer,{"nullable":False}),("comment",sa.Text,{"server_default":""})])
    table("ai_request_logs",[("id",uuid,{"primary_key":True}),("user_id",uuid,{}),("request_type",sa.String(50),{"nullable":False}),("status",sa.String(30),{"nullable":False}),("error_code",sa.String(80),{})])
    table("ai_quota_counters",[("id",uuid,{"primary_key":True}),("user_id",uuid,{"nullable":False}),("quota_date",ts,{"nullable":False}),("request_count",sa.Integer,{"server_default":"0"}),("token_count",sa.Integer,{"server_default":"0"})],[sa.UniqueConstraint("user_id","quota_date")])
def downgrade():
    for name in ["ai_quota_counters","ai_request_logs","ai_feedback","ai_tutor_preferences","ai_model_policies","ai_provider_configs","ai_usage_records","ai_message_contexts","ai_messages","ai_conversations"]:op.drop_table(name)
