"""Add versioned legal-document review and publication workflow."""
from alembic import op
import sqlalchemy as sa
revision = "0054_legal_documents"
down_revision = "0053_contact_messages"
branch_labels = None
depends_on = None
def upgrade():
    uuid = sa.UUID()
    op.create_table("legal_documents", sa.Column("id", uuid, nullable=False), sa.Column("document_type", sa.String(30), nullable=False), sa.Column("current_version_id", uuid, nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("document_type"))
    op.create_index("ix_legal_documents_document_type", "legal_documents", ["document_type"])
    op.create_table("legal_document_versions", sa.Column("id", uuid, nullable=False), sa.Column("document_id", uuid, nullable=False), sa.Column("version", sa.String(40), nullable=False), sa.Column("title", sa.String(180), nullable=False), sa.Column("content", sa.Text(), nullable=False), sa.Column("effective_date", sa.DateTime(timezone=True), nullable=True), sa.Column("review_status", sa.String(20), nullable=False, server_default="draft"), sa.Column("publication_status", sa.String(20), nullable=False, server_default="unpublished"), sa.Column("rejection_reason", sa.Text(), nullable=False, server_default=""), sa.Column("submitted_by", uuid, nullable=True), sa.Column("reviewed_by", uuid, nullable=True), sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True), sa.Column("published_by", uuid, nullable=True), sa.Column("published_at", sa.DateTime(timezone=True), nullable=True), sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False), sa.ForeignKeyConstraint(["document_id"], ["legal_documents.id"], ondelete="CASCADE"), sa.ForeignKeyConstraint(["submitted_by"], ["users.id"], ondelete="SET NULL"), sa.ForeignKeyConstraint(["reviewed_by"], ["users.id"], ondelete="SET NULL"), sa.ForeignKeyConstraint(["published_by"], ["users.id"], ondelete="SET NULL"), sa.PrimaryKeyConstraint("id"), sa.UniqueConstraint("document_id", "version"))
    op.create_index("ix_legal_versions_document_created", "legal_document_versions", ["document_id", "created_at"])
    op.create_index("ix_legal_document_versions_document_id", "legal_document_versions", ["document_id"])
    op.create_index("ix_legal_document_versions_review_status", "legal_document_versions", ["review_status"])
    op.create_index("ix_legal_document_versions_publication_status", "legal_document_versions", ["publication_status"])
def downgrade():
    op.drop_index("ix_legal_document_versions_publication_status", table_name="legal_document_versions"); op.drop_index("ix_legal_document_versions_review_status", table_name="legal_document_versions"); op.drop_index("ix_legal_document_versions_document_id", table_name="legal_document_versions"); op.drop_index("ix_legal_versions_document_created", table_name="legal_document_versions"); op.drop_table("legal_document_versions"); op.drop_index("ix_legal_documents_document_type", table_name="legal_documents"); op.drop_table("legal_documents")
