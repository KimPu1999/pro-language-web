# Phase 1–29 implementation matrix

Status means code evidence exists in this repository; it does not mean production operation was verified.

| Phase | Evidence | Status | Test/evidence gap |
|---|---|---|---|
| 1–5 foundation, auth, courses, labs, challenges | `auth_routes.py`, course routes, `lab_routes.py`, `challenge_routes.py`, migrations `0001–0005` | IMPLEMENTED | Production email, runner and browser flows not fully staged |
| 6 roadmaps | `roadmap_routes.py`, `roadmaps/`, migration `0006` | IMPLEMENTED | Staging content verification |
| 7 projects | `project_routes.py`, project pages, migration `0007` | IMPLEMENTED | External URL/storage verification |
| 8 AI tutor | `ai_routes.py`, `ai_service.py`, `ai-tutor/`, migration `0008` | PARTIAL | Provider streaming and quota load test unavailable |
| 9 certificates/gamification | models, routes, migration `0009` | IMPLEMENTED | Restore/revocation drill not run |
| 10 community | `community_routes.py`, community pages, migration `0010` | IMPLEMENTED | Browser moderation smoke test unavailable |
| 11 live classes | `live_class_routes.py`, migration `0011` | PARTIAL | Video provider not configured |
| 12 analytics | `analytics_routes.py`, migration `0012` | IMPLEMENTED | Production query plans not measured |
| 13 operations | `operations_routes.py`, migration `0013` | IMPLEMENTED | Alert delivery/staging operations not verified |
| 14 learning intelligence | `learning_intelligence_routes.py`, migration `0014` | IMPLEMENTED | Recommendation quality requires real dataset |
| 15 career | `career_routes.py`, migration `0015` | IMPLEMENTED | External integration verification |
| 16 collaboration | collaboration routes/pages, migration `0016` | PARTIAL | Multi-client WebSocket and CRDT test unavailable |
| 17 developer ecosystem | `ecosystem_routes.py`, migration `0017` | IMPLEMENTED | External GitHub/provider verification |
| 18 organizations | `organization_routes.py`, migration `0018` | IMPLEMENTED | Cross-tenant staging matrix incomplete |
| 19 enterprise security | `security_routes.py`, migration `0019` | PARTIAL | SSO/SCIM/WebAuthn providers disabled locally |
| 20 automation | `automation_routes.py`, migration `0020` | PARTIAL | Worker/Redis execution not staged |
| 21 content studio | `content_studio_routes.py`, migration `0021` | IMPLEMENTED | Instructor browser review unavailable |
| 22 learning labs | `lab_routes.py`, migration `0022` | PARTIAL | Runner isolation requires approved executor |
| 23 collaboration enhancements | collaboration/realtime routes, migration `0023` | PARTIAL | Multi-client and recording-consent evidence missing |
| 24 lesson bookmarks | migration `0024`, lesson reader | IMPLEMENTED | Offline browser test unavailable |
| 25 learning path bookmarks | migration `0025`, learning-path pages | IMPLEMENTED | Browser smoke unavailable |
| 26 project learning | migration `0026`, project learning routes | IMPLEMENTED | Staging content verification |
| 27 community indexes | migration `0027` | IMPLEMENTED | Live query-plan evidence missing |
| 26 cloud labs | `cloud_lab_routes.py`, cloud pages, migrations `0028` | PARTIAL | Provisioning/isolation not verified in staging |
| 27 cybersecurity | `cybersecurity_routes.py`, cybersecurity pages, migration `0029` | PARTIAL | Lab isolation and approved-target tests not staged |
| 28 mobile/offline | `mobile_routes.py`, service worker, IndexedDB, migration `0030` | PARTIAL | Actual network-disconnect and push tests unavailable |
| 29 AI companion | `ai_companion_routes.py`, companion pages, migration `0031` | PARTIAL | Provider and voice unavailable locally |

## Interpretation

The repository contains implementation evidence across all listed phases, but external services, isolation boundaries, staging, backups, and browser automation remain conditional. No phase is marked production-complete solely from route existence.
