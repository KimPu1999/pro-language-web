# Analytics architecture

The FastAPI analytics router performs read-only aggregate queries over source tables. Date filters are converted to UTC half-open intervals (`start <= timestamp < end + 1 day`). The frontend uses a same-origin Next.js rewrite to the FastAPI API, so cookies remain server managed.

The first implementation calculates metrics on demand. The migration adds only export history and audit records. Daily snapshots and Redis caching can be introduced after query timings from production-sized data justify them; source records are never overwritten.
