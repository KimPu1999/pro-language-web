# Deployment notes

## Phase 32 prerequisites

The Phase 32 scalability console is safe to run without provisioning new paid
resources. Before enabling production scaling integrations, operators must
provide a production-like staging environment, authenticated telemetry, a
rollback plan, a tested database backup/restore path, and explicit approval for
any capacity change.

The API is designed for multiple instances when session validation, rate-limit
state, queues, and durable application state use shared services. This has not
been multi-instance tested in the local repository. Read replicas, CDN/object
storage delivery, runner autoscaling, active-active regions, and provider-backed
AI capacity are configuration choices, not local defaults.

Run the additive migration only after reviewing the environment and backup:

```bash
cd backend
PYTHONPATH=. python3 -m alembic upgrade head
```

No deployment or migration is run automatically by this project change.
