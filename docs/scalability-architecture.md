# Scalability architecture

The intended topology is stateless FastAPI instances behind health-based routing, PostgreSQL as durable source of truth, Redis for bounded queues and coordination, isolated runners/workspaces, object storage for private files, and a CDN only for versioned public assets. Session validation remains shared and server-side. Non-idempotent mutations must not be blindly retried.

The implementation records capacity evidence separately from control-plane policies. Production autoscaling requires an explicitly authorized external controller.
