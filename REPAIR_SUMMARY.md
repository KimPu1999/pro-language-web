# Learn-Coding Repair Summary

## Implemented

- Added independent Next.js applications at `apps/platform` and `apps/admin`.
- Added independent layouts, navigation, error boundaries, branding assets, and
  development builds for both applications.
- Added shared FastAPI public endpoints for branding, navigation, and published
  platform pages.
- Added protected admin settings endpoints for branding, navigation, and pages.
- Added default Learn-Coding branding while preserving the existing TKP logo.
- Added additive Alembic migration `0044_learn_coding_branding`.
- Added admin role/session checks, CSRF-protected settings mutations, audit calls,
  and admin-facing error details.
- Added `backend/app/bootstrap_super_admin.py` for first-admin provisioning.
- Added `backend/app/reset_admin_password.py` for secure local administrator
  password recovery; it revokes existing sessions and records an audit row.
- Added split-platform regression tests covering branding, draft privacy,
  published pages, navigation persistence, and student denial.
- Updated the new public navigation/home to consume the shared published
  branding/navigation API.
- Cleared stale generated Next.js caches and rebuilt the legacy frontend; the
  missing `./130.js` runtime error no longer reproduces.
- Updated the stale frontend unit test to match the required English-only UI.

## First secure administrator login

Start the backend with the project virtual environment, not the system
micromamba `uvicorn`:

```bash
cd /Users/kimpu/Desktop/Pro-Language-Web/backend
./.venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Provision the first administrator locally. The command prompts for the password
without putting it in shell history:

```bash
cd /Users/kimpu/Desktop/Pro-Language-Web/backend
PYTHONPATH=. .venv/bin/python -m app.bootstrap_super_admin \
  --email your-admin@example.com \
  --name "Site Administrator"
```

Then start `apps/admin` on port 3001 and sign in at
`http://localhost:3001/login`. The command refuses to create a second admin if
one already exists. It requires an 8–12 character password and never prints it.

If the administrator password is forgotten, reset it locally:

```bash
PYTHONPATH=. .venv/bin/python -m app.reset_admin_password \
  --email admin@learn-coding.local
```

This command prompts for the new password, revokes existing sessions, and does
not print or store the password in command history.

## Files added or modified

- `apps/platform/**`
- `apps/admin/**`
- `backend/app/admin_routes.py`
- `backend/app/bootstrap_super_admin.py`
- `backend/app/main.py`
- `backend/app/mailer.py`
- `backend/app/schemas.py`
- `backend/migrations/versions/0044_learn_coding_branding.py`
- `backend/tests/test_split_platform.py`
- `frontend/app/layout.tsx`
- `frontend/tests/ui.test.tsx`
- `README.md`
- `AUDIT_REPORT.md`
- `DATA_INTEGRITY_REPORT.md`
- `TEST_REPORT.md`
- `REPAIR_SUMMARY.md`

## Remaining issues

The split applications are not yet a complete migration of the existing 530
route frontend. The admin shell does not yet provide full CRUD editors for all
requested content, media upload/organization, analytics charts, role management,
or every settings surface. These remain the next implementation phase. The
legacy frontend remains intact so existing routes and data are not lost while
that work is completed.

