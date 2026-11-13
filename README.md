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
pytest

# frontend
cd frontend
npm run lint
npm run typecheck
npm run build
npm run test:e2e
```

## Environment variables

Backend: `DATABASE_URL`, `CORS_ORIGINS`, `LOG_LEVEL`.

Frontend: `NEXT_PUBLIC_API_BASE_URL`.

No secret is required for Phase 1.

## Troubleshooting

- If the API cannot connect, verify PostgreSQL is running and `DATABASE_URL` points to an existing database.
- If the UI shows an API error, start FastAPI on port 8000 or change `NEXT_PUBLIC_API_BASE_URL`.
- Run `alembic current` and `alembic upgrade head` to inspect migration state.

See [docs/architecture.md](docs/architecture.md), [docs/database.md](docs/database.md), [docs/api.md](docs/api.md), and [docs/roadmap.md](docs/roadmap.md).

