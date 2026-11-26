# Admin and Platform Architecture Audit

Audit date: 2026-11-26

This report records the repository and database evidence inspected before the consolidation changes. Counts below are source and database counts, not inferred completion percentages.

## 1. Runtime inventory

| Area | Actual implementation | Inventory |
| --- | --- | ---: |
| Canonical frontend | Next.js 15, React 19, TypeScript, Tailwind | `frontend/` |
| Backend | FastAPI 0.115.6, SQLAlchemy 2.0, Alembic | `backend/` |
| Database | PostgreSQL through `DATABASE_URL` | 511 tables; Alembic head `0057_personal_notebook` |
| Canonical Admin routes | `frontend/app/admin` | 19 page files |
| Canonical Platform routes | `frontend/app/platform` | 70 page files |
| Student Dashboard routes | `frontend/app/dashboard` | 41 page files |
| Legacy Admin app | `apps/admin` | 31 page files; port 3001 |
| Legacy Platform app | `apps/platform` | 23 page files; port 3000 |

The canonical frontend and the two `apps/*` trees are separate Next applications. The README and package manifests confirm that the legacy applications are intended to use the same FastAPI/PostgreSQL backend. They are therefore architectural duplication and must be decommissioned only after runtime and external-link verification; this audit does not delete them.

The main backend route scan found 152 handlers whose paths contain `/admin` or `/platform`. The count includes feature-specific handlers and repeated endpoint families, so it is an inventory signal rather than a claim that every handler is a unique feature.

## 2. Database evidence

The read-only inventory found:

| Record type | Count |
| --- | ---: |
| Users | 2 |
| Courses | 56 |
| Course modules | 671 |
| Lessons | 1,250 |
| Enrollments | 10 |
| Challenges | 12 |
| Content review items | 0 |
| Media assets | 11 |
| Legal documents | 1 |
| Organizations | 0 |
| AI content projects | 0 |
| Personal notes | 0 |
| Project templates | 17 |

No database reset, destructive migration, record deletion, or content rewrite was performed.

## 3. Feature classification

| Feature | Existing route(s) | Status found | Action | Risk |
| --- | --- | --- | --- | --- |
| Student Dashboard | `/dashboard/*` | Separate working workspace | **KEEP** | Low |
| Canonical Admin workspace | `/admin/*` | Working but had duplicated navigation targets | **IMPROVE** | Medium |
| Canonical Platform workspace | `/platform/*` | Working pages with a second shell | **MERGE** into the shared management shell | Medium |
| Legacy Admin application | `apps/admin` | Separate app with overlapping management features | **KEEP temporarily; DEPRECATE after migration verification** | High |
| Legacy Platform application | `apps/platform` | Separate app with overlapping platform features | **KEEP temporarily; DEPRECATE after migration verification** | High |
| Admin Users | Backend `/api/v1/admin/users`; old sidebar target was settings | API existed, UI target was wrong | **REPAIR** | Medium |
| Audit Logs | Backend `/api/v1/admin/audit-logs`; old sidebar target was security | API existed, UI target was wrong | **REPAIR** | Medium |
| Module Management / Lesson Management | Both pointed to `/platform/content-studio` | Duplicate navigation entries | **MERGE** into course builder/content operations | Medium |
| Content Review | `/platform/content-review` | Real queue and workflow API; no organization records exist | **KEEP/IMPROVE** | Medium |
| Curriculum Quality | `/admin/curriculum-quality` | Real audit API and evidence-based gaps | **KEEP** | Medium |
| Media Library | `/platform/media` and admin media API | Central database-backed media path exists | **KEEP** as the single library | Medium |
| Translations | `/admin/translations` | Existing centralized translation API/UI | **KEEP/IMPROVE** | Medium |
| Branding / settings | `/admin/settings`, `/platform/settings` | Two settings surfaces with different purposes | **KEEP**, clarify ownership | Medium |
| Student/instructor management | `/platform/students`, `/platform/instructors` | Platform routes and RBAC-backed APIs exist | **KEEP** | Medium |
| Public/legal/contact CMS | Backend models/routes exist; canonical admin editors are incomplete | **IMPROVE** | High |
| Feature-specific platform pages | `/platform/*` | Many specialized routes and APIs | **KEEP until individual usage is verified** | Medium |

## 4. Problems repaired in this batch

### Shared management shell

`frontend/components/management-shell.tsx` is now the protected shell for both `/admin/*` and `/platform/*`. It provides one sticky header, one responsive sidebar, one TKP logo treatment, active route styling, mobile drawer behavior, collapse persistence, language switching, and role-filtered navigation.

