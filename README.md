# CodeMaster Academy

CodeMaster Academy is a free programming learning platform for beginner, intermediate, and professional learners. Phase 1 provides a public learning experience backed by a versioned FastAPI API and PostgreSQL-ready SQLAlchemy models. Authentication, enrollment writes, and code execution are intentionally deferred.

## Prerequisites

- Node.js 20+
- npm 10+
- Python 3.11+
- PostgreSQL 15+

## Quick start

```bash
cp backend/.env.example backend/.env
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

In another terminal:

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open http://localhost:3000. The frontend expects the API at `http://localhost:8000` by default.

## PostgreSQL setup

Start PostgreSQL, then create the database before running migrations. With the
default local PostgreSQL user, run:

```bash
createdb -h localhost -U postgres codemaster
```

If `createdb` is unavailable, use:

```bash
psql -h localhost -U postgres -d postgres -c "CREATE DATABASE codemaster;"
```

If the database already exists, PostgreSQL will report that and you can continue.
Set `DATABASE_URL` in `backend/.env`, for example:

```text
DATABASE_URL=postgresql+psycopg://postgres:postgres@localhost:5432/codemaster
```

SQLite is used by the backend test suite. Production and local development use PostgreSQL.

## Commands

```bash
# backend
cd backend && source .venv/bin/activate
alembic upgrade head
python -m app.seed
PYTHONPATH=. pytest

# frontend
cd frontend
npm run test:unit
npm run lint
npm run typecheck
npm run build
npm run test:e2e
```

Phase 13 adds the quality workflow, administrator quality page at `/platform/quality`, request correlation headers, frontend unit tests, and production-readiness documentation. Run `git diff --check` before commits. The secure runner, video provider, external AI provider, telemetry backend, backup restore, and staging load tests remain explicitly unavailable until configured and verified.

Phase 14 adds deployment preparation: a non-root backend image, readiness endpoint (`/api/v1/ready`), environment-variable boundaries, deployment architecture, rollback, backup, monitoring, and launch documentation. No cloud deployment is claimed; provider credentials, domains, managed services, staging, restore tests, and final Go/No-Go approval are still required.

## Environment variables

Backend: `DATABASE_URL`, `CORS_ORIGINS`, `LOG_LEVEL`, session/token TTLs, cookie settings, `APP_BASE_URL`, and mailer/SMTP settings. `MAILER_MODE=console` is the development default; SMTP credentials are only read from environment variables.

Frontend: `NEXT_PUBLIC_API_BASE_URL`.

No secret is required for Phase 1.

Phase 2 adds student accounts. Run `alembic upgrade head` after updating the environment. Registration creates student accounts only. In production set `COOKIE_SECURE=true`, use HTTPS, configure trusted `CORS_ORIGINS`, and configure an SMTP or transactional mail provider. Sessions are server-side and the browser stores only HttpOnly session cookies plus a CSRF double-submit cookie.

Phase 3 adds the admin control center at `/admin`. Only `admin` and `super_admin` accounts can use platform-wide CMS operations. Instructors may manage assigned or owned courses through server-side ownership checks. Apply migration `0003_course_cms` before using the CMS.

Phase 4 adds the interactive classroom foundation and migration `0004_interactive_classroom`. The Monaco editor, exercise/submission records, Redis queue adapter, and ownership-protected job APIs are included. Code execution is disabled by default (`RUNNER_ENABLED=false`) and must only be enabled with a separately deployed hardened sandbox worker. See [docs/code-execution.md](docs/code-execution.md), [docs/sandbox-security.md](docs/sandbox-security.md), and [docs/runner-deployment.md](docs/runner-deployment.md).

Phase 5 adds migration `0005_challenges_assessments`, the challenge catalog, workspace, challenge submission records, skill dashboard, daily challenge contract, achievements schema, and admin challenge creation. Challenge submissions remain safely unavailable until the Phase 4 isolated runner is deployed.

Phase 6 adds migration `0006_personalized_roadmaps`, career roadmap catalog/detail pages, student learning goals, evidence-based roadmap enrollment/progress, prerequisite validation, deterministic recommendations, and roadmap administration. See [docs/personalized-learning.md](docs/personalized-learning.md), [docs/roadmap-builder.md](docs/roadmap-builder.md), and [docs/recommendation-engine.md](docs/recommendation-engine.md).

Phase 8 adds migration `0008_ai_tutor`, the authenticated AI Tutor conversation API, SSE streaming contract, lesson/challenge context filtering, server-side quotas, preferences, usage records, and `/ai-tutor` plus `/admin/ai`. AI is disabled by default. Configure a reviewed provider adapter on the server before enabling live requests; no API key is sent to the browser. See [docs/ai-tutor.md](docs/ai-tutor.md), [docs/ai-provider-setup.md](docs/ai-provider-setup.md), [docs/ai-security.md](docs/ai-security.md), and [docs/ai-usage-limits.md](docs/ai-usage-limits.md).

