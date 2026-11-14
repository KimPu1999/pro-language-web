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

## Phase 30 database release control

The migration chain currently has one head, `0031_ai_companion`. Production upgrades require an encrypted backup, isolated restore rehearsal, migration application, smoke tests, and rollback evidence before approval.

Migration `0032_operations_feedback` adds alert rules/events, incident actions, feedback responses, bug reports and attachment metadata, improvement events, release approvals, feature flags/rules, backup checks, restore drills, operational reviews, and operations audit logs. It is additive and does not delete existing data.
Migration `0013_operations` adds post-launch incidents, incident events, student feedback, engineering issues, release records, service health history, maintenance windows, and improvement items. It is additive and preserves all existing learning data.
# Phase 16 additions

Migration `0014_learning_intelligence` adds skill prerequisites and snapshots, recommendation feedback, study plans/items, revision items/attempts, private risk indicators, and minimal AI coach interaction records. Existing `skill_definitions`, `student_skill_evidence`, `student_learning_goals`, and `learning_recommendations` are reused.

Migration `0015_career_development` adds career, mentor, resume, portfolio review, interview, application, and career audit tables. Existing roadmaps, skills, portfolios, projects, users, and sessions remain intact.

Migration `0017_developer_ecosystem` adds GitHub connection/installations/sync records, approved public source projects and opportunities, contribution records and verification history, code review requests/feedback, collaboration requests, opt-in developer profiles, webhook delivery deduplication, contribution metrics, and ecosystem audit logs. It is additive and preserves existing student data. Apply with `PYTHONPATH=. python3 -m alembic upgrade head` from `backend`.

Migration `0018_organizations` adds organizations, memberships, invitations, organization teams, settings, private course mappings, training programs/items/assignments, assessments/attempts, organization skill snapshots, report exports, audit/security events, resource usage and support access. All are additive and use foreign keys, indexes and tenant-scoped unique constraints.

Migration `0019_enterprise_security` adds organization identity provider/domain/session records, MFA/recovery/passkey records, SCIM tokens/mappings, security policies/sessions/audit events, access reviews, compliance controls/evidence, retention policies, privacy requests, and alert rules/events. Sensitive credential fields are never returned by public schemas.
## Phase 23 content studio

Migration `0021_content_studio` is additive. It stores tenant-scoped content projects, generation jobs and outputs, lesson/quiz/challenge/project drafts, translations, quality checks, review requests and decisions, immutable revision snapshots, publication records, usage records, and audit logs. Existing courses, lessons, challenges, and project records are preserved and are not overwritten by generation requests.

Migration `0022_learning_labs` adds lab definitions and versions, steps, files, test cases, student workspaces, snapshots, runs, submissions, progress, SQL/API boundary records, reviews, and audit logs. Existing course, challenge, and runner data is preserved.
## Phase 25 tables

Migration `0023_collaboration` adds collaboration rooms, members, invitations, sessions, documents, updates, snapshots, presence, chat, pair sessions, execution jobs, debugging notes, AI interactions, recording consent/metadata, feedback and audit logs. Existing team and lab tables are preserved.

## Phase 26 cloud labs

Migration `0028_cloud_lab_indexes` extends the existing Phase 24 learning-lab
tables with ownership/status, snapshot, run, and audit indexes. Cloud lab
routes intentionally reuse `learning_labs`, `learning_lab_workspaces`,
`learning_lab_workspace_files`, `learning_lab_snapshots`,
`learning_lab_runs`, and `learning_lab_audit_logs`; no duplicate cloud
workspace tables are created.

## Phase 27 cybersecurity

Migration `0029_cybersecurity_training` adds published lab definitions, ownership-scoped attempts, vulnerability/remediation records, threat-model versions, AI interaction metadata, security events, and cybersecurity audit logs. It is additive and preserves existing learning, challenge, certificate, and runner records. Run `PYTHONPATH=. python3 -m alembic upgrade head` from `backend` in an environment with PostgreSQL configured.

## Phase 28 mobile/offline

Migration `0030_mobile_offline` adds mobile devices, push subscriptions/preferences, offline content versions/manifests/policies, sync events/conflicts, learning activity, bookmarks, preferences, delivery events, and platform audit records. It is additive and preserves existing course and progress data.

## Phase 29 AI companion

Migration `0031_ai_companion` adds companion profiles/conversations/messages, study sessions and activities, evidence-labelled recommendations, versioned revision items/reviews, goals, plans, insights, voice session metadata, feedback, usage, security events, and audit logs. Existing AI tutor, learning intelligence, revision, and study-plan tables remain intact.

## Phase 32 scalability

Migration `0033_scalability` adds additive capacity snapshots, scaling policies
and events, service-instance records, database/queue/runner/CDN/AI metrics,
cost records, budget policies, recovery drills, failover events, and
scalability audit logs. It does not alter existing learning data or provision
infrastructure.
