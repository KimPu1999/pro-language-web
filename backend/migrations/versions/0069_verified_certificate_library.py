"""Add verified certificate evidence, localized artifacts, and template controls."""
from alembic import op
import sqlalchemy as sa

revision = "0069_verified_certificate_library"
down_revision = "0068_card_display_defaults"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("certificate_templates", sa.Column("heading", sa.String(180), nullable=True))
    op.add_column("certificate_templates", sa.Column("logo_url", sa.String(500), nullable=True))
    op.add_column("certificate_templates", sa.Column("accent_color", sa.String(20), server_default="#6d5dfc", nullable=False))
    op.add_column("certificate_policies", sa.Column("rules_json", sa.Text(), server_default="{}", nullable=False))
    op.add_column("issued_certificates", sa.Column("evidence_json", sa.Text(), server_default="{}", nullable=False))
    op.add_column("issued_certificates", sa.Column("locale", sa.String(10), server_default="en", nullable=False))
    op.add_column("issued_certificates", sa.Column("recipient_visible", sa.Boolean(), server_default=sa.false(), nullable=False))
    op.add_column("issued_certificates", sa.Column("completion_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("issued_certificates", sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True))


def downgrade():
    for table, columns in {
        "issued_certificates": ("expires_at", "completion_at", "recipient_visible", "locale", "evidence_json"),
        "certificate_policies": ("rules_json",),
        "certificate_templates": ("accent_color", "logo_url", "heading"),
    }.items():
        for column in columns:
            op.drop_column(table, column)
