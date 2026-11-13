# Tenant isolation

The API returns `401` for anonymous requests and `403` when an authenticated user is not an active member of the requested organization. Membership, team, training, analytics, course mapping, settings and export records are all filtered by the resolved tenant. Cross-tenant tests cover workspace and organization listing boundaries.
