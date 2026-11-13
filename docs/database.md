# Database

The schema uses UUID identifiers, timestamp columns, unique slugs, ordered modules and lessons, optional Myanmar content, and published flags. `users.password_hash` is reserved for a future authentication implementation and is never returned by public schemas.

Migration `0002_auth_student` adds normalized email, account status, role, verification/login/password timestamps, `user_profiles`, `auth_sessions`, single-use verification/reset token tables, security audit logs, and lesson visit timestamps. Tokens are stored as SHA-256 hashes. Existing users are preserved and normalized emails are backfilled.

Migration `0003_course_cms` extends languages, categories, courses, lessons, and code examples with CMS metadata and adds `course_instructors`, `course_revisions`, `publishing_reviews`, and `admin_audit_logs`. Existing `published` values are backfilled into the workflow status. No enrollment or progress rows are removed.

Run `alembic upgrade head` followed by `python -m app.seed`. The seed is idempotent by slug and creates representative published courses for Python, JavaScript, TypeScript, Java, C++, PHP, HTML, CSS, and SQL.

Migration `0004_interactive_classroom` adds coding exercises, starter code, test cases, execution jobs/results, submissions, submission test results, and per-user editor preferences. Foreign keys and user ownership indexes support isolation. Hidden exercise tests are never returned by public runner endpoints.

Migration `0005_challenges_assessments` adds challenge taxonomy, language configs, public/hidden challenge tests, hints, challenge submissions/results, UTC daily assignments, student progress, skill statistics, and unique achievement awards. Existing Phase 4 execution jobs remain the execution source of truth.

Migration `0006_personalized_roadmaps` adds career roadmaps, ordered stages and steps, resource links, prerequisite edges, student roadmap enrollments/progress, learning goals, skill assessments/evidence, recommendations, and revision snapshots. Existing course, lesson, challenge, enrollment, and progress rows are preserved.

Migration `0007_projects_portfolio` adds project templates/categories/skills, milestones, student project records, submissions, review/rubric/feedback records, portfolios, portfolio links, verified project skills, and audit logs. Existing student data is preserved; approved evidence is unique by student, skill, and project.

Migration `0008_ai_tutor` adds conversations, messages, message context references, usage records, provider/model policy records, tutor preferences, feedback, request logs, and UTC quota counters. Conversation and usage rows are user-scoped. Provider credentials are not stored in these tables; deployment secrets remain environment-managed. Deleted conversations are soft-deleted so operational retention can be managed without exposing them to list/detail queries.

Migration `0010_community` adds community categories/posts/tags, answers, bounded-depth comments, unique votes and bookmarks, snippets, study groups and memberships, reports, user blocks, and user-scoped notifications. Existing users and learning records are preserved.

Migration `0011_live_classes` adds classes, sessions, instructors, registrations, waitlists, attendance, idempotent presence events, private recording metadata, resources, Q&A, chat messages, code snapshots, and audit logs. Timestamps are timezone-aware and schedules are stored in UTC.
Migration `0013_operations` adds post-launch incidents, incident events, student feedback, engineering issues, release records, service health history, maintenance windows, and improvement items. It is additive and preserves all existing learning data.
