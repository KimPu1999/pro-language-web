# API

Public routes are under `/api/v1`:

The platform quality endpoint is `GET /api/v1/platform/quality`. It is server-protected by platform RBAC and returns observed configuration/database signals. It intentionally reports unavailable or not-run checks instead of fabricating CI, provider, backup, or isolation success.

Phase 31 adds `/api/v1/status`, `/api/v1/feedback`, `/api/v1/feedback/my`, `/api/v1/support/report-bug`, `/api/v1/platform/monitoring`, `/api/v1/platform/alerts`, `/api/v1/platform/improvements`, `/api/v1/platform/releases`, `/api/v1/platform/feature-flags`, `/api/v1/platform/maintenance`, `/api/v1/platform/backups`, and `/api/v1/platform/reviews`. Mutations require CSRF and appropriate authenticated ownership or platform RBAC.

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

## Collaboration and competitions (Phase 18)

Collaboration routes are under `/api/v1/teams`, `/api/v1/hackathons`, and `/api/v1/competitions`. Team membership and invitation actions are ownership-scoped. Hackathon registration/submission windows and competition registration use server UTC. `/api/v1/platform/collaboration/status` is admin-only and reports whether a CRDT gateway is configured.

## Developer ecosystem (Phase 19)

`GET /api/v1/developers` and `/developers/contributions` are authenticated and ownership-scoped. `GET /api/v1/github/status` reports provider configuration without secrets. Public `GET /api/v1/open-source/projects` and `/open-source/opportunities` return approved/public records only. `GET /api/v1/developers/{username}` returns only opt-in public profiles. `POST /api/v1/github/webhooks` validates GitHub HMAC signatures and delivery IDs; it returns `503` when the provider secret is not configured. Admin integration status is `GET /api/v1/platform/developer-ecosystem/status`.

## Organizations (Phase 20)

Organization routes are under `/api/v1/organizations` and require an active membership for tenant routes. Creation, member changes, invitations, teams, private course mappings, training, settings and exports use CSRF-protected mutations. `/api/v1/platform/organizations` and platform status changes require global admin roles. Analytics suppresses groups smaller than five active members.

## Enterprise security (Phase 21)

Security status and policy routes are under `/api/v1/organizations/{slug}/security`. Account sessions/MFA are under `/api/v1/settings/security`; privacy requests are under `/api/v1/privacy`. SCIM endpoints are under `/api/v1/scim/v2` and return `503` while SCIM is disabled. Compliance controls are platform-admin-only under `/api/v1/platform/compliance`.
## Phase 23 content studio

Tenant authoring endpoints are under `/api/v1/organizations/{slug}/content-studio`: dashboard, projects, generation jobs, lesson drafts, translations, revisions, reviews, quality records, and usage. Publishing is `POST .../projects/{project_id}/publish?revision_id=...` and requires an approved revision plus owner/admin membership. `/api/v1/platform/content-studio` is restricted to platform admins. AI generation returns `provider_unavailable` when no provider is configured.

## Phase 24 learning labs

Lab APIs include `GET /api/v1/labs`, `GET /api/v1/labs/{id}`, `GET /api/v1/me/labs`, workspace creation and file/snapshot/run endpoints, instructor lab endpoints, and `GET /api/v1/platform/labs`. Run responses report `runner_unavailable` when the isolated worker is absent.
## Phase 25 collaboration APIs

The collaboration API includes `/api/v1/collaboration/dashboard`, room CRUD and membership, documents, snapshots, chat, pair sessions, shared execution, recording consent, and `/api/v1/platform/collaboration`. The WebSocket endpoint is `/api/v1/ws/collaboration/{room_id}`. All room operations require authenticated active membership; mutations require CSRF validation.
## Phase 26 cloud lab API

- `GET /api/v1/cloud-labs/catalog`
- `GET /api/v1/cloud-labs/dashboard`
- `GET /api/v1/cloud-labs/{lab_id}`
- `POST /api/v1/cloud-labs/{lab_id}/workspaces`
- `GET /api/v1/cloud-labs/workspaces/{workspace_id}`
- `PATCH /api/v1/cloud-labs/workspaces/{workspace_id}/lifecycle`
- `PUT /api/v1/cloud-labs/workspaces/{workspace_id}/files`
- `POST /api/v1/cloud-labs/workspaces/{workspace_id}/snapshots`
- `GET /api/v1/cloud-labs/modes`
- `GET /api/v1/cloud-labs/platform/operations`

All mutating endpoints require an authenticated verified user and CSRF token.
Workspace data is ownership-scoped. Operations requires platform RBAC.

## Phase 27 cybersecurity API

