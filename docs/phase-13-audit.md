# Phase 13 audit

Audited 2026-11-13. The repository is a single-tenant Next.js App Router and FastAPI application with PostgreSQL/Alembic, Redis queues, challenge runner hooks, AI routes, live-class routes, community routes, analytics, and Playwright smoke coverage.

## Findings

| Severity | Finding | Evidence / impact | Action |
|---|---|---|---|
| High | Secure runner is not configured | `RUNNER_ENABLED=false`; queue fails closed and no worker implementation is present in this repository | Keep execution disabled until an isolated worker, network policy, resource limits, cleanup, and integration tests exist |
| High | Video provider is not configured | No provider adapter or verified webhook implementation is present | Room-token endpoint now returns unavailable/503 instead of random bearer-like tokens |
| High | Production CI and security gates were absent | No GitHub Actions workflow was present at audit start | Add the quality workflow and keep secrets out of untrusted PR jobs |
| Medium | Frontend unit-test layer was absent | Only Playwright smoke coverage existed | Added Vitest + React Testing Library setup and shared component tests |
| Medium | Observability is partial | Request correlation headers are now emitted, but no OpenTelemetry/error backend is configured | Keep quality page explicit; configure telemetry before production |
| Medium | Analytics has on-demand per-enrollment lesson queries | `completion_rows` performs repeated aggregate queries | Benchmark and replace with grouped queries before high-volume use |
| Medium | Community content sanitization is minimal | Current community paths keep user content as text and apply limited URL/script filtering; no rich HTML renderer exists | Keep rich HTML disabled; adopt a maintained sanitizer before enabling HTML/Markdown rendering |
| Low | Dependency audit is not reproducible offline | `npm audit` could not reach registry in this environment; Python audit tool is not installed | Run scans in CI with network access and review high/critical findings |
| Operational | Backup restore and load tests are unverified | No backup service or k6 setup is present in the repository | Validate in isolated staging and record RPO/RTO evidence |

Tenant isolation is not applicable to the current single-tenant schema. If tenants are introduced, every resource and analytics query needs a tenant key and isolation tests before release.

## Verified fixes

- Added request correlation and baseline security response headers.
- Added an administrator-only `/api/v1/platform/quality` status endpoint and `/platform/quality` page. It reports unconfigured dependencies explicitly.
- Closed the live-room token path when the provider adapter is unavailable.
- Added Vitest/React Testing Library checks for shared UI and Myanmar preference behavior.
- Added a least-privilege CI workflow for type checking, linting, unit tests, backend tests, dependency audits, migrations, and Playwright smoke tests.

## Remaining release blockers

The runner, video provider, external AI provider, production telemetry, backup restore, staging load test, and production dependency audit are not configured or verified. They must remain release gates for any deployment that advertises those features.
