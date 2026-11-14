# Phase 40 Repository Inventory

## Repository evidence

- Frontend: `frontend/`, Next.js App Router, 363 `page.tsx` files before the
  Phase 40 audit changes.
- Backend: `backend/app/`, FastAPI routers registered in `backend/app/main.py`.
- Persistence: SQLAlchemy models in `backend/app/models.py`; Alembic revisions
  `0001` through `0040`.
- Tests: backend pytest modules under `backend/tests`; frontend Vitest and
  Playwright configuration under `frontend/`.
- CI: `.github/workflows/quality.yml` contains frontend, backend, browser,
  dependency, and PostgreSQL migration jobs.
- Runtime integrations: Redis queue adapter, disabled-by-default runner, AI
  provider abstraction, WebSocket/Yjs routes, PWA service worker, and platform
  operations records.

## Important runtime facts

The repository is configured for local development by default. Runner, AI,
collaboration, external mail, GitHub, and enterprise identity providers are
disabled unless environment variables enable them. No production deployment,
managed PostgreSQL, Redis, object storage, backup provider, or telemetry backend
was assumed during this audit.