- `GET /api/v1/cybersecurity/dashboard`
- `GET /api/v1/cybersecurity/paths` and `/paths/{slug}`
- `GET /api/v1/cybersecurity/labs` and `/labs/{id}`
- `POST /api/v1/cybersecurity/labs/{id}/attempts`
- `POST /api/v1/cybersecurity/attempts/{id}/evaluate`
- `POST /api/v1/cybersecurity/assessment/targets`
- `GET|POST /api/v1/cybersecurity/threat-models`
- `GET /api/v1/cybersecurity/ai-tutor/status`
- `GET /api/v1/cybersecurity/platform/operations`
- `GET|POST /api/v1/cybersecurity/instructor/labs`

Mutations require an authenticated verified user and CSRF token. Evaluation accepts only an owned learning workspace and never accepts a URL or arbitrary target. Platform operations use server-side platform RBAC.

## Phase 28 mobile API

- `GET /api/v1/mobile/dashboard` and `/library`
- `POST /api/v1/mobile/manifests`
- `GET /api/v1/mobile/manifests/{id}/content`
- `POST /api/v1/mobile/sync`
- `GET|PUT /api/v1/mobile/preferences`
- `GET|PUT /api/v1/mobile/notifications`
- `POST /api/v1/mobile/push-subscriptions`
- `DELETE /api/v1/mobile/push-subscriptions`
- `POST /api/v1/mobile/devices`
- `GET /api/v1/mobile/instructor/offline-settings`
- `GET /api/v1/mobile/platform/operations`

Manifests and content are ownership-scoped and published-only. Sync is idempotent per user/event ID and returns explicit conflicts for deleted content or version mismatch. Push delivery reports `not_configured` until a provider is installed.

## Phase 29 AI companion API

- `GET|PUT /api/v1/ai-companion/profile`
- `GET /api/v1/ai-companion/dashboard`
- `GET|POST /api/v1/ai-companion/study-sessions`
- `PATCH /api/v1/ai-companion/study-sessions/{id}`
- `GET /api/v1/ai-companion/revision`
- `POST /api/v1/ai-companion/revision/{id}/review`
- `GET /api/v1/ai-companion/recommendations`
- `GET|POST /api/v1/ai-companion/goals`
- `GET /api/v1/ai-companion/insights` and `/planner`
- `GET|POST /api/v1/ai-companion/voice/status` and `/voice/sessions`
- `DELETE /api/v1/ai-companion/privacy`
- `GET /api/v1/ai-companion/instructor/insights`
- `GET /api/v1/ai-companion/platform/operations`

Existing `/api/v1/ai/conversations` and `/stream` provide user-owned SSE chat. Companion mutations require verified authentication and CSRF; provider availability is never inferred from UI state.

## Phase 32 scalability API

- `GET /api/v1/platform/scalability`
- `GET /api/v1/platform/scalability/{database|workers|runners|cdn|ai|costs}`
- `GET|POST /api/v1/platform/scalability/policies`
- `GET|POST /api/v1/platform/scalability/events`
- `GET|POST /api/v1/platform/scalability/recovery`

All scalability endpoints require platform-admin RBAC. Mutations require the
existing CSRF token. Policy and event writes are evidence/policy records only;
they do not invoke an autoscaler or change infrastructure.

## Phase 33 marketplace API

- `GET /api/v1/marketplace`
- `GET /api/v1/marketplace/search`
- `GET /api/v1/marketplace/resources` and `/resources/{slug}`
- `GET /api/v1/marketplace/instructors/{slug}`
- `GET /api/v1/marketplace/recommended`
- `POST /api/v1/marketplace/resources`; `PATCH /resources/{id}`; `POST /resources/{id}/submit`
- `POST /api/v1/marketplace/resources/{id}/reviews` and `/report`
- `GET|POST /api/v1/marketplace/collections`; `POST /collections/{id}/items`
- `GET /api/v1/marketplace/moderation/queue`; `POST /moderation/reviews/{id}`
- `GET /api/v1/marketplace/analytics` and `/instructor/analytics`

Public endpoints filter published/public content server-side. Mutations require
verified authentication, CSRF, ownership or moderation authorization, and
resource-specific rate limits.

## Phase 34 Instructor Academy API

- `GET|POST /api/v1/instructor-academy/onboarding`
- `GET /api/v1/instructor-academy/dashboard|standards|training|development|quality|analytics|ai-coach|certifications`
- `POST /api/v1/instructor-academy/training/{id}/enroll`
- `POST /api/v1/instructor-academy/development`
- `POST /api/v1/instructor-academy/peer-reviews`
- `POST /api/v1/instructor-academy/appeals`
- `GET /api/v1/instructor-academy/platform/overview|applications`
- `POST /api/v1/instructor-academy/platform/applications/{id}`

Role activation is performed only by authorized platform administrators after
an application decision. Quality, review, and certification endpoints remain
evidence-driven.
