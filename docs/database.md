# Database

The schema uses UUID identifiers, timestamp columns, unique slugs, ordered modules and lessons, optional Myanmar content, and published flags. `users.password_hash` is reserved for a future authentication implementation and is never returned by public schemas.

Migration `0002_auth_student` adds normalized email, account status, role, verification/login/password timestamps, `user_profiles`, `auth_sessions`, single-use verification/reset token tables, security audit logs, and lesson visit timestamps. Tokens are stored as SHA-256 hashes. Existing users are preserved and normalized emails are backfilled.

Run `alembic upgrade head` followed by `python -m app.seed`. The seed is idempotent by slug and creates representative published courses for Python, JavaScript, TypeScript, Java, C++, PHP, HTML, CSS, and SQL.
