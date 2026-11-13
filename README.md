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

Create a database and set `DATABASE_URL` in `backend/.env`, for example:

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
npm run lint
npm run typecheck
npm run build
npm run test:e2e
```

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

Phase 7 adds migration `0007_projects_portfolio`, project templates, student workspaces, GitHub submission validation, instructor review records, weighted rubrics, verified project skill evidence, and private/public portfolio routes. See [docs/project-based-learning.md](docs/project-based-learning.md), [docs/project-review-workflow.md](docs/project-review-workflow.md), [docs/github-integration.md](docs/github-integration.md), and [docs/portfolio-builder.md](docs/portfolio-builder.md).

## Troubleshooting

- If the API cannot connect, verify PostgreSQL is running and `DATABASE_URL` points to an existing database.
- If the UI shows an API error, start FastAPI on port 8000 or change `NEXT_PUBLIC_API_BASE_URL`.
- Run `alembic current` and `alembic upgrade head` to inspect migration state.

See [docs/architecture.md](docs/architecture.md), [docs/database.md](docs/database.md), [docs/api.md](docs/api.md), and [docs/roadmap.md](docs/roadmap.md).

