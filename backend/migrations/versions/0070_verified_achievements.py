"""Add versioned, verified achievement definitions and awards."""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0070_verified_achievements"
down_revision = "0069_verified_certificates"
branch_labels = None
depends_on = None


def upgrade():
    u = postgresql.UUID(as_uuid=False)
    ts = sa.DateTime(timezone=True)

    for name, column in [
        ("title_mm", sa.Column("title_mm", sa.String(160), nullable=True)),
        ("description_mm", sa.Column("description_mm", sa.Text, nullable=True)),
        ("criteria_description", sa.Column("criteria_description", sa.Text, server_default="", nullable=False)),
        ("criteria_description_mm", sa.Column("criteria_description_mm", sa.Text, nullable=True)),
        ("category", sa.Column("category", sa.String(40), server_default="learning", nullable=False)),
        ("rule_type", sa.Column("rule_type", sa.String(60), server_default="lesson_completion_count", nullable=False)),
        ("rule_json", sa.Column("rule_json", sa.Text, server_default="{}", nullable=False)),
        ("rule_version", sa.Column("rule_version", sa.Integer, server_default="1", nullable=False)),
        ("badge_image_url", sa.Column("badge_image_url", sa.String(500), nullable=True)),
        ("icon_name", sa.Column("icon_name", sa.String(50), server_default="Award", nullable=False)),
        ("tier", sa.Column("tier", sa.String(30), server_default="standard", nullable=False)),
        ("related_course_id", sa.Column("related_course_id", u, sa.ForeignKey("courses.id", ondelete="SET NULL"), nullable=True)),
        ("related_path_id", sa.Column("related_path_id", u, sa.ForeignKey("career_roadmaps.id", ondelete="SET NULL"), nullable=True)),
        ("repeatable", sa.Column("repeatable", sa.Boolean, server_default=sa.false(), nullable=False)),
        ("visibility", sa.Column("visibility", sa.String(20), server_default="public", nullable=False)),
        ("status", sa.Column("status", sa.String(20), server_default="draft", nullable=False)),
        ("display_order", sa.Column("display_order", sa.Integer, server_default="0", nullable=False)),
        ("created_by", sa.Column("created_by", u, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True)),
        ("published_at", sa.Column("published_at", ts, nullable=True)),
    ]:
        op.add_column("achievement_definitions", column)
    op.create_index("ix_achievement_definitions_public_status", "achievement_definitions", ["status", "visibility", "display_order"])
    op.create_index("ix_achievement_definitions_rule_type", "achievement_definitions", ["rule_type", "status"])

    op.create_table(
        "achievement_rule_versions",
        sa.Column("id", u, primary_key=True),
        sa.Column("achievement_id", u, sa.ForeignKey("achievement_definitions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column("rule_type", sa.String(60), nullable=False),
        sa.Column("rule_json", sa.Text, server_default="{}", nullable=False),
        sa.Column("status", sa.String(20), server_default="draft", nullable=False),
        sa.Column("created_by", u, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", ts, server_default=sa.func.now()),
        sa.Column("updated_at", ts, server_default=sa.func.now()),
        sa.UniqueConstraint("achievement_id", "version"),
    )

    op.add_column("student_achievements", sa.Column("public_id", sa.String(80), nullable=True))
    op.add_column("student_achievements", sa.Column("criteria_version", sa.Integer, server_default="1", nullable=False))
    op.add_column("student_achievements", sa.Column("evidence_json", sa.Text, server_default="{}", nullable=False))
    op.add_column("student_achievements", sa.Column("status", sa.String(20), server_default="active", nullable=False))
    op.add_column("student_achievements", sa.Column("revoked_at", ts, nullable=True))
    op.add_column("student_achievements", sa.Column("revocation_reason", sa.Text, nullable=True))
    op.execute("UPDATE student_achievements SET public_id = md5(id::text || chr(58) || 'achievement') WHERE public_id IS NULL")
    op.alter_column("student_achievements", "public_id", nullable=False)
    op.create_unique_constraint("uq_student_achievements_public_id", "student_achievements", ["public_id"])
    op.create_index("ix_student_achievements_user_status", "student_achievements", ["user_id", "status", "awarded_at"])
    op.create_index("ix_student_achievements_public_id", "student_achievements", ["public_id"])

    op.create_table(
        "achievement_award_evidence",
        sa.Column("id", u, primary_key=True),
        sa.Column("award_id", u, sa.ForeignKey("student_achievements.id", ondelete="CASCADE"), nullable=False),
        sa.Column("evidence_type", sa.String(60), nullable=False),
        sa.Column("evidence_id", u, nullable=False),
        sa.Column("evidence_summary", sa.Text, server_default="", nullable=False),
        sa.Column("created_at", ts, server_default=sa.func.now()),
        sa.Column("updated_at", ts, server_default=sa.func.now()),
        sa.UniqueConstraint("award_id", "evidence_type", "evidence_id"),
    )
    op.create_table(
        "achievement_audit_events",
        sa.Column("id", u, primary_key=True),
        sa.Column("actor_id", u, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(80), nullable=False),
        sa.Column("resource_type", sa.String(60), nullable=False),
        sa.Column("resource_id", u, nullable=True),
        sa.Column("metadata_json", sa.Text, server_default="{}", nullable=False),
        sa.Column("created_at", ts, server_default=sa.func.now()),
        sa.Column("updated_at", ts, server_default=sa.func.now()),
    )
    op.create_index("ix_achievement_audit_events_resource", "achievement_audit_events", ["resource_type", "resource_id", "created_at"])


def downgrade():
    op.drop_index("ix_achievement_audit_events_resource", table_name="achievement_audit_events")
    op.drop_table("achievement_audit_events")
    op.drop_table("achievement_award_evidence")
    op.drop_index("ix_student_achievements_public_id", table_name="student_achievements")
    op.drop_index("ix_student_achievements_user_status", table_name="student_achievements")
    op.drop_constraint("uq_student_achievements_public_id", "student_achievements", type_="unique")
    for name in ("revocation_reason", "revoked_at", "status", "evidence_json", "criteria_version", "public_id"):
        op.drop_column("student_achievements", name)
    op.drop_table("achievement_rule_versions")
    op.drop_index("ix_achievement_definitions_rule_type", table_name="achievement_definitions")
    op.drop_index("ix_achievement_definitions_public_status", table_name="achievement_definitions")
    for name in ("published_at", "created_by", "display_order", "status", "visibility", "repeatable", "related_path_id", "related_course_id", "tier", "icon_name", "badge_image_url", "rule_version", "rule_json", "rule_type", "category", "criteria_description_mm", "criteria_description", "description_mm", "title_mm"):
        op.drop_column("achievement_definitions", name)
