# Monitoring

The application exposes liveness at `/api/v1/health` and database readiness at `/api/v1/ready`, plus request correlation IDs. External telemetry, error tracking, queue metrics, provider metrics, and alert delivery are not configured in this repository.

Configure alerts for elevated 5xx responses, readiness failures, database pool saturation, Redis queue age, failed workers, backup failures, and provider budget limits. Redact credentials, tokens, private code, and private learning content.
