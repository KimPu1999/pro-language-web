# Automation scheduling

The schema supports event and schedule triggers with organization-scoped configuration and `next_run_at`. A scheduler worker is not configured yet, so no scheduled execution is claimed. A future scheduler must use row locking or an equivalent lease and idempotency keys to prevent duplicate runs across workers.
