# Challenge grading

Challenges use published records, language configurations, public tests, and hidden tests. The API creates a submission and a Phase 4 execution job; the secure worker is responsible for running the code and returning bounded results. Grading must compare normalized output deterministically, calculate `passed_points / total_points * 100`, and map failures to `accepted`, `wrong_answer`, `compilation_error`, `runtime_error`, `time_limit_exceeded`, `memory_limit_exceeded`, `cancelled`, or `internal_error`.

The current environment has `RUNNER_ENABLED=false`, so submissions persist as `runner_unavailable` and are never executed. The API does not claim a score until a worker callback and grading service are deployed.
