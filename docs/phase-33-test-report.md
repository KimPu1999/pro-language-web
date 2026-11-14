# Phase 33 test report

| Check | Result | Evidence |
|---|---|---|
| Ruff | PASS | `backend`: `ruff check app` |
| Python compile | PASS | `python3 -m compileall -q app` |
| Migration head | PASS | `0034_marketplace (head)` |
| Backend tests | PASS | `PYTHONPATH=. pytest -q`: 96 passed, 1 warning |
| Marketplace tests | PASS | 5 marketplace tests included in full suite |
| TypeScript | PASS | `npm run typecheck` |
| ESLint | PASS | `npm run lint -- --max-warnings=0` via build validation |
| Frontend unit tests | PASS | 1 file, 2 tests |
| Next.js production build | PASS | 221 routes generated |
| Playwright | NOT RUN | Existing sandbox cannot bind local port 3000 (`EPERM`) |

The passing tests cover public draft exclusion, contributor authorization,
moderator publication, student denial, and review boundary behavior. No
production database migration was executed. Full-text indexing, external asset
scanning, browser accessibility automation, and production engagement telemetry
remain environment-level validation work.
