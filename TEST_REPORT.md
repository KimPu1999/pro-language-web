# Learn-Coding Test Report

Audit date: 2026-11-21

## Passing checks

| Check | Result |
| --- | --- |
| Backend full pytest suite | 143 passed, 1 warning |
| Backend admin/content/platform regression subset | 12 passed, 2 warnings |
| `apps/platform` TypeScript check | Passed |
| `apps/platform` production build | Passed; 8 generated routes |
| `apps/admin` TypeScript check | Passed |
| `apps/admin` production build | Passed |
| Legacy `frontend` production build | Passed; 456 static pages generated |
| Legacy `frontend` TypeScript check | Passed after clean build |
| Legacy `frontend` ESLint | Passed with `--max-warnings=0` |
| Legacy frontend unit tests | 4 passed |
| FastAPI health/readiness smoke checks | Passed |
| Public branding/navigation/course/project/challenge HTTP checks | Passed |
| Unauthenticated admin session check | Correctly denied with HTTP 401 |
| Read-only FK integrity audit | 653 constraints checked, 0 orphan violations |
| `git diff --check` | Passed |

## Important warnings

- Pytest reports an existing unknown `asyncio_default_fixture_loop_scope`
  configuration option and a Starlette deprecation warning.
- Next.js warns that multiple lockfiles cause workspace-root inference. This is
  non-blocking locally but should be resolved before production deployment.
- The first legacy frontend unit run exposed a stale test expecting the removed
  Burmese toggle. The component is intentionally English-only per the project
  requirement; the test now asserts that Burmese controls/content are not
  rendered, and the suite passes 4/4.

## Not yet verified

- Successful administrator login cannot be tested until an operator provisions
  the first admin account.
- Browser-level Playwright coverage, mobile visual review, and accessibility
  review were not run in this audit.
- Full end-to-end admin branding/media/content publishing was not claimed: the
  new admin UI is incomplete even though the protected backend endpoints and
  regression tests exist.
- Backup restore, production CORS, rate-limit load behavior, and external object
  storage were not tested.

