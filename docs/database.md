# Database

The schema uses UUID identifiers, timestamp columns, unique slugs, ordered modules and lessons, optional Myanmar content, and published flags. `users.password_hash` is reserved for a future authentication implementation and is never returned by public schemas.

Run `alembic upgrade head` followed by `python -m app.seed`. The seed is idempotent by slug and creates representative published courses for Python, JavaScript, TypeScript, Java, C++, PHP, HTML, CSS, and SQL.
