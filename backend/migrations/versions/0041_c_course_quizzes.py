"""Persist lesson quizzes for authored course content."""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "0041_c_course_quizzes"
down_revision = "0040_gamification_network"
branch_labels = None
depends_on = None

def upgrade():
    u = postgresql.UUID(as_uuid=False)
    ts = sa.DateTime(timezone=True)
    common = [sa.Column("created_at", ts, server_default=sa.func.now()), sa.Column("updated_at", ts, server_default=sa.func.now())]
    op.create_table("lesson_quizzes", sa.Column("id", u, primary_key=True), sa.Column("lesson_id", u, sa.ForeignKey("lessons.id", ondelete="CASCADE"), nullable=False, unique=True), sa.Column("title", sa.String(180), nullable=False), sa.Column("explanation", sa.Text, server_default="", nullable=False), sa.Column("status", sa.String(20), server_default="published", nullable=False), *common)
    op.create_index("ix_lesson_quizzes_lesson", "lesson_quizzes", ["lesson_id"])
    op.create_table("quiz_questions", sa.Column("id", u, primary_key=True), sa.Column("quiz_id", u, sa.ForeignKey("lesson_quizzes.id", ondelete="CASCADE"), nullable=False), sa.Column("prompt", sa.Text, nullable=False), sa.Column("question_type", sa.String(20), server_default="multiple_choice", nullable=False), sa.Column("options_json", sa.Text, server_default="[]", nullable=False), sa.Column("correct_answer", sa.String(255), nullable=False), sa.Column("explanation", sa.Text, server_default="", nullable=False), sa.Column("position", sa.Integer, nullable=False), sa.UniqueConstraint("quiz_id", "position"), *common)
    op.create_index("ix_quiz_questions_quiz", "quiz_questions", ["quiz_id"])
    op.create_table("quiz_attempts", sa.Column("id", u, primary_key=True), sa.Column("quiz_id", u, sa.ForeignKey("lesson_quizzes.id", ondelete="CASCADE"), nullable=False), sa.Column("user_id", u, sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False), sa.Column("answers_json", sa.Text, server_default="{}", nullable=False), sa.Column("score", sa.Integer, nullable=False), sa.Column("total", sa.Integer, nullable=False), *common)
    op.create_index("ix_quiz_attempts_user_quiz", "quiz_attempts", ["user_id", "quiz_id"])

def downgrade():
    op.drop_index("ix_quiz_attempts_user_quiz", table_name="quiz_attempts")
    op.drop_table("quiz_attempts")
    op.drop_index("ix_quiz_questions_quiz", table_name="quiz_questions")
    op.drop_table("quiz_questions")
    op.drop_index("ix_lesson_quizzes_lesson", table_name="lesson_quizzes")
    op.drop_table("lesson_quizzes")
