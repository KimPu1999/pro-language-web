# Incident management

Incidents use `detected`, `acknowledged`, `investigating`, `mitigating`, `resolved`, and `closed` statuses. Admins create and transition incidents; every transition appends an immutable timeline event. Resolution notes are restricted to administrators.

API: `GET/POST /api/v1/platform/operations/incidents`, `GET/PATCH /incidents/{id}`. State changes require the server session and CSRF token.
