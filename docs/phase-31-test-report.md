# Phase 31 test report

Environment: local macOS workspace, Python 3.11, SQLite test fixtures, installed Node dependencies.

| Command | Result |
|---|---|
| `ruff check app tests` | PASS |
| `python3 -m compileall -q app migrations` | PASS |
| `PYTHONPATH=. python3 -m alembic heads` | PASS: `0032_operations_feedback (head)` |
| `PYTHONPATH=. pytest -q tests/test_phase31_operations.py` | PASS: 4 passed, 1 warning |
| `PYTHONPATH=. pytest -q` | PASS: 87 passed, 1 warning |
| `npm run typecheck` | PASS |
| `npm run lint` | PASS |
| `npm run test:unit` | PASS: 2 tests |
| `npm run build` | PASS: 200 routes |
| Playwright | NOT RUN: local Chromium executable unavailable |
| PostgreSQL migration application | NOT RUN: no live PostgreSQL service available |
| OpenTelemetry/Prometheus integration | NOT RUN: no exporter or collector configured |
| Backup/restore drill | NOT RUN: no staging backup target available |
