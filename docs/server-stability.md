# Server Stability

## Runtime safeguards

- PostgreSQL connections are pre-pinged and bounded by pool, overflow and timeout settings.
- Requests have correlation IDs and duration logs.
- Requests slower than `SLOW_REQUEST_MS` (default `500`) are logged at warning level.
- Unexpected exceptions are logged server-side and return a non-sensitive error body.

## Operational finding

The local failure mode was an unhealthy development process holding port 8000. Start one backend process only, verify `/api/v1/health` and `/api/v1/ready`, and avoid starting a second process on the occupied port. Production should run a supervised ASGI service with health checks rather than development reload mode.

Redis worker health, production memory/CPU, queue backlog and crash recovery were NOT MEASURED in this run.
