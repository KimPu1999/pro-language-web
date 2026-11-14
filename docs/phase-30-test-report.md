# Phase 30 test report

Environment: local macOS workspace, Python 3.11, Node dependencies already installed, SQLite test fixtures for backend tests.

| Command | Result |
|---|---|
| `ruff check app tests` | PASS |
| `PYTHONPATH=. pytest -q` | PASS: 83 passed, 1 warning |
| `python3 -m compileall -q app migrations` | PASS |
| `PYTHONPATH=. python3 -m alembic heads` | PASS: `0031_ai_companion (head)` |
| `npm run typecheck` | PASS |
| `npm run lint` | PASS |
| `npm run test:unit` | PASS: 2 tests |
| `npm run build` | PASS: 186 Next.js routes resolved |
| `git diff --check` | PASS |
| `npm audit --audit-level=high` | BLOCKED: registry DNS/network unavailable; no vulnerability result obtained |
| Playwright smoke tests | NOT RUN: Chromium executable unavailable locally |
| PostgreSQL migration upgrade | NOT RUN: no live PostgreSQL service available |
| Backup restore/load/rollback rehearsal | NOT RUN: no staging environment available |
