"""Add private personal notebook notes, folders, and tags."""
from alembic import op
import sqlalchemy as sa

revision = "0057_personal_notebook"
down_revision = "0056_content_review_workflow"
branch_labels = None
depends_on = None


def upgrade():
    uuid = sa.UUID()
    op.create_table(
        "notebook_folders",
        sa.Column("id", uuid, nullable=False),
        sa.Column("owner_id", uuid, nullable=False),
        sa.Column("name", sa.String(120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False, server_default=""),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "name"),
    )
    op.create_index("ix_notebook_folders_owner_id", "notebook_folders", ["owner_id"])
    op.create_index("ix_notebook_folders_owner_updated", "notebook_folders", ["owner_id", "updated_at"])

    op.create_table(
        "note_tags",
        sa.Column("id", uuid, nullable=False),
        sa.Column("owner_id", uuid, nullable=False),
        sa.Column("name", sa.String(60), nullable=False),
        sa.Column("color", sa.String(20), nullable=False, server_default="#818CF8"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("owner_id", "name"),
    )
    op.create_index("ix_note_tags_owner_id", "note_tags", ["owner_id"])
    op.create_index("ix_note_tags_owner_name", "note_tags", ["owner_id", "name"])

    op.create_table(
        "personal_notes",
        sa.Column("id", uuid, nullable=False),
        sa.Column("owner_id", uuid, nullable=False),
        sa.Column("title", sa.String(240), nullable=False, server_default="Untitled note"),
        sa.Column("content", sa.Text(), nullable=False, server_default=""),
        sa.Column("course_id", uuid, nullable=True),
        sa.Column("lesson_id", uuid, nullable=True),
        sa.Column("folder_id", uuid, nullable=True),
        sa.Column("is_favorite", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_pinned", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["course_id"], ["courses.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["lesson_id"], ["lessons.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["folder_id"], ["notebook_folders.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    for name, columns in (
        ("ix_personal_notes_owner_id", ["owner_id"]),
        ("ix_personal_notes_course_id", ["course_id"]),
        ("ix_personal_notes_lesson_id", ["lesson_id"]),
        ("ix_personal_notes_folder_id", ["folder_id"]),
        ("ix_personal_notes_is_favorite", ["is_favorite"]),
        ("ix_personal_notes_is_pinned", ["is_pinned"]),
        ("ix_personal_notes_owner_updated", ["owner_id", "updated_at"]),
        ("ix_personal_notes_owner_course", ["owner_id", "course_id"]),
        ("ix_personal_notes_owner_lesson", ["owner_id", "lesson_id"]),
        ("ix_personal_notes_owner_folder", ["owner_id", "folder_id"]),
    ):
        op.create_index(name, "personal_notes", columns)

    op.create_table(
        "personal_note_tags",
        sa.Column("note_id", uuid, nullable=False),
        sa.Column("tag_id", uuid, nullable=False),
        sa.ForeignKeyConstraint(["note_id"], ["personal_notes.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["note_tags.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("note_id", "tag_id"),
    )


def downgrade():
    op.drop_table("personal_note_tags")
    for name in ("ix_personal_notes_owner_folder", "ix_personal_notes_owner_lesson", "ix_personal_notes_owner_course", "ix_personal_notes_owner_updated", "ix_personal_notes_is_pinned", "ix_personal_notes_is_favorite", "ix_personal_notes_folder_id", "ix_personal_notes_lesson_id", "ix_personal_notes_course_id", "ix_personal_notes_owner_id"):
        op.drop_index(name, table_name="personal_notes")
    op.drop_table("personal_notes")
    op.drop_index("ix_note_tags_owner_name", table_name="note_tags")
    op.drop_index("ix_note_tags_owner_id", table_name="note_tags")
    op.drop_table("note_tags")
    op.drop_index("ix_notebook_folders_owner_updated", table_name="notebook_folders")
    op.drop_index("ix_notebook_folders_owner_id", table_name="notebook_folders")
    op.drop_table("notebook_folders")
