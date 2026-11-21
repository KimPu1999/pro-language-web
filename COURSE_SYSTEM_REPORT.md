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

Migration `0045_course_detail_content` was added and applied to the local PostgreSQL database at the recorded head `0044_learn_coding_branding`. It adds defaulted target-audience, technology, and SEO fields to courses plus a `course_faqs` table. Existing rows remain valid and the existing backup was retained.

The public course detail response now includes real published curriculum only, course-level metadata, assigned active instructors when present, same-category published course recommendations, and published FAQs. The admin API supports protected FAQ create, edit, list, and delete operations with audit records. Draft and archived FAQs remain private.

## Public Platform

Implemented independent routes in `apps/platform`:

- `/courses` — search, category, difficulty, technology, sorting, pagination, loading, empty, and error states.
- `/courses/[slug]` — breadcrumb/SEO metadata, thumbnail fallback, overview, outcomes, prerequisites, target audience, technologies, curriculum accordion, lesson completion indicators, enrollment, progress, continue/review state, instructors, FAQs, and related published courses.
- `/courses/[slug]/learn/[lessonSlug]` — lesson content, code examples, course navigation, previous/next lesson, and authenticated progress persistence.

Published data is loaded from FastAPI. Draft or unpublished courses and lessons are not returned by public APIs.

## Admin Panel

Implemented independent routes in `apps/admin`:

- `/courses` — protected course table, search, status filters, and create/edit links.
- `/courses/new` — validated course creation form.
- `/courses/[id]` — course editing, draft save, module creation, lesson draft creation, publish, and unpublish.
- `/courses/[id]` — also manages target audience, technologies, SEO title/description, and course FAQs.

All mutations use the existing secure session, CSRF, and server-side role checks.

## Verification

- Course/auth/progress regression tests: **16 passed**.
- Full backend regression suite: **146 passed**, 2 warnings.
- Platform and admin TypeScript checks: passed.
- Backend Python compilation: passed.
- Clean public catalog/detail/lesson routes: HTTP 200.
- Clean admin course and new-course routes: HTTP 200.
- Live FastAPI health check: HTTP 200.
- Live published-course API: HTTP 200 with real records, curriculum counts, related-course data, and the new detail fields.

The local Next.js development cache was rebuilt after reproducing and fixing the prior `Cannot find module './130.js'` generated-chunk error. That error was caused by running a production build while the dev server was active; it was not caused by the course route source.

## Remaining limitations

- Thumbnail editing currently accepts an internal asset path; a dedicated course-media upload control is not yet present.
- The split Admin lesson editor currently creates lesson drafts and lists curriculum; full rich lesson/code/quiz editing remains available through the existing protected backend/legacy editor APIs and should be surfaced in a follow-up UI slice.
- Course-to-project relationships are not represented by an existing database foreign key, so related content is limited to real same-category published courses; no fabricated related-project links were added.
- Instructor assignment management is still exposed by the existing domain table but does not yet have a dedicated split-admin assignment control.
- No deployment was performed.
