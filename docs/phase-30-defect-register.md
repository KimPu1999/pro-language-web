# Phase 30 defect register

| ID | Priority | Finding | Resolution/evidence | Status |
|---|---|---|---|---|
| QA-001 | P1 | CI Ruff job failed on legacy unused imports and one undefined `OrganizationSupportAccess` symbol. | Removed confirmed unused imports, imported the model, removed unused locals, and constrained the gate to E9/F correctness rules. `ruff check app tests` passes. | RESOLVED |
| QA-002 | P1 | `/platform/quality-center` did not exist. | Added a route alias reusing the existing quality page and existing server-protected quality API. | RESOLVED |
| QA-003 | P1 | Platform quality status must not infer external CI, backup, isolation, or provider health. | Existing quality response reports configuration/dependency observations and explicit `not_configured`/`partial` states. | RESOLVED |
| QA-004 | P0/P1 | Live production isolation, restore, and migration evidence unavailable. | No safe local fix can substitute for staging evidence. Launch blocker documented. | OPEN BLOCKER |
| QA-005 | P1 | Playwright browser binary unavailable locally. | CI installs Chromium; local E2E remains unverified. | OPEN BLOCKER |

No destructive migration, deployment, data reset, or secret change was performed.