`frontend/components/platform-shell.tsx` remains as a compatibility wrapper so existing platform routes keep their URLs while using the shared shell. The student dashboard shell remains separate.

### Misrouted governance navigation

The former admin sidebar labeled “Admin Users” but linked to `/platform/settings`, and labeled “Audit Logs” but linked to `/platform/security`. These were replaced with:

- `/admin/users`, backed by `/api/v1/admin/users`
- `/admin/audit-logs`, backed by `/api/v1/admin/audit-logs`

Both pages use server-side search, pagination, loading/error/empty states, and live database responses. They do not expose student notes or other private learning content.

### Duplicate Admin Overview route

`/admin/dashboard` is now the canonical overview implementation. `/admin` preserves compatibility by redirecting to `/admin/dashboard`; the old duplicate implementation was moved into the canonical dashboard route.

### Permission consistency

The platform Content Studio endpoint previously allowed only `admin` and `super_admin`, while the shared RBAC definition also recognizes `platform_admin`. It now uses the existing `require_platform_admin` dependency. Existing authentication, CSRF, verified-email, and server-side role checks remain active.

### Content Review scope

The current Content Review UI and API are platform-scoped. The UI no longer depends on selecting an organization, and the backend explicitly rejects organization-scoped submissions for platform review items. Organization isolation remains enforced by the organization-specific content APIs; no authorization bypass was added.

## 5. Navigation and API audit findings

- Existing course, module, lesson, quiz, project, curriculum-quality, media, translation, review, settings, student, instructor, and analytics APIs were located in the backend route modules.
- Admin users and audit log APIs were already implemented and protected by `full_admin`; the missing piece was a correctly routed canonical UI.
- Content Review uses real dashboard, reviewer, author, queue, detail, assignment, transition, publish, comment, and history endpoints.
- The canonical shell now filters navigation by the same role families used by the frontend (`platform_admin`/`admin`/`super_admin` and content roles). API authorization remains authoritative.
- The API client keeps its existing 8-second timeout and explicit FastAPI reachability error. A stale frontend process was restarted during verification; FastAPI health returned 200 and the management route returned 200.

## 6. Security review

Existing controls confirmed during inspection:

- Server-side session cookie authentication.
- CSRF protection for state-changing admin actions.
- Verified-email requirement for admin access.
- `full_admin`, `require_platform_admin`, and content-role checks in backend routes.
- Versioned Content Review workflow and explicit publish action.
- Database-backed audit logging.

The main issue repaired in this batch was role-definition drift in Content Studio. The legacy application trees remain a security and maintenance risk until they are either migrated to the canonical shell or formally retired; they were not removed because their runtime and external consumers have not yet been fully verified.

## 7. Files changed

- `frontend/components/management-shell.tsx`
- `frontend/components/platform-shell.tsx`
- `frontend/app/admin/layout.tsx`
- `frontend/app/admin/page.tsx`
- `frontend/app/admin/dashboard/page.tsx`
- `frontend/app/admin/users/page.tsx`
- `frontend/app/admin/audit-logs/page.tsx`
- `frontend/lib/api.ts`
- `backend/app/content_studio_routes.py`
- `docs/admin-platform-audit.md`

## 8. Verification performed

- Frontend TypeScript typecheck: passed.
- Frontend production build: passed; Next generated 461 static pages.
- ESLint on changed frontend shell and governance pages: passed.
- `git diff --check`: passed.
- Focused backend authorization/content tests: **6 passed**.
- Full backend suite: **183 passed**.
- FastAPI health endpoint: HTTP 200.
- Canonical management route smoke check: HTTP 200 after restarting the stale Next process.

The backend test run emitted two existing environment warnings: a Starlette `BlockingPortal` deprecation warning and an unrecognized `asyncio_default_fixture_loop_scope` pytest option. They did not fail the tests.

## 9. Remaining work

1. Verify all links and deployment consumers of `apps/admin` and `apps/platform`, then migrate or retire those duplicate app trees with redirects where required.
2. Add/repair canonical editors for public pages, legal pages, contact messages, and any other backend-backed features currently reachable only through legacy UI.
3. Run a route-by-route authenticated smoke test across the 70 platform pages and 19 admin pages; the current environment has only two users, zero organizations, and zero review records, so some workflows cannot be exercised with live records.
4. Reconcile the remaining specialized platform routes into documented product areas without deleting data or database tables.
5. Run the full backend suite and production frontend build after the remaining migration decisions are complete.
