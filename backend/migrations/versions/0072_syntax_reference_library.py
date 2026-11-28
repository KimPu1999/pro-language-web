"""Expand syntax references into a reviewed, bilingual reference library.

This migration is additive. Existing syntax rows and their identifiers remain
unchanged; the new fields provide richer content, translation records, and
version history for the admin workflow.
"""
from alembic import op
import sqlalchemy as sa

revision = "0072_syntax_reference_library"
down_revision = "0071_initial_achievement_drafts"
branch_labels = None
depends_on = None


def upgrade():
    columns = [
        ("reference_type", sa.String(60), "language_syntax"),
        ("difficulty", sa.String(30), "beginner"),
        ("purpose", sa.Text(), ""),
        ("syntax_format", sa.Text(), ""),
        ("parameters", sa.Text(), ""),
        ("return_value", sa.Text(), ""),
        ("version_compatibility", sa.Text(), ""),
        ("input_output", sa.Text(), ""),
        ("common_mistakes", sa.Text(), ""),
        ("best_practices", sa.Text(), ""),
        ("practice_exercises", sa.Text(), ""),
        ("further_reading", sa.Text(), ""),
        ("minimum_examples", sa.Integer(), "5"),
        ("review_notes", sa.Text(), ""),
        ("approved_by", sa.UUID(), None),
        ("reviewed_at", sa.DateTime(timezone=True), None),
        ("published_at", sa.DateTime(timezone=True), None),
        ("created_by", sa.UUID(), None),
        ("updated_by", sa.UUID(), None),
    ]
    for name, column_type, default in columns:
        kwargs = {"nullable": name in {"approved_by", "reviewed_at", "published_at", "created_by", "updated_by"}}
        if default is not None:
            kwargs["server_default"] = sa.text("NULL") if default == "" and kwargs["nullable"] else sa.text(f"'{default}'") if isinstance(default, str) else sa.text(str(default))
        op.add_column("syntax_references", sa.Column(name, column_type, **kwargs))
    op.create_index("ix_syntax_references_type_difficulty", "syntax_references", ["reference_type", "difficulty"])
    op.create_foreign_key("fk_syntax_references_approved_by", "syntax_references", "users", ["approved_by"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_syntax_references_created_by", "syntax_references", "users", ["created_by"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_syntax_references_updated_by", "syntax_references", "users", ["updated_by"], ["id"], ondelete="SET NULL")

    example_columns = [
        ("difficulty", sa.String(30), "beginner"),
        ("description", sa.Text(), ""),
        ("setup", sa.Text(), ""),
        ("sample_input", sa.Text(), ""),
        ("common_mistakes", sa.Text(), ""),
        ("verification_steps", sa.Text(), ""),
    ]
    for name, column_type, default in example_columns:
        op.add_column("syntax_reference_examples", sa.Column(name, column_type, nullable=False, server_default=sa.text(f"'{default}'")))

    uuid = sa.UUID()
    op.create_table(
        "syntax_reference_translations",
        sa.Column("id", uuid, nullable=False),
        sa.Column("reference_id", uuid, nullable=False),
        sa.Column("locale", sa.String(5), nullable=False),
        sa.Column("title", sa.String(180), nullable=False, server_default=""),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("purpose", sa.Text(), nullable=False, server_default=""),
        sa.Column("syntax_format", sa.Text(), nullable=False, server_default=""),
        sa.Column("parameters", sa.Text(), nullable=False, server_default=""),
        sa.Column("return_value", sa.Text(), nullable=False, server_default=""),
        sa.Column("version_compatibility", sa.Text(), nullable=False, server_default=""),
        sa.Column("input_output", sa.Text(), nullable=False, server_default=""),
        sa.Column("common_mistakes", sa.Text(), nullable=False, server_default=""),
        sa.Column("best_practices", sa.Text(), nullable=False, server_default=""),
        sa.Column("practice_exercises", sa.Text(), nullable=False, server_default=""),
        sa.Column("further_reading", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["reference_id"], ["syntax_references.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference_id", "locale"),
    )
    op.create_index("ix_syntax_reference_translations_locale", "syntax_reference_translations", ["locale"])
    op.create_index("ix_syntax_reference_translations_reference_id", "syntax_reference_translations", ["reference_id"])

    op.create_table(
        "syntax_example_translations",
        sa.Column("id", uuid, nullable=False),
        sa.Column("example_id", uuid, nullable=False),
        sa.Column("locale", sa.String(5), nullable=False),
        sa.Column("title", sa.String(180), nullable=False, server_default=""),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("setup", sa.Text(), nullable=False, server_default=""),
        sa.Column("sample_input", sa.Text(), nullable=False, server_default=""),
        sa.Column("expected_output", sa.Text(), nullable=False, server_default=""),
        sa.Column("explanation", sa.Text(), nullable=False, server_default=""),
        sa.Column("common_mistakes", sa.Text(), nullable=False, server_default=""),
        sa.Column("verification_steps", sa.Text(), nullable=False, server_default=""),
        sa.Column("status", sa.String(20), nullable=False, server_default="draft"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["example_id"], ["syntax_reference_examples.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("example_id", "locale"),
    )
    op.create_index("ix_syntax_example_translations_example_id", "syntax_example_translations", ["example_id"])

    op.create_table(
        "syntax_reference_versions",
        sa.Column("id", uuid, nullable=False),
        sa.Column("reference_id", uuid, nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("snapshot_json", sa.Text(), nullable=False),
        sa.Column("created_by", uuid, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["reference_id"], ["syntax_references.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("reference_id", "version"),
    )
    op.create_index("ix_syntax_reference_versions_reference", "syntax_reference_versions", ["reference_id", "version"])


def downgrade():
    op.drop_index("ix_syntax_reference_versions_reference", table_name="syntax_reference_versions")
    op.drop_table("syntax_reference_versions")
    op.drop_index("ix_syntax_example_translations_example_id", table_name="syntax_example_translations")
    op.drop_table("syntax_example_translations")
    op.drop_index("ix_syntax_reference_translations_reference_id", table_name="syntax_reference_translations")
    op.drop_index("ix_syntax_reference_translations_locale", table_name="syntax_reference_translations")
    op.drop_table("syntax_reference_translations")
    for name in ("verification_steps", "common_mistakes", "sample_input", "setup", "description", "difficulty"):
        op.drop_column("syntax_reference_examples", name)
    op.drop_constraint("fk_syntax_references_updated_by", "syntax_references", type_="foreignkey")
    op.drop_constraint("fk_syntax_references_created_by", "syntax_references", type_="foreignkey")
    op.drop_constraint("fk_syntax_references_approved_by", "syntax_references", type_="foreignkey")
    op.drop_index("ix_syntax_references_type_difficulty", table_name="syntax_references")
    for name, _, _ in ("updated_by", None, None), ("created_by", None, None), ("published_at", None, None), ("reviewed_at", None, None), ("approved_by", None, None), ("review_notes", None, None), ("minimum_examples", None, None), ("further_reading", None, None), ("practice_exercises", None, None), ("best_practices", None, None), ("common_mistakes", None, None), ("input_output", None, None), ("version_compatibility", None, None), ("return_value", None, None), ("parameters", None, None), ("syntax_format", None, None), ("purpose", None, None), ("difficulty", None, None), ("reference_type", None, None):
        op.drop_column("syntax_references", name)
