# Learning path testing

Run from `backend/`:

```bash
PYTHONPATH=. pytest -q
PYTHONPATH=. alembic heads
```

Run from `frontend/`:

```bash
npm run typecheck
npm run lint
npm run build
```

The roadmap tests cover publication visibility, enrollment ownership, duplicate enrollment, and learning-goal ownership. Browser smoke tests require the Playwright browser binary to be installed separately.
