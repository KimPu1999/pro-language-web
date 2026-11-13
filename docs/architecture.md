# Architecture

The repository is a two-app monorepo. `frontend` is a Next.js App Router application using server components for public course detail and a small client boundary for search and Myanmar preference. `backend` is a FastAPI application with versioned read-only public routes. SQLAlchemy models are shared by Alembic and the seed command.

The public boundary exposes published records only. Authentication, enrollment mutations, progress writes, administration, payments, and code execution are Phase 2 concerns.
