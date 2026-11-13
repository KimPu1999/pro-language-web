"""community, Q&A, groups and moderation"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0010_community"; down_revision="0009_certificates_gamification"; branch_labels=None; depends_on=None
def upgrade():
 u=postgresql.UUID(as_uuid=True);ts=sa.DateTime(timezone=True)
 def t(n,cs,cons=()):op.create_table(n,*[sa.Column(a,b,**c) for a,b,c in cs],*cons)
 common=[("created_at",ts,{"server_default":sa.func.now()}),("updated_at",ts,{"server_default":sa.func.now()})]
 t("community_categories",[("id",u,{"primary_key":True}),("name",sa.String(100),{}),("slug",sa.String(100),{"unique":True}),("description",sa.Text,{"server_default":""})]+common)
 t("community_posts",[("id",u,{"primary_key":True}),("author_id",u,{}),("category_id",u,{"nullable":True}),("title",sa.String(220),{}),("slug",sa.String(240),{"unique":True}),("body",sa.Text,{}),("post_type",sa.String(30),{"server_default":"discussion"}),("visibility",sa.String(20),{"server_default":"public"}),("status",sa.String(20),{"server_default":"published"}),("accepted_answer_id",u,{"nullable":True})]+common)
 t("community_post_tags",[("post_id",u,{"primary_key":True}),("tag",sa.String(50),{"primary_key":True})],[sa.UniqueConstraint("post_id","tag")])
 t("community_answers",[("id",u,{"primary_key":True}),("post_id",u,{}),("author_id",u,{}),("body",sa.Text,{}),("status",sa.String(20),{"server_default":"published"})]+common)
 t("community_comments",[("id",u,{"primary_key":True}),("author_id",u,{}),("post_id",u,{}),("parent_id",u,{"nullable":True}),("body",sa.Text,{}),("status",sa.String(20),{"server_default":"published"})]+common)
 t("community_votes",[("id",u,{"primary_key":True}),("user_id",u,{}),("target_type",sa.String(20),{}),("target_id",u,{}),("value",sa.Integer,{"server_default":"1"})]+common,[sa.UniqueConstraint("user_id","target_type","target_id")])
 t("community_bookmarks",[("id",u,{"primary_key":True}),("user_id",u,{}),("post_id",u,{})]+common,[sa.UniqueConstraint("user_id","post_id")])
 t("community_snippets",[("id",u,{"primary_key":True}),("author_id",u,{}),("title",sa.String(180),{}),("language",sa.String(50),{}),("source_code",sa.Text,{}),("description",sa.Text,{"server_default":""}),("visibility",sa.String(20),{"server_default":"public"}),("status",sa.String(20),{"server_default":"published"})]+common)
 t("study_groups",[("id",u,{"primary_key":True}),("owner_id",u,{}),("name",sa.String(160),{}),("slug",sa.String(180),{"unique":True}),("description",sa.Text,{}),("visibility",sa.String(20),{"server_default":"public"}),("status",sa.String(20),{"server_default":"active"})]+common)
 t("study_group_members",[("id",u,{"primary_key":True}),("group_id",u,{}),("user_id",u,{}),("role",sa.String(20),{"server_default":"member"})]+common,[sa.UniqueConstraint("group_id","user_id")])
 t("community_reports",[("id",u,{"primary_key":True}),("reporter_id",u,{}),("target_type",sa.String(30),{}),("target_id",u,{}),("reason",sa.Text,{}),("status",sa.String(20),{"server_default":"open"})]+common)
 t("user_blocks",[("id",u,{"primary_key":True}),("user_id",u,{}),("blocked_user_id",u,{})]+common,[sa.UniqueConstraint("user_id","blocked_user_id")])
 t("community_notifications",[("id",u,{"primary_key":True}),("user_id",u,{}),("notification_type",sa.String(40),{}),("target_id",u,{"nullable":True}),("preview",sa.String(240),{"server_default":""}),("read_at",ts,{"nullable":True})]+common)
 for n,tbl,cols in [("ix_community_posts_feed","community_posts",["visibility","created_at"]),("ix_community_notifications_user","community_notifications",["user_id","read_at"]),("ix_community_reports_status","community_reports",["status"])]:op.create_index(n,tbl,cols)
def downgrade():
 for n in ["community_notifications","user_blocks","community_reports","study_group_members","study_groups","community_snippets","community_bookmarks","community_votes","community_comments","community_answers","community_post_tags","community_posts","community_categories"]:op.drop_table(n)
