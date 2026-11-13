# Deployment readiness

Audited 2026-11-13. The repository has a Next.js frontend, FastAPI backend, PostgreSQL/Alembic migrations, Redis queue configuration, disabled-by-default runner/AI/video boundaries, and CI quality gates. A provider deployment has not been performed or verified.

## Blockers

- No production cloud accounts, domains, managed PostgreSQL/Redis instances, object storage, email provider, monitoring backend, or provider credentials are available in this workspace.
- The secure code runner has no isolated worker implementation here and remains disabled.
- AI and live video adapters are disabled/not configured.
- Backup restore, staging, load testing, and alert verification are not run.
- Existing Ruff findings must be reduced or an agreed lint policy must be adopted before making the backend quality gate required.

## Implemented preparation

- Added a non-root `backend/Dockerfile` with a health check and production Uvicorn command.
- Added `backend/.dockerignore`.
- Added root `.env.example` with server/public variable boundaries.
- Added `/api/v1/ready` for database readiness; `/api/v1/health` remains a liveness/database check.
- Frontend API calls use same-origin rewrites in the browser and `API_INTERNAL_URL` only during server rendering.

No deployment URL is claimed. Production requires explicit Go/No-Go approval after staging verification.