Phase 9 adds migration `0009_certificates_gamification`, certificate verification/PDF endpoints, achievements summary, XP balance and event ledgers, streak records, and opt-in leaderboard APIs. See the certificate and gamification documentation for issuance and privacy rules.

Phase 10 adds migration `0010_community`, public community feed and Q&A APIs, comments, votes, bookmarks, snippets, study groups, reports, blocks, notifications, and the first community pages. Shared code is stored as text and is never executed by the API process.

Phase 11 adds migration `0011_live_classes`, live-class catalog/detail pages, UTC session scheduling, registration, capacity/waitlist records, room access checks, attendance/presence, chat, Q&A, and a disabled-by-default video provider boundary. Configure `VIDEO_PROVIDER` and `VIDEO_ENABLED` only after integrating a supported provider adapter.

Phase 12 adds migration `0012_analytics`, real database-backed platform analytics, scoped instructor analytics, administrator-only CSV reporting, and export audit records. Open `/platform/analytics` after signing in as an administrator. See `docs/phase-12-analytics.md`, `docs/analytics-api.md`, and `docs/analytics-security.md`.

Phase 7 adds migration `0007_projects_portfolio`, project templates, student workspaces, GitHub submission validation, instructor review records, weighted rubrics, verified project skill evidence, and private/public portfolio routes. See [docs/project-based-learning.md](docs/project-based-learning.md), [docs/project-review-workflow.md](docs/project-review-workflow.md), [docs/github-integration.md](docs/github-integration.md), and [docs/portfolio-builder.md](docs/portfolio-builder.md).

## Troubleshooting

- If the API cannot connect, verify PostgreSQL is running and `DATABASE_URL` points to an existing database.
- If migrations fail with `database "codemaster" does not exist`, create it with the PostgreSQL commands above, then rerun `alembic upgrade head`.
- If the UI shows an API error, start FastAPI on port 8000 or change `NEXT_PUBLIC_API_BASE_URL`.
- Run `alembic current` and `alembic upgrade head` to inspect migration state.

See [docs/architecture.md](docs/architecture.md), [docs/database.md](docs/database.md), [docs/api.md](docs/api.md), and [docs/roadmap.md](docs/roadmap.md).

# Phase 16 learning intelligence

Student intelligence pages are available at `/dashboard/intelligence`, `/dashboard/skills`, `/dashboard/recommendations`, `/dashboard/study-plan`, `/dashboard/revision`, and `/dashboard/ai-coach`. Scores use verified persisted evidence; insufficient evidence is shown as `Not Yet Assessed`. AI coach responses remain unavailable until a server-side provider is configured.

# Phase 17 career development

Career pages include `/dashboard/career`, `/career/paths`, `/mentorship/mentors`, `/career/resume-builder`, `/career/interviews`, and `/career/applications`. Mentor profiles require administrator approval. Resume and application records are private to the authenticated student.

## Phase 19 developer ecosystem

The developer hub is available at `/developers`; public open-source discovery is available at `/open-source` and `/open-source/opportunities`. GitHub is disabled by default and displays `Not Configured` until a reviewed OAuth/App deployment is configured. Verified contribution records are server-synced and ownership-scoped; user-submitted links never become verified evidence.

## Phase 20 organizations

Organization workspaces are available at `/organizations` and `/organization/[slug]/dashboard`. Organization data is membership-scoped, public learning remains free, and private training/analytics are not available to users outside the organization. PostgreSQL migration `0018_organizations` is additive.

## Phase 21 security

Organization security is available at `/organization/[slug]/security`; account sessions and MFA status are under `/settings/security`. OIDC, SAML, TOTP, passkeys, and SCIM show `Not Configured` until maintained protocol libraries and deployment credentials are installed. The compliance page never claims certification.

## Phase 23 content studio

Instructor content authoring is available under `/instructor/content-studio`, with platform oversight at `/platform/content-studio`. Migration `0021_content_studio` adds tenant-scoped drafts, generation jobs, translations, quality checks, review decisions, revisions, publications, usage, and audit logs. AI generation remains `Not Configured` unless a real provider and worker are configured. No AI-generated content is published without an independent approved revision.

## Phase 22 automation

Organization automation is available at `/organization/[slug]/automation`, with workflow drafts at `/organization/[slug]/automation/builder` and platform oversight at `/platform/automation`. Migration `0020_automation` adds tenant-scoped workflow versions, durable queued runs, approvals, idempotency, agent permissions, recommendations, templates, usage, security events, and audit logs. No worker, scheduler, or live AI agent provider is configured by default; those surfaces show truthful unavailable states.

