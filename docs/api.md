# API

Public routes are under `/api/v1`:

- `GET /health`
- `GET /languages`
- `GET /categories`
- `GET /courses?search=&language=&level=&category=&page=&page_size=`
- `GET /courses/{slug}`
- `GET /courses/{slug}/modules`
- `GET /lessons/{id}`
- `GET /paths`

Course results are paginated and only published courses, modules, lessons, and paths are exposed.

Authentication routes include `POST /auth/register`, `POST /auth/login`, `POST /auth/logout`, `GET /auth/me`, `GET /auth/verify-email`, `POST /auth/resend-verification`, `POST /auth/forgot-password`, `POST /auth/reset-password`, and `POST /auth/change-password`.

Authenticated student routes include `GET/PATCH /me/profile`, `GET /me/enrollments`, `POST /me/enrollments/{course_slug}`, `GET /me/dashboard`, `POST /me/lessons/{lesson_id}/progress`, and `POST /me/sessions/revoke-others`. Cookie-authenticated state changes require the `X-CSRF-Token` header matching the CSRF cookie. Enrollment and progress mutations require verified email.

Admin routes are under `/api/v1/admin`: dashboard statistics, language/category list and mutation routes, course list/create/update/duplicate/archive routes, builder and curriculum routes, module/lesson/example creation, and publishing decisions. Every mutation requires an authenticated administrator or authorized instructor plus CSRF validation. Instructors are checked against course ownership or `course_instructors`.
