# AI Usage Limits

Usage is enforced by the backend, not by browser counters. Each authenticated user has a UTC daily request counter in `ai_quota_counters`; the configured `AI_DAILY_REQUEST_LIMIT` is checked before a stream starts. Prompt input is bounded by the request schema and `AI_MAX_INPUT_CHARS`.

Every attempt records an `ai_usage_records` row, including failed provider attempts. Token counts are recorded when the provider returns a completed response. Admin usage reports expose aggregate request and failure counts without provider secrets or student message content.

Quota policy is intentionally free-tier oriented. A production deployment should add Redis-backed concurrency and rate limiting, monthly budgets, provider cost accounting, retention jobs, and operational alerts before enabling a paid provider.