## Phase 24 learning labs

Learning labs are available at `/labs` and `/dashboard/labs`; workspaces use `/labs/{labId}/workspace`. Migration `0022_learning_labs` adds lab versions, owned files, snapshots, execution records, progress, reviews, and audit logs. Code execution, SQL environments, controlled API targets, and AI assistance show truthful unavailable states until isolated services are configured.
## Phase 25 collaboration

Phase 25 adds authenticated collaboration rooms, durable document/update/snapshot records, room chat, pair-role controls, consent records, and a disabled-by-default WebSocket gateway. Run `alembic upgrade head` to apply migration `0023_collaboration`. Real-time editing, isolated execution, AI assistance, and recordings show truthful unavailable states until their providers are configured.

## Phase 26 cloud labs

Cloud lab routes are available at `/cloud-labs`, `/dashboard/cloud-labs`,
`/cloud-labs/workspaces/[workspaceId]`, `/instructor/cloud-labs`, and
`/platform/cloud-labs`. Phase 26 reuses the Phase 24 learning-lab schema and
adds migration `0028_cloud_lab_indexes` for dashboard, lifecycle, and audit
queries. Docker, CI/CD, Kubernetes, and deployment are simulation-only until
an isolated worker or preview service is separately configured. The FastAPI
host never executes student commands and never exposes a Docker socket.

## Phase 27 cybersecurity learning

Cybersecurity catalog, learning paths, lab attempts, threat-model drafts, AI provider status, instructor authoring, and platform operations are available under `/cybersecurity`, `/instructor/cybersecurity`, and `/platform/cybersecurity`. Migration `0029_cybersecurity_training` is additive. Evaluation is server-side and runner-gated; arbitrary external targets, public vulnerable targets, automatic scoring, and platform-secret access remain disabled.

## Phase 28 mobile/offline learning

Mobile learning routes include `/dashboard/mobile`, `/offline/library`, `/offline/downloads`, `/offline/lessons/[lessonId]`, `/settings/notifications`, `/instructor/offline-settings`, and `/platform/mobile`. Migration `0030_mobile_offline` adds account-scoped manifests, sync events/conflicts, preferences, push subscriptions, and audit records. API responses are never cached and offline progress is not verified grading.

## Phase 29 AI learning companion

AI companion routes include `/dashboard/ai-companion`, `/ai-companion/chat`, `/ai-companion/study`, `/ai-companion/revision`, `/ai-companion/practice`, `/ai-companion/goals`, `/ai-companion/insights`, `/ai-companion/planner`, `/ai-companion/voice`, `/settings/ai-companion`, `/instructor/ai-learning-insights`, and `/platform/ai-companion`. Migration `0031_ai_companion` adds adaptive sessions, goals, recommendations, revision records, privacy metadata, and operations records. Existing AI chat/SSE remains provider-gated; voice is `Not Configured` by default.

## Phase 30 quality and launch readiness

The quality center is available at `/platform/quality-center` and reuses the server-protected platform quality API. The Phase 30 recommendation is currently NO-GO for production until staging migration, restore, browser, isolation, accessibility, performance, provider, and rollback evidence is attached. See `docs/phase-30-release-readiness.md`.

## Phase 31 operations

Post-launch operations are available at `/platform/operations`, `/platform/monitoring`, `/platform/incidents`, `/platform/improvements`, `/platform/releases`, `/platform/feature-flags`, `/platform/maintenance`, and `/platform/backups`. Student feedback is available at `/feedback`, bug reporting at `/support/report-bug`, and public status at `/status`. These surfaces show recorded evidence and explicit unavailable states; they do not fabricate telemetry or backup health.

## Phase 32 scalability

Scalability evidence is available at `/platform/scalability` and its database,
workers, runners, CDN, AI, costs, policies, events, and recovery subpages.
Migration `0033_scalability` is additive. These surfaces record measurements,
policies, and recovery evidence but do not provision paid resources or change
production capacity. Local and provider-backed telemetry remain explicitly
`not_tested` or `not_configured` until connected and verified.

## Phase 33 learning marketplace

The free marketplace is available at `/marketplace`, `/marketplace/search`,
`/marketplace/resources`, `/marketplace/recommended`, `/marketplace/collections`,
and `/contributor/studio`. It reuses published courses and instructor profiles,
while community resources use additive migration `0034_marketplace`. There are
no paid courses, checkout, subscriptions, payment gateways, commissions, or
paywalls. Draft resources require human moderation before publication.
