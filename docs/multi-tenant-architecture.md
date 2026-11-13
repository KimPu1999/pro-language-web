# Multi-tenant architecture

CodeMaster uses a shared application and shared PostgreSQL database. An authenticated request resolves a tenant from a path slug, then checks the current user’s active `organization_memberships` row. Every organization query in the Phase 20 API includes the resolved organization ID; client-supplied organization IDs are not used as authorization.

Tenant cache and worker keys must use `organization_id` as a namespace component. Exports and future object storage keys must also include the organization namespace. PostgreSQL RLS is a defense-in-depth follow-up once the connection pool can safely set and clear a transaction-local tenant context.
