"""Add the public contact inbox without changing existing records."""
from alembic import op
import sqlalchemy as sa
revision = "0053_contact_messages"
down_revision = "0052_media_library"
branch_labels = None
depends_on = None
def upgrade():
    uuid = sa.UUID()
    op.create_table("contact_messages", sa.Column("id", uuid, nullable=False), sa.Column("name", sa.String(120), nullable=False), sa.Column("email", sa.String(320), nullable=False), sa.Column("subject", sa.String(180), nullable=False), sa.Column("message", sa.Text(), nullable=False), sa.Column("status", sa.String(20), nullable=False, server_default="new"), sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True), sa.Column("resolved_by", uuid, nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.ForeignKeyConstraint(["resolved_by"], ["users.id"], ondelete="SET NULL"), sa.PrimaryKeyConstraint("id"))
    op.create_index("ix_contact_messages_status_created", "contact_messages", ["status", "created_at"])
    op.create_index("ix_contact_messages_email", "contact_messages", ["email"])
def downgrade():
    op.drop_index("ix_contact_messages_email", table_name="contact_messages")
    op.drop_index("ix_contact_messages_status_created", table_name="contact_messages")
    op.drop_table("contact_messages")
