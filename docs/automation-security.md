# Automation security

All organization automation reads resolve membership on the server. Mutations require CSRF validation and manager or approver roles. Published version IDs, tenant-scoped idempotency keys, audit logs, approval expiry, separation of duties, and restricted action schemas protect the workflow boundary. A real worker must preserve these checks at execution time.
