# Phase 35 test report

Focused backend tests: `PYTHONPATH=. pytest -q tests/test_student_success.py --disable-warnings` — 3 passed.

Full backend suite: `PYTHONPATH=. pytest -q tests --disable-warnings --maxfail=1` — 104 passed, 1 warning, 111.67 seconds.

Frontend: `npm run lint` passed; `npm run build` passed and generated 249 routes. The build includes TypeScript validation. Playwright/browser smoke tests were not executed in this environment, so browser behavior and accessibility automation remain unverified.

Migration integrity: `alembic heads` reported `0036_student_success (head)`; applying against a live PostgreSQL instance was not performed because the local shell lacks the `psycopg` driver and a configured PostgreSQL service.
