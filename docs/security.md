# Security

Security controls are enforced server-side through authentication dependencies,
RBAC, CSRF checks, tenant-scoped queries, hashed session tokens, input
validation, rate limits, audit records, and isolated-runner boundaries.

Phase 40 release status is **NO-GO** until staging verifies PostgreSQL tenant
isolation, runner/container isolation, dependency scanning, TLS/CORS/cookie
configuration, Redis access controls, backup encryption, and WebSocket
authorization. See `phase-40-security-audit.md`.
