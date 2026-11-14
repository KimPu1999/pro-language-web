# Phase 36 test report

Focused assessment tests: `PYTHONPATH=. pytest -q tests/test_assessments.py --disable-warnings` — 2 passed after correcting a test fixture detachment issue.

Full backend suite: `PYTHONPATH=. pytest -q tests --disable-warnings --maxfail=1` — 106 passed, 1 warning, 121.75 seconds.

Frontend: `npm run typecheck` passed, `npm run lint` passed, and `npm run build` passed with 260 routes. Playwright/browser accessibility tests were not run.

Migration integrity: `alembic heads` reported `0037_assessment_integrity (head)`. Applying migrations to live PostgreSQL was not performed because this shell lacks the `psycopg` driver and a configured PostgreSQL service.
