# Challenge system

The public challenge catalog is served by the existing `challenges` schema and
the FastAPI router at `/api/v1/challenges`. Published records are the only
records exposed to unauthenticated catalog requests. Hidden test cases are
never included in public challenge detail responses.

## Public API

- `GET /api/v1/challenges` supports `search`, `category`, `topic`, `language`,
  `difficulty`, `page`, and `page_size`.
- `GET /api/v1/challenges/{slug}` returns the published problem, examples,
  hints, enabled languages, and public tests.
- `GET /api/v1/challenge-categories` returns active challenge categories.
- `GET /api/v1/challenges/progress/me` returns authenticated user progress.
- `POST /api/v1/challenges/{id}/run` and `/submit` require a verified user and
  CSRF protection. They enqueue work for the configured secure runner.

## Content rules

The catalog seed is idempotent. It creates only missing categories, topics,
and complete starter challenges. Existing challenge content, submissions, and
progress are preserved. A challenge is published only when it has English
content, at least one enabled language, a public example/test, and a hidden
test. The seed does not create fake solved counts or progress records.

If the runner is unavailable, submissions are recorded as
`runner_unavailable`; the application does not execute code in the FastAPI
process.
