# Learning path API

- `GET /api/v1/learning-paths` — published, paginated list with `search`, `career_category`, `difficulty`, `page`, and `page_size`.
- `GET /api/v1/learning-paths/{slug}` — published detail including stages and steps.
- `GET /api/v1/learning-paths/{slug}/stages` — published stages.
- `GET /api/v1/learning-paths/{slug}/courses` — published courses referenced by steps.
- `POST /api/v1/learning-paths/{id}/enroll` — verified student enrollment with CSRF protection.
- `POST /api/v1/learning-paths/{id}/bookmark` — authenticated bookmark toggle.
- `GET /api/v1/me/learning-paths` — current user's enrollments and real progress.
- `GET /api/v1/me/learning-paths/{id}/progress` — ownership-scoped progress.

Legacy `/roadmaps` endpoints remain available for compatibility.
