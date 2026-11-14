# Phase 30 launch checklist

- [x] Frontend typecheck, lint, unit tests, and build pass locally.
- [x] Backend Ruff correctness gate and full Pytest suite pass locally.
- [x] Migration chain has one head (`0031_ai_companion`).
- [x] Platform quality center route exists and is server-protected.
- [ ] PostgreSQL migration rehearsal on staging.
- [ ] Backup restore drill with measured RPO/RTO.
- [ ] Playwright smoke suite with installed browser.
- [ ] Tenant-isolation staging matrix.
- [ ] Secure runner isolation validation.
- [ ] AI provider, email, Redis, collaboration, cloud, and push provider verification.
- [ ] Accessibility audit.
- [ ] Load and performance measurements.
- [ ] Rollback rehearsal and monitoring alert test.

The unchecked items are release blockers.
