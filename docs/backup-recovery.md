# Backup and recovery

Backups and restore are not configured or verified here. Production must use encrypted managed PostgreSQL backups, private object-storage versioning, retention policy, and an isolated restore test.

Suggested targets are RPO 24 hours and RTO 4 hours until the operator approves stricter targets. Record the restore timestamp, schema revision, row-integrity checks, and application smoke results. Never test restore procedures against production.
