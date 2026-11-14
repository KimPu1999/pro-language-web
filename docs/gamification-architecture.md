# Gamification Architecture

The API separates verified evidence from presentation. Existing challenge,
assessment, achievement, streak, and competition services remain authoritative.
The Phase 39 router adds quest assignment and completion orchestration, writes
an append-only XP ledger, and records audit events. Client requests cannot
award XP without server-side evidence.

All platform mutation endpoints require existing admin/RBAC dependencies and
CSRF protection. Public ranking uses the existing user opt-in preference.
