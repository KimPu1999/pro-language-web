"""Correct a Burmese quiz prompt embedded in English Linux lesson content."""

from alembic import op
import sqlalchemy as sa


revision = "0066_fix_linux_quiz_locale"
down_revision = "0065_project_workflow_links"
branch_labels = None
depends_on = None


OLD_PROMPT = "chmod 777 ကို ဘာကြောင့် ရှောင်သင့်သနည်း?"
NEW_PROMPT = "Why should chmod 777 usually be avoided?"


def upgrade():
    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            UPDATE lessons
            SET content_en = replace(content_en, :old_prompt, :new_prompt)
            WHERE content_en LIKE :pattern
            """
        ),
        {"old_prompt": OLD_PROMPT, "new_prompt": NEW_PROMPT, "pattern": f"%{OLD_PROMPT}%"},
    )
    connection.execute(
        sa.text(
            """
            UPDATE quiz_questions
            SET prompt = :new_prompt
            WHERE prompt = :old_prompt
            """
        ),
        {"old_prompt": OLD_PROMPT, "new_prompt": NEW_PROMPT},
    )


def downgrade():
    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            UPDATE lessons
            SET content_en = replace(content_en, :new_prompt, :old_prompt)
            WHERE content_en LIKE :pattern
            """
        ),
        {"old_prompt": OLD_PROMPT, "new_prompt": NEW_PROMPT, "pattern": f"%{NEW_PROMPT}%"},
    )
    connection.execute(
        sa.text(
            """
            UPDATE quiz_questions
            SET prompt = :old_prompt
            WHERE prompt = :new_prompt
            """
        ),
        {"old_prompt": OLD_PROMPT, "new_prompt": NEW_PROMPT},
    )
