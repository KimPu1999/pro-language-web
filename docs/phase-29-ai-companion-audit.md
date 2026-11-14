# Phase 29 AI companion audit

The repository already provides `/api/v1/ai` conversations, authenticated SSE, provider abstraction, redaction, quotas, usage records, learning intelligence, deterministic revision, study plans, goals, challenges, labs, offline learning, notifications, and tenant/RBAC boundaries. Phase 29 reuses the existing AI chat transport and adds an adaptive companion boundary under `/api/v1/ai-companion`.

The configured provider is inspected through existing settings. When disabled or unsupported, the companion reports `not_configured`; it never fabricates answers, mastery, grades, voice output, or usage.
