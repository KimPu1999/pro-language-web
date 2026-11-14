# Cloud Workspace Architecture

Phase 26 reuses the Phase 24 `learning_lab_*` schema. A workspace belongs to
one user and one published lab version. Browser requests go through Next.js to
FastAPI, PostgreSQL stores metadata/files/snapshots, and Redis is only a job
queue. A separately deployed isolated runner is the only permitted execution
boundary.

`RUNNER_ENABLED=false` is the safe default. In that mode Docker, CI/CD,
Kubernetes, and deployment activities are deterministic simulations.
