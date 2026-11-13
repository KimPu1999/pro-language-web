# Runner deployment contract

Set `REDIS_URL`, `RUNNER_QUEUE_NAME`, and `RUNNER_ENABLED=true` only when a reviewed worker service is available. The API publishes JSON jobs to Redis. A worker should claim a job, validate the allowlisted runtime, execute inside the hardened sandbox, write a bounded result, and update the job status through an authenticated internal channel or service boundary.

The worker deployment is intentionally outside this repository's local development path. Before enabling it, provision immutable runtime images, a Redis ACL, TLS where required, metrics and alerting, dead-letter handling, job expiry, and operational runbooks. Keep `RUNNER_ENABLED=false` in environments without that infrastructure.
