# Verified Leaderboards

The leaderboard endpoint returns XP from PostgreSQL-backed balances only for
users whose existing `LeaderboardPreference.opted_in` flag is true. No users are
fabricated and no private users are exposed by default. Period filtering is
currently an API contract placeholder; historical snapshot aggregation remains
follow-up work.
