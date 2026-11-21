"""Set the product identity to Learn-Coding without changing user content."""
from alembic import op
import sqlalchemy as sa

revision = "0044_learn_coding_branding"
down_revision = "0043_languages_platform_branding"
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    bind.execute(
        sa.text("UPDATE platform_settings SET value_json = replace(replace(value_json, :old, :new), :legacy, :new) WHERE key = 'branding'"),
        {"old": "Languages-Platform", "legacy": "Language-Platform", "new": "Learn-Coding"},
    )

def downgrade():
    pass
