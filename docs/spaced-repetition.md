# Spaced repetition

Revision attempts accept a confidence rating from 1 to 5. The next interval is 1 day for ratings 1–2, 3 days for 3, 7 days for 4, and 14 days for 5. Review timestamps are stored in UTC, and every attempt is retained for auditability.

## Phase 29

Phase 29 revision uses deterministic algorithm `v1`. Correct reviews increase the ease factor and interval; incorrect reviews reduce the ease factor and reset the interval to a bounded value. Review outcomes are stored independently of AI output.
