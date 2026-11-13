# API Performance Audit

## Scope

This audit covers the local FastAPI service and the Next.js clients used by the platform and analytics pages. Measurements were taken on 2026-11-13 against `127.0.0.1:8000`; protected endpoints were checked without credentials and therefore correctly returned `401`.

## Baseline observations

| Endpoint | Result | Observed time |
|---|---:|---:|
| `/api/v1/health` | 200 | 107.1 ms during the first cold check; 21.9 ms after warm-up |
| `/api/v1/ready` | 200 | 5.7 ms |
| `/api/v1/courses?page_size=12` | 200 | 259.1 ms during the first check; 25.8 ms and 10.7 ms on repeated warm checks |
| `/api/v1/auth/me` | 401 | 2.8 ms |
| `/api/v1/admin/dashboard` | 401 | 2.7 ms |
| `/api/v1/platform/analytics/overview` | 401 | 2.8 ms |
| `/api/v1/platform/quality` | 401 | 3.2 ms |
| `/api/v1/organizations` | 401 | 2.8 ms |

The first cold requests include process, database connection and query-plan warm-up. Authenticated analytics and admin timings require a provisioned admin account and were not fabricated.

## Confirmed causes

1. A stale or unresponsive development FastAPI process repeatedly occupied port 8000. The browser then reported timeout or connection failures even though a listener appeared in local process tools.
2. The API had request IDs but no duration or exception logging, making slow requests and 500s difficult to correlate.
3. Analytics completion calculation queried lesson totals and completed lessons for every enrollment and called that calculation twice in the overview endpoint.
4. The main and analytics frontend clients did not deduplicate simultaneous GET requests, so React development remounts could issue duplicate requests.
5. SQLAlchemy had pre-ping enabled but no explicit bounded pool timeout, recycle policy, or overflow policy for PostgreSQL.

## Changes

- Added bounded PostgreSQL pool settings with safe SQLite test handling.
- Added request duration logging, slow-request warning threshold, response timing header and correlation ID propagation.
- Added safe generic 500 JSON responses containing only a request ID; server logs retain the traceback.
- Replaced analytics completion N+1 work with grouped aggregate queries and calculate overview completion data once.
- Added in-flight GET deduplication to the shared and analytics API clients.

## Limitations

The local environment did not provide an authenticated platform admin session or production traffic, so protected dashboard latency, p95/p99, memory, Redis queue depth and PostgreSQL `EXPLAIN ANALYZE` against production-size data remain NOT MEASURED.
