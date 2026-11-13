# Production readiness

Current status: **not ready for production**.

Required before release:

- Configure PostgreSQL, Redis, secure cookies, strict trusted origins, and a secret manager.
- Verify the isolated code runner and video provider in staging.
- Configure AI provider policy and quotas if AI is enabled.
- Run migrations on a clean database and a sanitized upgrade snapshot.
- Run CI, dependency scans, Playwright, accessibility scans, load tests, and a backup restore.
- Configure telemetry and an on-call alert path.

The quality dashboard intentionally displays `not configured`, `partial`, or `unknown` instead of inventing health metrics.
