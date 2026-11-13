# Phase 24 learning labs audit

The existing Monaco and runner boundary were reusable. The runner persists jobs and returns `runner_unavailable` when Redis or an isolated worker is not configured; FastAPI never executes student code. Phase 24 adds lab definitions, immutable lab versions, owned workspaces, files, snapshots, runs, submissions, progress, SQL/API boundary records, reviews, and audit records.

SQL execution and controlled API targets are not configured in this repository. Their UI states are explicit and no platform database credentials or unrestricted proxy are exposed.
