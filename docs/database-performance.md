# Database Performance

The PostgreSQL engine now uses configurable settings:

- `DB_POOL_SIZE=5`
- `DB_MAX_OVERFLOW=10`
- `DB_POOL_TIMEOUT_SECONDS=15`
- `DB_POOL_RECYCLE_SECONDS=1800`

These defaults are intentionally conservative and can be overridden per deployment. SQLite tests continue to use their existing connection behavior.

The platform analytics completion calculation now loads enrollment pairs once, counts published lessons grouped by course once, and counts completed lessons grouped by course and user once. The previous per-enrollment query loop and duplicate overview calculation were removed.

Production `EXPLAIN ANALYZE`, `pg_stat_statements`, connection saturation and before/after production benchmarks were NOT RUN because no production database was supplied.
