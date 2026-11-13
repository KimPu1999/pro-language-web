# Performance benchmarks

No representative load benchmark has been claimed. `k6` is not installed in this workspace, PostgreSQL `pg_stat_statements` availability has not been verified, and no staging profile exists.

On 2026-11-13, five local `GET /api/v1/health` observations returned HTTP 200 in 116.1 ms, 4.3 ms, 4.2 ms, 3.8 ms, and 4.8 ms. This is a warm-up observation only, not an endpoint or production latency SLO.

The first benchmark should measure public course browsing, lesson retrieval, authenticated dashboard, challenge status, community feed, and administrator analytics at p50/p95/p99 with error rate and database query counts. Capture `EXPLAIN (ANALYZE, BUFFERS)` for the resulting slow queries. Analytics currently has a known N+1-shaped completion calculation and should be grouped before scale testing.

Run load tests only against isolated staging. Record concurrency, throughput, latency, resource usage, and database pool saturation in this file after execution.
