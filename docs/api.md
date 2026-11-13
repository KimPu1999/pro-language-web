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

Runner routes are under `/api/v1/runner`: `GET /languages`, `POST /execute`, `GET /jobs/{id}`, `POST /jobs/{id}/cancel`, `GET /exercises/{slug}`, `POST /exercises/{id}/submit`, `GET /submissions`, and editor preference GET/PUT routes. Jobs are scoped to the authenticated student. The API returns `runner_unavailable` when the secure worker is disabled and never executes source in-process.

Challenge routes are under `/api/v1/challenges`: public catalog/detail, authenticated `POST /{id}/run` and `POST /{id}/submit`, owned `GET /submissions/history`, daily challenge, skills, and achievements routes. Admin challenge creation, language/test configuration, and publishing are under `/api/v1/challenges/admin` and require instructor/admin authorization plus CSRF.

Roadmap routes include public `GET /roadmaps` and `/roadmaps/{slug}`, student goal GET/PUT, roadmap start/list/pause/progress, recommendations, and admin roadmap/stage/step/resource/prerequisite/reorder/publish routes under `/api/v1/admin/roadmaps`. Student writes require authentication, verification where enrollment changes, ownership, and CSRF. Admin writes use server-side RBAC.

Project routes include public `GET /projects` and `/projects/{slug}`; student project start/list/detail, milestone updates, GitHub submission, portfolio GET/PUT, approved-project showcase, and public `/u/{username}`; instructor review queue and decision routes; and admin project/milestone creation. Student and review mutations require CSRF, ownership, and role checks.

AI Tutor routes are under `/api/v1/ai`: conversation create/list/detail/rename/delete, authenticated `POST /conversations/{id}/stream` SSE chat, preference GET/PUT, usage status, and admin-only settings/usage inspection. The stream emits `token`, `complete`, or `error` events. The disabled provider returns an explicit unavailable error and persists a failed assistant message. Lesson and challenge context is retrieved only after published-content checks; hidden tests and private records are excluded.

Community routes are under `/api/v1/community`: public feed, post detail, authenticated post/answer/comment/vote/bookmark/snippet/group/report/block operations, public snippets/groups, authenticated notifications, and admin report inspection. State-changing routes require CSRF. Answers can only be accepted by the question owner; private group and moderation expansion remains server-side work.

Live class routes are under `/api/v1/live-classes`: public catalog/detail, authenticated registration/cancellation, room-token status, presence, chat, Q&A, and instructor/admin class creation and scheduling. Room tokens return an explicit unavailable state while `VIDEO_ENABLED=false`. Registration, attendance, and chat access are membership-scoped.

Operations endpoints include `GET /api/v1/health` for liveness and `GET /api/v1/ready` for database readiness. Platform quality and operations checks require `admin` or `super_admin` and report unconfigured dependencies without fabricating health metrics.

Phase 15 operations include student-owned `POST /api/v1/platform/operations/feedback` and `GET /feedback/mine`; administrator-only incident, incident timeline, feedback inbox, engineering issue, release, health-history, and maintenance endpoints under `/api/v1/platform/operations`. Mutations require CSRF protection.
# Learning intelligence (Phase 16)

Authenticated student endpoints are under `/api/v1/learning`: `GET /intelligence`, `/skills`, `/recommendations`, `/study-plans`, `/revision`, and `GET /goals`. Verified students can create study plans, submit recommendation feedback, and record revision attempts with CSRF protection. `POST /coach` returns a truthful unavailable state when AI is disabled. `GET /platform/insights` is restricted to platform administrators and suppresses small groups.

## Career development (Phase 17)

Career routes are under `/api/v1/career`: dashboard, published paths, approved mentors, mentor applications, UTC availability, mentorship requests, private resumes, portfolio-review requests, published interview questions, timed interview sessions, and private job applications. Admin-only routes review mentors and create interview questions. Student mutations require authentication and CSRF tokens.
