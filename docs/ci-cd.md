# CI/CD

`.github/workflows/quality.yml` runs frontend checks, backend tests, dependency audit hooks, Playwright smoke tests, and a PostgreSQL migration job. Production deployment is intentionally absent: add protected staging and production environments only after cloud credentials and approval gates are configured.

A release should build immutable artifacts, run migrations as a controlled job, deploy compatible application versions, run smoke tests, and retain the previous artifact for rollback. Untrusted pull requests must not receive production secrets.
