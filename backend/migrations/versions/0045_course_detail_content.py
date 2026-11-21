"""Add course detail metadata and managed FAQs.

All additions are nullable-or-defaulted and preserve existing course rows.
"""
from alembic import op
import sqlalchemy as sa

revision = "0045_course_detail_content"
down_revision = "0044_learn_coding_branding"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("courses", sa.Column("target_audience", sa.Text(), nullable=False, server_default=""))
    op.add_column("courses", sa.Column("technologies", sa.Text(), nullable=False, server_default=""))
    op.add_column("courses", sa.Column("seo_title", sa.String(length=180), nullable=False, server_default=""))
    op.add_column("courses", sa.Column("seo_description", sa.Text(), nullable=False, server_default=""))
    op.create_table(
        "course_faqs",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("course_id", sa.UUID(), nullable=False),
        sa.Column("question", sa.String(length=500), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="published"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_course_faqs_course_id", "course_faqs", ["course_id"])
    op.create_index("ix_course_faqs_course_status_position", "course_faqs", ["course_id", "status", "position"])


def downgrade():
    op.drop_index("ix_course_faqs_course_status_position", table_name="course_faqs")
    op.drop_index("ix_course_faqs_course_id", table_name="course_faqs")
    op.drop_table("course_faqs")
    op.drop_column("courses", "seo_description")
    op.drop_column("courses", "seo_title")
    op.drop_column("courses", "technologies")
    op.drop_column("courses", "target_audience")
