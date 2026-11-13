# API Error Root Causes

## Confirmed

- Local connection failures and timeout messages were caused by stale/unresponsive FastAPI development processes competing for port 8000. A clean process returned `/api/v1/health` and `/api/v1/ready` successfully.
- Protected routes returning `401` or `403` without a valid session are expected authorization behavior, not server errors.
- The first request to a live Next.js development page can return a transient compilation error while the route is being compiled; after compilation, three consecutive `/platform/analytics` requests returned HTTP 200. Production builds do not use development compilation.

## Stabilization changes

- Unexpected request exceptions are logged with request ID, method, path and duration and return a safe `500` JSON response.
- Successful and error responses include `X-Request-ID`; successful responses also include `X-Response-Time-ms`.
- Database connections use pre-ping, bounded overflow, timeout and recycle settings for PostgreSQL.

No production traceback or secret is sent to the browser. A real authenticated 500 reproduction was NOT AVAILABLE in this local run.
