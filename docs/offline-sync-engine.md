# Offline sync engine

`POST /api/v1/mobile/sync` accepts at most 100 account-authenticated events. `(user_id,event_id)` is unique for idempotency. Events are `applied`, `conflict`, or replayed with their existing status. Content-version mismatch and deleted/unpublished lessons create explicit conflicts. No event grants a verified challenge score.
