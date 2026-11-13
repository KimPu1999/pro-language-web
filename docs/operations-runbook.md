# Operations runbook

1. Check `/api/v1/health` and `/api/v1/ready`.
2. Capture `X-Request-ID`, UTC time, deployment version, and affected service.
3. Review application logs, database readiness, Redis/worker queues, and provider status.
4. Disable runner, AI, or video with server-side flags if isolation/provider health is uncertain.
5. Create or update an incident and append a timeline event.
6. Roll back only to a schema-compatible artifact after approval; use forward migrations for schema repair.
7. Validate authentication, public course access, and critical smoke tests before closing the incident.

Backups, restores, alerts, and external telemetry are not verified in this workspace.
