# Incident response

1. Confirm the request ID, UTC time, affected route, and deployment version.
2. Preserve relevant redacted logs and audit events without copying secrets or private content.
3. Disable the affected feature using its server-side flag. Runner, AI, and video paths must fail closed.
4. Revoke sessions or provider credentials when authentication or secret exposure is suspected.
5. Isolate queues and stop retry storms; inspect dead-letter and duplicate events.
6. Recover only in an isolated environment, validate migrations and data integrity, then deploy through CI.
7. Record impact, root cause, corrective action, and follow-up test coverage.

Backup RPO/RTO targets and restore evidence are not configured yet and must be agreed before production launch.
