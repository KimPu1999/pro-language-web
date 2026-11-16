"""Rename legacy public branding values to Languages-Platform."""
from alembic import op
import sqlalchemy as sa

revision = "0043_languages_platform_branding"
down_revision = "0042_platform_settings"
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    for legacy in ("Learn-Coding", "Language-Platform"):
        bind.execute(
            sa.text("UPDATE platform_settings SET value_json = replace(value_json, :legacy, :current) WHERE key = 'branding'"),
            {"legacy": legacy, "current": "Languages-Platform"},
        )

def downgrade():
    pass
