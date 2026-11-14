# Phase 26 Cloud Labs Audit

## Repository findings

Phase 24 already supplies the core learning-lab service. The authoritative
tables are `learning_labs`, `learning_lab_versions`,
`learning_lab_workspaces`, `learning_lab_workspace_files`,
`learning_lab_snapshots`, `learning_lab_runs`, `learning_lab_progress`, and
`learning_lab_audit_logs`. The `/api/v1/labs` and `/api/v1/lab-workspaces/*`
routes are therefore reused by Phase 26 instead of introducing duplicate
workspace storage.

Reusable infrastructure:

- `backend/app/lab_routes.py`: lab catalog, verified workspace ownership,
  files, snapshots, run idempotency, instructor publishing, and platform
  metrics.
- `backend/app/runner_routes.py`, `runner_queue.py`, and `runner_registry.py`:
  authenticated submissions and Redis queueing. The API process never runs
  submitted code. `RUNNER_ENABLED=false` fails closed.
- `frontend/components/lab-pages.tsx`: existing Monaco catalog, dashboard,
  detail, and workspace views.
- `backend/app/ai_routes.py` and `ai_service.py`: quota-limited tutor with
  provider/configuration checks and redaction.
- `backend/app/ecosystem_routes.py`: signed GitHub webhook handling and
  encrypted connection storage.
- `backend/app/collaboration_routes.py` and
  `realtime_collaboration_routes.py`: tenant/team ownership controls; CRDT
  status is explicitly unavailable until configured.
- `backend/app/organization_routes.py`: organization membership and tenant
  context helpers.
- `backend/app/rbac.py`: platform RBAC.

## Trust boundaries

The browser is untrusted and may edit files or request transitions only for a
workspace owned by the authenticated user. FastAPI validates ownership,
verification, CSRF, paths, idempotency, quotas, and lifecycle transitions.
Redis is a queue, not an execution boundary. A separately deployed rootless
runner must consume jobs in an isolated namespace/container or microVM. Host
Docker sockets, host shells, privileged containers, and cluster-admin tokens
are not exposed.

## Current truthful service modes

- Workspace persistence: PostgreSQL-backed and test-covered.
- Code execution: unavailable unless `RUNNER_ENABLED=true` and Redis plus an
  isolated worker are configured.
- Docker labs: deterministic simulation until a separately isolated runner is
  configured.
- Kubernetes labs: deterministic simulation by default; no cluster access.
- Deployment previews: not public by default and require a future isolated
  preview service.
- AI assistant: unavailable unless an AI provider is configured.
- GitHub: unavailable/simulation mode unless GitHub credentials are configured.

## Known gaps carried into Phase 26

The repository does not contain a host-safe container/microVM worker, a
Kubernetes namespace provisioner, or a preview proxy. Phase 26 must not claim
those capabilities until independently deployed and security-tested.
