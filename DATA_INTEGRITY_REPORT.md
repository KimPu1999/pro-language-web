# Learn-Coding Data Integrity Report

Audit date: 2026-11-21  
Database: local PostgreSQL `codemaster` / schema `public`

## Recovery snapshot

- A non-destructive PostgreSQL custom-format backup was created before further
  audit work:
  `/private/tmp/learn-coding-codemaster-20261121.dump`
- Size: approximately 2.1 MB
- SHA-256:
  `e7d5891efdfe2e0dfcee347fe8257628e0359972abd014db81bc9d31cd4413a7`
- `pg_restore --list` reports 2,498 archive entries.
- The backup was not restored during this audit because restore would change
  database state and was not authorized.
- No table drops, truncations, database resets, destructive deletes, or data
  recreation were performed.

## Migration state

Alembic reports:

```text
0044_learn_coding_branding (head)
```

Migrations `0042`, `0043`, and `0044` are present in the local migration chain.
The Learn-Coding branding migration is additive/normalizing: it updates legacy
branding labels to Learn-Coding without deleting user or learning records.

## Current row counts

| Table | Rows |
| --- | ---: |
| users | 1 |
| courses | 54 |
| course_modules | 670 |
| lessons | 1,249 |
| project_templates | 13 |
| challenges | 10 |
| enrollments | 0 |
| lesson_progress | 0 |
| code_submissions | 0 |
| platform_settings | 0 |
| admin_audit_logs | 0 |

## Publication and account state

- Courses: 52 published, 2 archived; `published=true` for 52 and `false` for 2.
- Projects: 13 published.
- Challenges: 10 published.
- There are no enrollment, progress, or code-submission rows to migrate or
  repair in this snapshot.
- The only user is an active student and is not email-verified.
- No admin audit rows exist because no admin account or admin session existed.
- `platform_settings` is empty, so the API supplies the safe Learn-Coding/TKP
  defaults until an authorized admin saves settings.

## API consistency checks

The running API returned the same published totals:

- `GET /api/v1/courses?page_size=1`: HTTP 200, total 52
- `GET /api/v1/projects?page_size=1`: HTTP 200, total 13
- `GET /api/v1/challenges?page_size=1`: HTTP 200, total 10

Draft and non-published platform pages are rejected by the public page endpoint;
this was covered by the split-platform regression tests.

## Recovery conclusion

No evidence of data loss was found in the audited local database. This is a
current-state verification, not proof against an unknown historical database or
unavailable backup. Keep the verified dump outside source control and perform a
separate restore drill in an isolated database before production use.

