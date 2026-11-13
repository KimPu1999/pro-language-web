# Phase 20 enterprise audit

The platform had global session authentication, global platform roles, public courses, existing developer teams, analytics, Redis configuration and additive Alembic migrations. It had no organization membership or tenant context before Phase 20. Existing developer teams remain separate; organization teams use separate tables and membership checks.

Phase 20 adds an additive organization boundary. Organization records, members, invitations, teams, private course assignments, training programs, assessments, analytics, exports, settings, security events, resource usage and support access all carry `organization_id` where applicable. Route dependencies resolve the organization by slug and then require an active membership before querying tenant records.

## Known gaps

- PostgreSQL RLS policies are not enabled yet; application-level tenant checks are active and RLS should be added after deployment role/session-variable conventions are finalized.
- Existing global course/enrollment/progress tables are not rewritten to add a tenant column. Organization-private access is represented by `organization_courses`; public learning remains unchanged.
- The first implementation provides training/assessment records and verified-attempt fields. Full question authoring and runner-backed organization assessment workflows remain follow-up work.
- Organization report exports are queued records only; a worker and private object-storage delivery must be configured before exports are marked complete.

All unconfigured services must display `Not Configured`, `Unknown`, or an unavailable state.
