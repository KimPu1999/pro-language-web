"""phase 26 cloud lab workspace indexes

Phase 26 reuses the Phase 24 learning-lab tables. These indexes support the
cloud dashboard, ownership checks, lifecycle operations, and audit views
without creating a duplicate workspace data model.
"""

from alembic import op

revision = "0028_cloud_lab_indexes"
down_revision = "0027_community_query_indexes"
branch_labels = None
depends_on = None


def upgrade():
    op.create_index("ix_learning_lab_workspaces_user_status", "learning_lab_workspaces", ["user_id", "status"])
    op.create_index("ix_learning_lab_snapshots_workspace_created", "learning_lab_snapshots", ["workspace_id", "created_at"])
    op.create_index("ix_learning_lab_runs_workspace_status", "learning_lab_runs", ["workspace_id", "status"])
    op.create_index("ix_learning_lab_audit_logs_resource", "learning_lab_audit_logs", ["resource_id", "created_at"])


def downgrade():
    op.drop_index("ix_learning_lab_audit_logs_resource", table_name="learning_lab_audit_logs")
    op.drop_index("ix_learning_lab_runs_workspace_status", table_name="learning_lab_runs")
    op.drop_index("ix_learning_lab_snapshots_workspace_created", table_name="learning_lab_snapshots")
    op.drop_index("ix_learning_lab_workspaces_user_status", table_name="learning_lab_workspaces")
