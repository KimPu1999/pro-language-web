# Performance Test Results

Date: 2026-11-13

## API smoke measurements

| Check | Result |
|---|---|
| FastAPI health | PASS, HTTP 200 |
| FastAPI readiness | PASS, HTTP 200 |
| Public course page | PASS, HTTP 200 |
| Authenticated endpoints without credentials | PASS, HTTP 401 as expected |
| Request ID header | PASS |
| Response timing header | PASS |
| Repeated public course request | PASS, 25.8 ms then 10.7 ms |
| Platform analytics navigation after compilation | PASS, 147–182 ms, HTTP 200 |

## Automated checks

- Backend compile and pytest: PASS, 63 passed, 1 existing Starlette deprecation warning.
- Frontend ESLint: PASS; TypeScript: PASS; unit suite: PASS, 1 file and 2 tests.
- Next production build: PASS, 121 routes generated.
- Playwright browser smoke tests: NOT RUN because the installed Playwright version does not support downloading Chromium on macOS 12 in this environment.

No performance improvement claim is made for production traffic, p95/p99, memory or Redis throughput without those measurements.
