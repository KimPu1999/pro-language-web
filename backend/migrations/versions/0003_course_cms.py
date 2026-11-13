"""course management CMS fields and workflow tables"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
revision="0003_course_cms"; down_revision="0002_auth_student"; branch_labels=None; depends_on=None
def upgrade():
    add=lambda table, name, typ, **kw: op.add_column(table,sa.Column(name,typ,**kw))
    for name,typ,default in [("description",sa.Text(),""),("icon",sa.String(120),None),("status",sa.String(20),"active"),("display_order",sa.Integer(),"0")]: add("programming_languages",name,typ,nullable=True,server_default=default)
    for name,typ,default in [("description",sa.Text(),""),("status",sa.String(20),"active"),("display_order",sa.Integer(),"0")]: add("course_categories",name,typ,nullable=True,server_default=default)
    for name,typ,default in [("short_description",sa.Text(),""),("thumbnail",sa.String(500),None),("requirements",sa.Text(),""),("status",sa.String(20),"draft"),("created_by",postgresql.UUID(as_uuid=False),None),("updated_by",postgresql.UUID(as_uuid=False),None)]: add("courses",name,typ,nullable=True,server_default=default)
    add("lessons","description",sa.Text(),nullable=True,server_default=""); add("lessons","duration_minutes",sa.Integer(),nullable=True,server_default="10"); add("lessons","status",sa.String(20),nullable=True,server_default="draft")
    for name,typ,default in [("filename",sa.String(180),None),("description",sa.Text(),""),("position",sa.Integer(),"0")]: add("code_examples",name,typ,nullable=True,server_default=default)
    op.execute("UPDATE courses SET status=CASE WHEN published THEN 'published' ELSE 'draft' END WHERE status IS NULL OR status='draft'")
    op.execute("UPDATE lessons SET status=CASE WHEN published THEN 'published' ELSE 'draft' END WHERE status IS NULL OR status='draft'")
    uuid=postgresql.UUID(as_uuid=False)
    op.create_table("course_instructors",sa.Column("course_id",uuid,sa.ForeignKey("courses.id",ondelete="CASCADE"),primary_key=True),sa.Column("user_id",uuid,sa.ForeignKey("users.id",ondelete="CASCADE"),primary_key=True),sa.Column("assigned_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
    op.create_table("course_revisions",sa.Column("id",uuid,primary_key=True),sa.Column("course_id",uuid,sa.ForeignKey("courses.id",ondelete="CASCADE"),nullable=False),sa.Column("changed_by",uuid,sa.ForeignKey("users.id"),nullable=False),sa.Column("status",sa.String(20),nullable=False),sa.Column("snapshot_json",sa.Text,nullable=False),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
    op.create_table("publishing_reviews",sa.Column("id",uuid,primary_key=True),sa.Column("course_id",uuid,sa.ForeignKey("courses.id",ondelete="CASCADE"),nullable=False),sa.Column("reviewer_id",uuid,sa.ForeignKey("users.id"),nullable=False),sa.Column("decision",sa.String(30),nullable=False),sa.Column("note",sa.Text,nullable=False,server_default=""),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
    op.create_table("admin_audit_logs",sa.Column("id",uuid,primary_key=True),sa.Column("actor_id",uuid,sa.ForeignKey("users.id"),nullable=False),sa.Column("action",sa.String(80),nullable=False),sa.Column("entity_type",sa.String(50),nullable=False),sa.Column("entity_id",uuid),sa.Column("metadata_json",sa.Text,nullable=False,server_default="{}"),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
def downgrade():
    for table in ["admin_audit_logs","publishing_reviews","course_revisions","course_instructors"]: op.drop_table(table)
    for table, columns in {"code_examples":["position","description","filename"],"lessons":["status","duration_minutes","description"],"courses":["updated_by","created_by","status","requirements","thumbnail","short_description"],"course_categories":["display_order","status","description"],"programming_languages":["display_order","status","icon","description"]}.items():
        for column in columns: op.drop_column(table,column)
