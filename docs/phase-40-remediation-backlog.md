# Phase 40 Remediation Backlog

## Resolved

- P1: Assessment grading endpoint referenced undefined `AssessmentGradeRevision`.
  Fixed import; Ruff now passes.
- P1: Platform system-health quality contract lacked regression coverage and
  had a duplicate-route risk. Covered the existing authenticated
  `/api/v1/platform/quality` endpoint without introducing a second source.
- P2: CI Ruff gate had unused imports/locals across existing assessment, career,
  community, gamification, and test files. Safe fixes applied.

## Release blockers still open

- P0/P1 evidence gap: no live PostgreSQL migration rehearsal in this environment.
- P1: secure runner is disabled by default and has no Phase 40 isolation test
  against a real worker.
- P1: Redis, AI, WebSocket/Yjs, object storage, email, and backup providers are
  not configured or verified.
- P1: no Playwright end-to-end regression run against a running frontend/API.
- P2: many later-phase pages are entry shells or truthful “not configured”
  surfaces rather than complete production workflows.
