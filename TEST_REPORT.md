# Learn-Coding Test Report

Audit date: 2026-11-21

## Passing checks

| Check | Result |
| --- | --- |
| Backend full pytest suite | 146 passed, 2 warnings |
| Backend course/admin/content regression subset | 16 passed, 2 warnings |
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
| Public course catalog/detail/lesson and Admin course routes | Passed; HTTP 200 after clean `.next` restart |
| Public course detail metadata/FAQ fields | Passed; HTTP 200 with real curriculum, related courses, and empty-safe detail fields |
| Additive course-detail migration | Applied locally: `0045_course_detail_content` |
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
- Full end-to-end admin branding/media/content publishing was not claimed: media
  upload and rich lesson editing remain outside this course-detail slice.
- Backup restore, production CORS, rate-limit load behavior, and external object
  storage were not tested.

