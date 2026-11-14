# Horizontal API scaling

The API uses server-managed sessions in PostgreSQL rather than process-local authentication state. Health and readiness endpoints exist. Database pools are bounded. Distributed rate limiting is not enabled; the current in-process buckets are not sufficient for multiple instances and must be replaced with Redis-backed limits before horizontal production scaling.
