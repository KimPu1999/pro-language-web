# Architecture

The repository is a two-app monorepo. `frontend` is a Next.js App Router application using server components for public course detail and a small client boundary for search and Myanmar preference. `backend` is a FastAPI application with versioned read-only public routes. SQLAlchemy models are shared by Alembic and the seed command.

The public boundary exposes published records only. Authentication, enrollment mutations, progress writes, administration, payments, and code execution are Phase 2 concerns.

Phase 2 adds a server-managed session boundary. Passwords use Argon2id; raw session and recovery tokens are never stored. Authentication cookies are HttpOnly and SameSite-configurable, and state-changing cookie requests require a CSRF header. Public registration hard-codes the `student` role. Student dashboards calculate progress from published lessons and enrollment rows rather than accepting client-provided percentages.

Phase 3 adds an authenticated CMS boundary under `/api/v1/admin`. Admins and super admins can manage taxonomy, courses, curriculum, lessons, examples, and publishing. Instructors are restricted to courses they own or are assigned through `course_instructors`. Course revisions, publishing reviews, and admin audit records preserve workflow history. Public course queries continue to filter on `published`.

Phase 4 keeps code execution outside the API process. The API persists execution jobs and uses a Redis queue adapter; a separately deployed hardened worker is responsible for execution when enabled. The browser uses Monaco through a client component and receives bounded job results. No student source is executed during local development.

Phase 5 adds a challenge boundary on top of those execution jobs. Published challenge queries expose only public tests; authenticated submission and history endpoints enforce ownership. Skill and achievement records are server-derived, while the current runner-unavailable state prevents false grading.

Phase 6 adds career roadmaps and student goal preferences. Roadmap steps link to existing courses and challenges by resource type/id. Progress is derived from existing lesson and accepted-submission evidence, while recommendations rank published roadmap records using deterministic goal matching.

Phase 7 adds project templates and a review boundary. GitHub URLs are validated and stored as metadata; repositories are never fetched or executed by FastAPI. Approved reviews create verified project skill evidence and can satisfy roadmap project resources. Portfolio visibility is explicit and defaults to private.

Phase 8 adds an AI boundary under `/api/v1/ai`. Conversations, messages, usage, preferences, quotas, and audit records are persisted with user ownership checks. Context retrieval is allowlisted to published lesson and challenge records and is passed as untrusted reference material to a provider adapter. The default provider is disabled, so the application reports an unavailable state instead of fabricating answers. Streaming uses Server-Sent Events; the browser never receives provider credentials.

Phase 10 adds a community boundary under `/api/v1/community`. Public posts are filtered by published/public status; authenticated mutations require the existing session and CSRF checks. Group membership, post ownership, answer acceptance, votes, bookmarks, reports, blocks, and notification recipients are checked server-side. User-generated content is stored as text and shared snippets are never executed in FastAPI.

Phase 11 adds live class records and room authorization. Session times are normalized to UTC, registrations are unique per student/session, and room access requires a registration or authorized staff role. The video provider is abstracted behind configuration and returns an unavailable state when disabled; FastAPI does not expose provider secrets or execute media logic.

Phase 19 adds the developer ecosystem boundary under `/api/v1/developers`, `/api/v1/github`, and `/api/v1/open-source`. Public records are filtered to approved/public data. GitHub webhook delivery IDs are deduplicated in PostgreSQL and signatures are checked server-side. OAuth and repository synchronization remain disabled until provider configuration and a server-side PKCE/token encryption implementation are deployed.
