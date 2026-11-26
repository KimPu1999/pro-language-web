"""Add course-scoped syntax references and ordered examples."""
from alembic import op
import sqlalchemy as sa

revision = "0055_syntax_references"
down_revision = "0054_legal_documents"
branch_labels = None
depends_on = None


def upgrade():
    uuid = sa.UUID()
    op.create_table(
        "syntax_references",
        sa.Column("id", uuid, nullable=False),
        sa.Column("course_id", uuid, nullable=False),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("slug", sa.String(180), nullable=False),
        sa.Column("category", sa.String(100), nullable=False, server_default="Basics"),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("basic_syntax", sa.Text(), nullable=False, server_default=""),
        sa.Column("when_to_use", sa.Text(), nullable=False, server_default=""),
        sa.Column("important_notes", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("course_id", "slug"),
    )
    op.create_index("ix_syntax_references_course_id", "syntax_references", ["course_id"])
    op.create_index("ix_syntax_references_status", "syntax_references", ["status"])
    op.create_index("ix_syntax_references_course_status_order", "syntax_references", ["course_id", "status", "display_order"])
    op.create_table(
        "syntax_reference_examples",
        sa.Column("id", uuid, nullable=False),
        sa.Column("reference_id", uuid, nullable=False),
        sa.Column("example_number", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(180), nullable=False),
        sa.Column("code", sa.Text(), nullable=False),
        sa.Column("language", sa.String(50), nullable=False),
        sa.Column("expected_output", sa.Text(), nullable=False, server_default=""),
        sa.Column("explanation", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["reference_id"], ["syntax_references.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference_id", "example_number"),
    )
    op.create_index("ix_syntax_reference_examples_reference_id", "syntax_reference_examples", ["reference_id"])
    op.create_index("ix_syntax_examples_reference_order", "syntax_reference_examples", ["reference_id", "example_number"])
    op.create_table(
        "lesson_syntax_references",
        sa.Column("lesson_id", uuid, nullable=False),
        sa.Column("reference_id", uuid, nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reference_id"], ["syntax_references.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("lesson_id", "reference_id"),
    )


def downgrade():
    op.drop_table("lesson_syntax_references")
    op.drop_index("ix_syntax_examples_reference_order", table_name="syntax_reference_examples")
    op.drop_index("ix_syntax_reference_examples_reference_id", table_name="syntax_reference_examples")
    op.drop_table("syntax_reference_examples")
    op.drop_index("ix_syntax_references_course_status_order", table_name="syntax_references")
    op.drop_index("ix_syntax_references_status", table_name="syntax_references")
    op.drop_index("ix_syntax_references_course_id", table_name="syntax_references")
    op.drop_table("syntax_references")
