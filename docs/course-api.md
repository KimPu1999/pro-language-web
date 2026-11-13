+# Course API

Public endpoints:

- `GET /api/v1/courses`
- `GET /api/v1/courses/{slug}`
- `GET /api/v1/courses/{slug}/modules`
- `GET /api/v1/lessons/{lesson_id}`
- `GET /api/v1/languages`
- `GET /api/v1/categories`

Authenticated endpoints:

- `POST /api/v1/me/enrollments/{course_slug}`
- `POST /api/v1/me/lessons/{lesson_id}/progress`
- `POST /api/v1/me/lessons/{lesson_id}/bookmark`
- `GET /api/v1/me/dashboard`

Mutation endpoints require a verified session and CSRF token. Published lesson
reads do not expose private progress, bookmarks, hidden tests, or authoring
records.

