# Learn-Coding Repository Audit

Audit date: 2026-11-21  
Repository: `/Users/kimpu/Desktop/Pro-Language-Web`  
Deployment: not performed

## Executive result

The local FastAPI service and PostgreSQL database are healthy. Existing course,
lesson, project, and challenge data is present and the public API serves the
published records. The original Next.js application still contains the complete
working surface. The new `apps/platform` and `apps/admin` applications build
independently and use the shared API, but they are currently thin migration
shells rather than a complete replacement for all existing routes and admin
workflows.

Administrator sign-in initially failed because the database contained no admin
account. A secure operator CLI was added and has now provisioned one verified
super administrator without placing a password in an HTTP request or log.

## Architecture inventory

| Area | Current state |
| --- | --- |
| Existing frontend | `frontend/`, Next.js App Router, 530 page routes, existing public/student/admin/platform surfaces |
| Public split app | `apps/platform`, Next.js App Router, independent layout, navigation, error boundary, login, branding asset, 7 page files |
| Admin split app | `apps/admin`, Next.js App Router, independent layout, secure-session check, error boundary, login, dashboard shell, 6 page files |
| Backend | `backend/app`, FastAPI, SQLAlchemy, existing domain route modules, 662 route decorators found |
| Database | PostgreSQL database `codemaster`, public schema, 487 tables, Alembic head `0044_learn_coding_branding` |
| Branding | Existing TKP image preserved at `apps/platform/public/branding/tkp.png` and `apps/admin/public/branding/tkp.png`; backend defaults to Learn-Coding |
| Upload storage | No configured S3/object-storage or complete media-upload service was found. Branding paths are validated as internal paths; a full media library still needs implementation. |
| Deployment | Backend Dockerfile exists. No repository Docker Compose or production provider manifest was found. No deployment was triggered. |

## Existing functionality that can be reused

- The monolithic frontend remains the source of truth for the many existing
  learning, student, community, career, tool, and platform routes.
- Existing FastAPI domain modules, SQLAlchemy models, authentication/session
  code, RBAC helpers, CSRF checks, rate limiting, and Alembic migrations remain
  reusable.
- Existing PostgreSQL records were not copied into a second database.
- The existing TKP logo was reused unchanged.

## Authentication and authorization findings

- Admin login checks the password, active account status, verified email, and an
  allowed administrative role before creating the secure session.
- Admin logout requires the CSRF token and revokes the session.
- Admin APIs use server-side role dependencies; hiding a menu is not the
  authorization boundary.
- Unauthenticated `GET /api/v1/admin/auth/me` returns `401 Authentication
  required`.
- Current student account: `kimpiang1999@gmail.com`, role `student`, account
  status `active`, email verified `false`.
- Current admin account: `admin@learn-coding.local`, role `super_admin`, account
  status `active`, email verified `true`.

## Findings and severity

| Severity | Finding | State |
| --- | --- | --- |
| High | No verified admin principal existed | Repaired operationally with a secure bootstrap CLI |
| High | Split apps do not yet contain all 530 legacy routes | Open migration work; legacy frontend remains available and builds |
| High | New admin UI is a shell for only a subset of CRUD workflows | Open; backend admin APIs are broader than the new UI |
| Medium | New public app initially hardcoded branding | Repaired; platform navigation and home now read the public branding/navigation API |
| Medium | No complete media upload/storage implementation found | Open; do not claim Media Library completion |
| Medium | Existing authored records include `content_mm`/Myanmar content fields | Preserved for data safety; the shared UI test and new split UI are English-only |
| Low | Multiple lockfiles trigger a Next.js workspace-root warning | Non-blocking; should be cleaned up before deployment |
| Low | Stale `.next` chunks caused `Cannot find module './130.js'` | Repaired by clearing generated cache and rebuilding |

## Safe migration plan

1. Keep `frontend/` as the currently complete application while the split apps
   are migrated route-by-route.
2. Move shared API clients, types, and visual primitives into a package only
   after their ownership and tests are clear.
3. Port one public domain at a time and verify published/draft behavior against
   the same backend records.
4. Port admin CRUD screens against existing protected endpoints, adding
   permission-specific UI only after backend authorization tests pass.
5. Add a real media backend and restore test before enabling destructive media
   actions.
6. Run staging browser, accessibility, backup-restore, and security tests
   before retiring the legacy frontend.

