# Workflow engine

Workflow definitions belong to an organization. A definition has draft versions and immutable published versions. A run stores the exact version ID used, a correlation ID, durable step records, and an organization-scoped idempotency key.

The API validates node types, allowlisted action names, edge references, self-loops, cycles, and graph size. It rejects shell, SQL, URL, and command configuration. PostgreSQL is the source of truth; Redis is reserved for a future worker queue and is never treated as durable state.

Current execution status is `queued_only` because no worker is configured in this repository. This is intentionally visible to operators.
