# Testing strategy

Backend tests use pytest with isolated SQLite fixtures and FastAPI `TestClient`; they do not use production data. Frontend unit tests use Vitest, jsdom, and React Testing Library. Browser smoke tests use Playwright and a local Next server.

Run:

```bash
cd backend && PYTHONPATH=. pytest -q
cd frontend && npm run test:unit && npm run typecheck && npm run lint && npm run build
cd frontend && npm run test:e2e
```

CI should add a PostgreSQL service for migration tests and mocked provider services for AI, video, runner, and GitHub integrations. Paid external services are never required for tests.

Security tests cover ownership, RBAC, CSRF, hidden content, provider failure, and privacy boundaries. Load, restore, accessibility axe scans, and real provider integration remain staging checks until configured.
