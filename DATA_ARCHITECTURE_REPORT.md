# Learn-Coding Data Architecture Audit

Audit date: 2026-11-21  
Database: PostgreSQL `codemaster`, `public` schema  
Change policy: read-only inventory plus application/API connection repairs; no
content rows or student records were changed in this audit.

## Findings

The existing schema already groups data by logical domain without separate
PostgreSQL schemas. This is the correct preservation strategy for the current
application. The database contains 487 tables and 653 foreign-key constraints.
The read-only orphan audit found **0 foreign-key orphan violations**.

| Domain | Existing source of truth | Current rows | Admin/public connection |
| --- | --- | ---: | --- |
| Platform settings/branding/navigation/pages | `platform_settings` JSON records | 0 | `/api/v1/site/*`, protected Admin settings; defaults are used while empty |
| Users/profiles | `users`, `user_profiles` | 2 / 1 | Protected `/api/v1/admin/users`; student ownership remains user-ID based |
| Courses | `courses`, `course_modules`, `lessons`, `lesson_quizzes` | 54 / 670 / 1,249 / 1,249 | Public published course API and protected Admin curriculum APIs |
| Enrollments/progress | `enrollments`, `lesson_progress` | 0 / 0 | Existing student APIs; no records to migrate |
| Projects | `project_templates`, `project_milestones`, submissions/reviews | 13 / 52 / 0 / 0 | Public project detail and protected Admin project APIs |
| Challenges | `challenges`, `challenge_test_cases`, submissions/results | 10 / 20 / 0 / 0 | Public challenge detail exposes public tests only; Admin list/create/publish APIs |
| Careers | `career_roadmaps`, `roadmap_stages`, `roadmap_steps` | 8 / 8 / 8 | Public roadmap detail and protected Admin roadmap inventory/create APIs |
| Interviews | `interview_question_bank` | 0 | Existing student/admin create APIs; no records to connect |
| Jobs/applications | `career_job_postings`, `job_applications` | 0 / 0 | Existing career APIs; no records to migrate |
| Achievements | `achievement_definitions`, `student_achievements` | 0 / 0 | Existing student achievement API; no records to migrate |
| Audit | `admin_audit_logs` | 3 | Admin bootstrap/login activity is recorded |

## Relationship verification

The following important chains are backed by real foreign keys and were checked
without modifying rows:

```text
Course → CourseModule → Lesson → LessonQuiz / CodeExample
ProjectTemplate → ProjectMilestone → StudentProject → ProjectSubmission → ProjectReview → ProjectReviewScore
Challenge → ChallengeTestCase → ChallengeSubmission → ChallengeTestResult
CareerRoadmap → RoadmapStage → RoadmapStep → RoadmapStepResource
User → Enrollment / LessonProgress / StudentProject / ChallengeSubmission / achievements
```

No orphaned child rows were found across the full FK audit. Project tutorials
and starter/source examples are represented by `project_milestones` fields
(`content_en`, `code`, `expected_output`) rather than a separate tutorial table.
Challenge reference/hidden test data is protected by the public API: the public
detail endpoint returns only `is_hidden=false` tests.

## Missing or not database-backed domains

No current source-of-truth tables were found for developer-tool definitions,
contact messages, legal document revisions, SEO records, homepage sections, or
a general media library. Existing support/bug attachment tables are scoped to
their parent workflows and must not be treated as a general media library.
No replacement records were created for these absent domains. They require a
separate additive schema/API design and migration if the product needs them.

## Repairs made

- Added protected `GET /api/v1/admin/users` inventory endpoint.
- Added protected `GET /api/v1/admin/roadmaps` inventory endpoint, including
  draft and archived roadmaps for Admin rather than exposing them publicly.
- Connected the split Admin UI to existing course, project, challenge, career,
  user, instructor, submission, and platform-page APIs.
- Connected the split Public UI to published project, challenge, and career
  APIs and added detail pages that preserve public/private boundaries.
- Added regression coverage for the Admin inventory endpoints.

These changes do not copy, merge, delete, or recreate existing content.

