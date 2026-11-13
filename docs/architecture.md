# Architecture

The repository is a two-app monorepo. `frontend` is a Next.js App Router application using server components for public course detail and a small client boundary for search and Myanmar preference. `backend` is a FastAPI application with versioned read-only public routes. SQLAlchemy models are shared by Alembic and the seed command.

The public boundary exposes published records only. Authentication, enrollment mutations, progress writes, administration, payments, and code execution are Phase 2 concerns.

Phase 2 adds a server-managed session boundary. Passwords use Argon2id; raw session and recovery tokens are never stored. Authentication cookies are HttpOnly and SameSite-configurable, and state-changing cookie requests require a CSRF header. Public registration hard-codes the `student` role. Student dashboards calculate progress from published lessons and enrollment rows rather than accepting client-provided percentages.

Phase 3 adds an authenticated CMS boundary under `/api/v1/admin`. Admins and super admins can manage taxonomy, courses, curriculum, lessons, examples, and publishing. Instructors are restricted to courses they own or are assigned through `course_instructors`. Course revisions, publishing reviews, and admin audit records preserve workflow history. Public course queries continue to filter on `published`.
