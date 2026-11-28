"""Store bilingual module descriptions and learning objectives."""
from alembic import op
import sqlalchemy as sa

revision = "0075_course_module_localization"
down_revision = "0074_review_draft_link"
branch_labels = None
depends_on = None


def upgrade():
    for name in ("title_mm", "description", "description_mm", "learning_objectives", "learning_objectives_mm"):
        op.add_column("course_modules", sa.Column(name, sa.Text() if name != "title_mm" else sa.String(180), nullable=False, server_default=""))


def downgrade():
    for name in ("learning_objectives_mm", "learning_objectives", "description_mm", "description", "title_mm"):
        op.drop_column("course_modules", name)
