"""Add durable media library state, references, folders, and audit records."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0062_media_library_hardening"
down_revision = "0061_ai_tutor_hardening"
branch_labels = None
depends_on = None


def upgrade():
    u = postgresql.UUID(as_uuid=False)
    op.create_table(
        "media_folders",
        sa.Column("id", u, primary_key=True),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("parent_id", u, sa.ForeignKey("media_folders.id", ondelete="CASCADE"), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_by", u, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.UniqueConstraint("parent_id", "name"),
    )
    op.create_index("ix_media_folders_parent_id", "media_folders", ["parent_id"])
    op.create_index("ix_media_folders_status", "media_folders", ["status"])
    for name, column_type in (("processing_status", sa.String(24)), ("visibility", sa.String(20)), ("checksum", sa.String(64))):
        op.add_column("media_assets", sa.Column(name, column_type, nullable=True, server_default="ready" if name == "processing_status" else "public" if name == "visibility" else None))
    op.add_column("media_assets", sa.Column("folder_id", u, sa.ForeignKey("media_folders.id", ondelete="SET NULL"), nullable=True))
    op.add_column("media_assets", sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True))
    op.alter_column("media_assets", "processing_status", nullable=False, server_default=None)
    op.alter_column("media_assets", "visibility", nullable=False, server_default=None)
    op.create_index("ix_media_assets_processing_status", "media_assets", ["processing_status"])
    op.create_index("ix_media_assets_visibility", "media_assets", ["visibility"])
    op.create_index("ix_media_assets_folder_id", "media_assets", ["folder_id"])
    op.create_index("ix_media_assets_checksum", "media_assets", ["checksum"])
    op.create_table(
        "media_references",
        sa.Column("id", u, primary_key=True),
        sa.Column("asset_id", u, sa.ForeignKey("media_assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("resource_type", sa.String(60), nullable=False),
        sa.Column("resource_id", sa.String(120), nullable=False),
        sa.Column("field_name", sa.String(80), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.UniqueConstraint("asset_id", "resource_type", "resource_id", "field_name"),
    )
    op.create_index("ix_media_references_asset_id", "media_references", ["asset_id"])
    op.create_table(
        "media_variants",
        sa.Column("id", u, primary_key=True),
        sa.Column("asset_id", u, sa.ForeignKey("media_assets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("variant_key", sa.String(60), nullable=False),
        sa.Column("storage_key", sa.String(500), nullable=False, unique=True),
        sa.Column("mime_type", sa.String(120), nullable=False),
        sa.Column("size_bytes", sa.Integer(), nullable=False),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="ready"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.UniqueConstraint("asset_id", "variant_key"),
    )
    op.create_index("ix_media_variants_asset_id", "media_variants", ["asset_id"])
    op.create_index("ix_media_variants_status", "media_variants", ["status"])
    op.create_table(
        "media_upload_sessions",
        sa.Column("id", u, primary_key=True),
        sa.Column("original_filename", sa.String(255), nullable=False),
        sa.Column("status", sa.String(24), nullable=False, server_default="pending"),
        sa.Column("bytes_received", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=False, server_default=""),
        sa.Column("storage_key", sa.String(500), nullable=True),
        sa.Column("created_by", u, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index("ix_media_upload_sessions_status", "media_upload_sessions", ["status"])
    op.create_index("ix_media_upload_sessions_created_by", "media_upload_sessions", ["created_by"])
    op.create_table(
        "media_audit_events",
        sa.Column("id", u, primary_key=True),
        sa.Column("asset_id", u, sa.ForeignKey("media_assets.id", ondelete="SET NULL"), nullable=True),
        sa.Column("actor_id", u, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(60), nullable=False),
        sa.Column("outcome", sa.String(20), nullable=False, server_default="success"),
        sa.Column("metadata_json", sa.Text(), nullable=False, server_default="{}"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index("ix_media_audit_events_asset_id", "media_audit_events", ["asset_id"])
    op.create_index("ix_media_audit_events_actor_id", "media_audit_events", ["actor_id"])
    op.create_table(
        "external_resource_links",
        sa.Column("id", u, primary_key=True),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("url", sa.String(2000), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("locale", sa.String(10), nullable=False, server_default="en"),
        sa.Column("resource_type", sa.String(60), nullable=False, server_default="general"),
        sa.Column("resource_id", sa.String(120), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("created_by", u, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
    )
    op.create_index("ix_external_resource_links_status", "external_resource_links", ["status"])


def downgrade():
    op.drop_index("ix_external_resource_links_status", table_name="external_resource_links")
    op.drop_table("external_resource_links")
    op.drop_index("ix_media_audit_events_actor_id", table_name="media_audit_events")
    op.drop_index("ix_media_audit_events_asset_id", table_name="media_audit_events")
    op.drop_table("media_audit_events")
    op.drop_index("ix_media_upload_sessions_created_by", table_name="media_upload_sessions")
    op.drop_index("ix_media_upload_sessions_status", table_name="media_upload_sessions")
    op.drop_table("media_upload_sessions")
    op.drop_index("ix_media_variants_status", table_name="media_variants")
    op.drop_index("ix_media_variants_asset_id", table_name="media_variants")
    op.drop_table("media_variants")
    op.drop_index("ix_media_references_asset_id", table_name="media_references")
    op.drop_table("media_references")
    for index in ("ix_media_assets_checksum", "ix_media_assets_folder_id", "ix_media_assets_visibility", "ix_media_assets_processing_status"):
        op.drop_index(index, table_name="media_assets")
    op.drop_column("media_assets", "deleted_at")
    op.drop_column("media_assets", "folder_id")
    op.drop_column("media_assets", "checksum")
    op.drop_column("media_assets", "visibility")
    op.drop_column("media_assets", "processing_status")
    op.drop_index("ix_media_folders_status", table_name="media_folders")
    op.drop_index("ix_media_folders_parent_id", table_name="media_folders")
    op.drop_table("media_folders")
