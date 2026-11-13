# Workflow approvals

Approval requests are organization-scoped and have an expiry. An approver must have an owner or admin organization role, cannot approve their own request, and can make one decision. A decision returns `revalidation_required`; protected actions must re-check authorization and approval state immediately before a future worker executes them.
