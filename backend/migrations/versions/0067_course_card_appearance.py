"""Add editable course card appearance metadata and stable media references."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0067_course_card_appearance"
down_revision = "0066_fix_linux_quiz_locale"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("courses", sa.Column("display_title", sa.String(180), nullable=False, server_default=""))
    op.add_column("courses", sa.Column("technology_name", sa.String(100), nullable=False, server_default=""))
    op.add_column("courses", sa.Column("card_short_description", sa.Text(), nullable=False, server_default=""))
    op.add_column("courses", sa.Column("card_image_alt", sa.String(240), nullable=False, server_default=""))
    uuid = postgresql.UUID(as_uuid=False)
    op.add_column("courses", sa.Column("card_logo_asset_id", uuid, sa.ForeignKey("media_assets.id", ondelete="SET NULL"), nullable=True))
    op.add_column("courses", sa.Column("card_cover_asset_id", uuid, sa.ForeignKey("media_assets.id", ondelete="SET NULL"), nullable=True))
    op.add_column("courses", sa.Column("show_rating", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("courses", sa.Column("is_featured", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("courses", sa.Column("card_sort_order", sa.Integer(), nullable=False, server_default="0"))
    op.create_index("ix_courses_card_logo_asset_id", "courses", ["card_logo_asset_id"])
    op.create_index("ix_courses_card_cover_asset_id", "courses", ["card_cover_asset_id"])
    op.create_index("ix_courses_published_card_sort", "courses", ["published", "is_featured", "card_sort_order"])
    op.execute("UPDATE courses SET display_title = title WHERE display_title = ''")
    op.execute("UPDATE courses SET technology_name = COALESCE((SELECT name FROM programming_languages WHERE programming_languages.id = courses.language_id), '') WHERE technology_name = ''")
    op.execute("UPDATE courses SET card_short_description = short_description WHERE card_short_description = ''")

def downgrade():
    op.drop_index("ix_courses_published_card_sort", table_name="courses")
    op.drop_index("ix_courses_card_cover_asset_id", table_name="courses")
    op.drop_index("ix_courses_card_logo_asset_id", table_name="courses")
    for name in ("card_sort_order", "is_featured", "show_rating", "card_cover_asset_id", "card_logo_asset_id", "card_image_alt", "card_short_description", "technology_name", "display_title"):
        op.drop_column("courses", name)
