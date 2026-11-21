# Learn-Coding Course System Recovery

## Scope

The Courses system was repaired against the existing PostgreSQL-backed FastAPI domain. Existing course, module, lesson, enrollment, progress, quiz, and user records were preserved. No reset, truncate, delete, or seed operation was run during this phase.

## Database findings

Current inventory from the shared `codemaster` database:

- Courses: 54 total; 52 published and 2 archived.
- Course modules: 670.
- Lessons: 1,249.
- Lesson quizzes: 1,249.
- Enrollments: 0.
- Lesson progress: 0.
- Quiz attempts: 0.

The existing relationship chain is intact:

`courses → course_modules → lessons → lesson_quizzes → quiz_attempts`

`users → enrollments → courses`

`users → lesson_progress → lessons`

The repository-wide foreign-key audit checked 653 constraints and found 0 orphan violations. Existing IDs and relationships were not rewritten.

## Backend/API work

The existing APIs were reused and verified:

- `GET /api/v1/courses`
- `GET /api/v1/courses/{slug}`
- `GET /api/v1/courses/{slug}/learning`
- `GET /api/v1/courses/{slug}/lessons/{lesson_slug}`
- `GET /api/v1/me/enrollments`
- `POST /api/v1/me/enrollments/{course_slug}`
- `GET /api/v1/me/courses/{course_slug}/progress`
- `POST /api/v1/me/lessons/{lesson_id}/progress`
- `POST /api/v1/me/lessons/{lesson_id}/visit`
- Protected admin course CRUD, curriculum, publishing, examples, quizzes, and stats APIs.

The public course list now returns short descriptions, thumbnails, module counts, and published lesson counts. The admin API now exposes course statistics and avoids assigning non-model fields during course updates.

## Public Platform

Implemented independent routes in `apps/platform`:

- `/courses` — search, category, difficulty, technology, sorting, pagination, loading, empty, and error states.
- `/courses/[slug]` — overview, outcomes, prerequisites, curriculum, enrollment, and continue-learning state.
- `/courses/[slug]/learn/[lessonSlug]` — lesson content, code examples, course navigation, previous/next lesson, and authenticated progress persistence.

Published data is loaded from FastAPI. Draft or unpublished courses and lessons are not returned by public APIs.

## Admin Panel

Implemented independent routes in `apps/admin`:

- `/courses` — protected course table, search, status filters, and create/edit links.
- `/courses/new` — validated course creation form.
- `/courses/[id]` — course editing, draft save, module creation, lesson draft creation, publish, and unpublish.

All mutations use the existing secure session, CSRF, and server-side role checks.

## Verification

- Course/auth/progress regression tests: **15 passed**.
- Platform and admin TypeScript checks: passed.
- Backend Python compilation: passed.
- Clean public catalog/detail/lesson routes: HTTP 200.
- Clean admin course and new-course routes: HTTP 200.
- Live FastAPI health check: HTTP 200.
- Live published-course API: HTTP 200 with real records and curriculum counts.

The local Next.js development cache was rebuilt after reproducing and fixing the prior `Cannot find module './130.js'` generated-chunk error. That error was caused by running a production build while the dev server was active; it was not caused by the course route source.

## Remaining limitations

- Thumbnail editing currently accepts an internal asset path; a dedicated course-media upload control is not yet present.
- The split Admin lesson editor currently creates lesson drafts and lists curriculum; full rich lesson/code/quiz editing remains available through the existing protected backend/legacy editor APIs and should be surfaced in a follow-up UI slice.
- Course-to-project relationships are not represented by an existing database foreign key, so no fabricated related-project links were added.
- No deployment was performed.
