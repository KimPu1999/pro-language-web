# AI Provider Setup

AI is disabled by default:

```env
AI_PROVIDER=disabled
AI_MODEL=disabled
AI_ENABLED=false
AI_REQUEST_TIMEOUT_SECONDS=30
AI_DAILY_REQUEST_LIMIT=20
AI_MAX_INPUT_CHARS=12000
```

The current Phase 8 adapter deliberately does not make external requests. A production provider must be implemented behind `backend/app/ai_service.py`, keep credentials in the deployment secret manager or environment, enforce timeouts, redact sensitive values, and return token usage. Never add a provider key to a `NEXT_PUBLIC_*` variable or persist it in PostgreSQL.

For automated tests, `AI_PROVIDER=mock` with `AI_ENABLED=true` uses the local deterministic adapter and does not require network access or paid credentials.
