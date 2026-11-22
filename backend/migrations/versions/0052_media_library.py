"""Add database metadata for the shared media library."""
from alembic import op
import sqlalchemy as sa

revision = "0052_media_library"
down_revision = "0051_career_path_builder"
branch_labels = None
depends_on = None


def upgrade():
    uuid = sa.UUID()
    op.create_table(
        "media_assets",
        sa.Column("id", uuid, nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("storage_key", sa.String(length=500), nullable=False),
        sa.Column("mime_type", sa.String(length=120), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=180), nullable=False, server_default=""),
        sa.Column("alt_text", sa.String(length=240), nullable=False, server_default=""),
        sa.Column("caption", sa.Text(), nullable=False, server_default=""),
        sa.Column("collection", sa.String(length=80), nullable=False, server_default="general"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="active"),
        sa.Column("uploaded_by", uuid, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["uploaded_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_key"),
    )
    op.create_index("ix_media_assets_status_created", "media_assets", ["status", "created_at"])
    op.create_index("ix_media_assets_collection", "media_assets", ["collection"])
    op.create_index("ix_media_assets_storage_key", "media_assets", ["storage_key"])
    op.create_index("ix_media_assets_uploaded_by", "media_assets", ["uploaded_by"])


def downgrade():
    op.drop_index("ix_media_assets_uploaded_by", table_name="media_assets")
    op.drop_index("ix_media_assets_storage_key", table_name="media_assets")
    op.drop_index("ix_media_assets_collection", table_name="media_assets")
    op.drop_index("ix_media_assets_status_created", table_name="media_assets")
    op.drop_table("media_assets")
