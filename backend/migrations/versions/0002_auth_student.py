"""authentication and student learning state"""
from alembic import op
import sqlalchemy as sa
revision="0002_auth_student"; down_revision="0001_initial"; branch_labels=None; depends_on=None
def upgrade():
    uuid=sa.String(36)
    for column, typ in [("email_normalized",sa.String(320)),("role",sa.String(30)),("account_status",sa.String(30)),("email_verified_at",sa.DateTime(timezone=True)),("last_login_at",sa.DateTime(timezone=True)),("password_changed_at",sa.DateTime(timezone=True))]: op.add_column("users",sa.Column(column,typ,nullable=True))
    op.execute("UPDATE users SET email_normalized=lower(trim(email)) WHERE email_normalized IS NULL")
    op.execute("UPDATE users SET role='student' WHERE role IS NULL")
    op.execute("UPDATE users SET account_status='active' WHERE account_status IS NULL")
    op.create_index("ix_users_email_normalized","users",["email_normalized"],unique=True)
    op.create_table("user_profiles",sa.Column("id",uuid,primary_key=True),sa.Column("user_id",uuid,sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False,unique=True),sa.Column("avatar_url",sa.String(500)),sa.Column("bio",sa.Text),sa.Column("learning_interests",sa.Text,nullable=False,server_default=""),sa.Column("preferred_language",sa.String(80)),sa.Column("learning_level",sa.String(30)),sa.Column("show_myanmar",sa.Boolean,nullable=False,server_default=sa.false()),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
    for table in ["auth_sessions","email_verification_tokens","password_reset_tokens"]:
        op.create_table(table,sa.Column("id",uuid,primary_key=True),sa.Column("user_id",uuid,sa.ForeignKey("users.id",ondelete="CASCADE"),nullable=False),sa.Column("token_hash",sa.String(128),nullable=False,unique=True),sa.Column("expires_at",sa.DateTime(timezone=True),nullable=False),sa.Column("revoked_at",sa.DateTime(timezone=True)) if table=="auth_sessions" else sa.Column("used_at",sa.DateTime(timezone=True)),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
        op.create_index(f"ix_{table}_user_id",table,["user_id"]); op.create_index(f"ix_{table}_token_hash",table,["token_hash"],unique=True)
    op.create_table("security_audit_logs",sa.Column("id",uuid,primary_key=True),sa.Column("user_id",uuid,sa.ForeignKey("users.id",ondelete="SET NULL")),sa.Column("event",sa.String(80),nullable=False),sa.Column("ip_address",sa.String(64)),sa.Column("metadata_json",sa.Text,nullable=False,server_default="{}"),sa.Column("created_at",sa.DateTime(timezone=True),server_default=sa.func.now()),sa.Column("updated_at",sa.DateTime(timezone=True),server_default=sa.func.now()))
    op.add_column("lesson_progress",sa.Column("last_visited_at",sa.DateTime(timezone=True),server_default=sa.func.now(),nullable=True))
def downgrade():
    op.drop_column("lesson_progress","last_visited_at")
    for table in ["security_audit_logs","password_reset_tokens","email_verification_tokens","auth_sessions","user_profiles"]: op.drop_table(table)
    op.drop_index("ix_users_email_normalized",table_name="users")
    for column in ["password_changed_at","last_login_at","email_verified_at","account_status","role","email_normalized"]: op.drop_column("users",column)
