# Production architecture

Use separate services: Vercel or equivalent for Next.js, a private container service for FastAPI, managed PostgreSQL, managed Redis, dedicated background workers, private object storage, a reviewed AI provider, a supported video provider, and transactional email.

The browser may access the frontend and public API routes. FastAPI accesses PostgreSQL, Redis, providers, and private storage through restricted credentials. Workers consume namespaced Redis queues. The code runner is a separate untrusted-compute boundary with no access to application secrets, database, Redis, or private storage.

Run Alembic as a release job after a backup and before compatible application rollout. Do not run migrations from every worker startup.
