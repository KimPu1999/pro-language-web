# Leaderboard rules

Only `verified=true` ranking rows are returned. Ordering is deterministic: total score descending, penalty seconds ascending, then solved count descending. Rejudge operations must update rankings transactionally and preserve an audit record.
