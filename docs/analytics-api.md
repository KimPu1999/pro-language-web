# Analytics API

Authenticated routes:

```text
GET  /api/v1/platform/analytics/overview
GET  /api/v1/platform/analytics/students
GET  /api/v1/platform/analytics/courses
GET  /api/v1/platform/analytics/instructors
GET  /api/v1/platform/analytics/challenges
GET  /api/v1/platform/analytics/learning
GET  /api/v1/platform/analytics/certificates
GET  /api/v1/platform/analytics/community
GET  /api/v1/platform/reports
POST /api/v1/platform/reports/export
```

Analytics endpoints accept `start_date` and `end_date` in `YYYY-MM-DD` format. The export endpoint requires a valid CSRF double-submit token and returns CSV. All errors use the existing API error conventions.
