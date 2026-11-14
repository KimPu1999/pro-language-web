# Roadmap

Phase 1 delivers the public catalog and read-only classroom foundation. Phase 2 delivers student authentication, email verification, password recovery, profiles, enrollment, progress persistence, and real student dashboards. Phase 3 can add instructor/admin course management, practice exercises, project submissions, and safe sandboxed code execution outside the API process.
Phase 3 delivers the first CMS foundation: taxonomy management, course drafts, curriculum and lesson authoring, code examples, ownership checks, revision snapshots, review decisions, and publish/archive workflow. Phase 4 can add richer markdown blocks, media storage, drag-and-drop ordering, instructor assignment screens, and advanced code execution.

Phase 4 delivers the interactive editor and execution boundary: Monaco, supported runtime registry, Redis job contracts, exercises, submissions, result persistence, and security documentation. Remaining work before a production execution launch includes deploying and reviewing the isolated worker, internal result callbacks, richer exercise authoring UI, and full cross-browser classroom automation. Phase 5 can add projects, assessments, discussions, certificates, and other advanced learning features.

Phase 5 adds the challenge catalog, challenge workspace, assessment schema, submission lifecycle, analytics contracts, daily assignments, and achievement persistence. Before production grading, deploy the isolated runner callback/grading service and complete the challenge management editor. Phase 6 can add projects, contests, peer review, and certificates.

Phase 6 adds personalized career roadmaps, learning goals, prerequisite-aware steps, evidence-based progress, and deterministic recommendations. Phase 7 can add social learning, mentor review, richer project assessments, and certificates.

Phase 7 adds real-world project templates, milestones, GitHub metadata submission, instructor review workflow, weighted rubrics, verified project evidence, and private/public portfolios. Phase 8 can add GitHub App private-repository synchronization, secure media storage, mentor assignment, and richer portfolio presentation.

Phase 8 adds the AI Tutor foundation: provider abstraction, disabled-provider behavior, persistent conversations, streaming transport, published lesson/challenge context retrieval, usage quotas, preferences, and admin operational visibility. Phase 9 can add a production provider adapter, richer project and roadmap assistant surfaces, evaluation, and additional AI-supported learning workflows.

Phase 10 adds the community foundation: public discussions, Q&A answers, bounded comments, votes, bookmarks, code snippets, public study groups, reports, blocks, and notifications. Phase 11 can add real-time collaboration, mentor spaces, richer moderation workflows, and advanced community discovery.

Phase 11 adds scheduled live classes, registrations, waitlist records, room authorization, provider configuration, attendance, chat, Q&A, and classroom UI states. Phase 12 can add a production WebSocket gateway, supported video integration, background reminder jobs, recordings, and collaborative live coding.
## Phase 12

Phase 12 adds real-data platform analytics, metric definitions, administrator-only CSV reporting, export audit records, and scoped instructor analytics. See `docs/phase-12-analytics.md`, `docs/analytics-metric-definitions.md`, and `docs/analytics-security.md`.

## Phase 13

Phase 13 adds regression test infrastructure, request correlation headers, fail-closed live-room behavior, the administrator quality-status page, CI quality gates, dependency-scan hooks, and production-readiness/security documentation. Real runner, video, AI, telemetry, backup restore, and load-test verification remain deployment prerequisites.

Phase 15 adds additive operations records, incident lifecycle APIs, student feedback ownership, engineering issue/release history, maintenance visibility, and an operations status surface. External monitoring, billing, backup, alerting, and deployment integrations remain provider-dependent and are shown as unknown until verified.

## Phase 30

Phase 30 is an audit and remediation phase. See the `docs/phase-30-*.md` audit, matrix, defect register, test report, and release checklist. It is not a deployment approval.

## Phase 31

Phase 31 adds post-launch monitoring records, student feedback, bug reporting, alert deduplication, release approvals, feature flags, maintenance notices, public status, backup evidence, and operational reviews. External telemetry and provider health remain deployment responsibilities.
# Phase 16 status

Learning intelligence is implemented with evidence-based skill snapshots, rule-based recommendations, verified study-plan tracking, spaced repetition records, and an unavailable-safe AI coach surface. Background refresh and richer provider integrations remain operational follow-up work.

Phase 17 adds career readiness, approved mentorship, private resume versions, portfolio review requests, timed interview practice, and private job application tracking. Phase 18 can add richer provider-backed scheduling, safe PDF rendering, and deeper interview evaluation.

Phase 18 adds team management, team projects/tasks, hackathon registration/submissions, competition records, and verified leaderboard contracts. Real-time CRDT collaboration and isolated competition execution remain deployment prerequisites when their providers are unavailable.

Phase 19 adds the developer hub, opt-in public developer profiles, approved open-source project/opportunity discovery, server-side GitHub webhook verification, contribution verification records, code review requests, maintainer surfaces, and privacy controls. GitHub OAuth, encrypted token persistence, repository synchronization, and provider-backed actions remain prerequisites for the next phase unless configured and independently tested.

Phase 20 adds organization creation, tenant memberships and invitations, organization teams, private course mappings, training programs, assessments, privacy-threshold analytics, exports, settings, platform organization oversight and time-limited support access. PostgreSQL RLS, full assessment authoring, worker-backed exports and production capacity measurements remain deployment follow-up work.

Phase 21 adds security policy/audit/access-review records, session revocation, privacy requests, compliance readiness records, and SCIM token/provisioning boundaries. OIDC, SAML, TOTP, passkeys, PostgreSQL RLS, retention workers and provider-backed compliance evidence remain configuration and integration prerequisites.

## Phase 22

Phase 22 adds tenant-scoped automation workflows, validated graph versions, durable queued run records, approval records, idempotency keys, agent/tool permission records, recommendations, usage visibility, and automation dashboards. A workflow worker, scheduler, and live AI provider remain explicitly unavailable until configured and independently tested.

## Phase 23

Phase 23 adds tenant-scoped AI content projects, durable generation job states, lesson/quiz/challenge/project drafts, separate translations, quality-check records, revision snapshots, independent review, and approved publication records. AI generation remains `Not Configured` or `provider_unavailable` without a real provider and worker; content can still be edited manually.

## Phase 24

Phase 24 adds published learning labs, owned workspaces, path-safe files, snapshots, durable run/submission records, progress records, instructor lab records, and truthful runner/SQL/API unavailable states. Isolated code workers, ephemeral SQL sandboxes, and controlled mock API services remain deployment prerequisites.
## Phase 25 — Advanced real-time collaboration

Added the room and durable document foundation, authenticated WebSocket contract, pair-role authorization, chat, snapshots, consent records, collaboration dashboards, and security documentation. Multi-client Yjs fan-out and provider-backed execution/recording remain deployment work.
## Phase 26 status

Cloud catalog, dashboard, owned workspaces, Monaco editing, lifecycle state,
file quota, snapshots, platform operations, and truthful execution-mode
reporting are implemented. Isolated Docker/microVM execution, Kubernetes
integration, public previews, and provider-backed AI remain deployment work,
not claimed functionality. Phase 27 should not begin until those boundaries
have independent security validation.

## Phase 27 status

The cybersecurity catalog, learning-path surfaces, approved lab records, ownership-scoped attempts, threat-model version one, instructor draft creation, AI status, and platform operations are implemented. Secure execution, server-side grading, vulnerability evidence generation, external provider AI, and published instructor workflows remain unavailable until their isolated workers/providers are configured and tested. No arbitrary target scanning is implemented.

## Phase 28 status

The mobile dashboard, PWA shell, offline library/reader, IndexedDB event queue, authenticated sync boundary, preferences, push subscription records, instructor status, and platform operations surface are implemented. Browser offline installation, push delivery, accessibility automation, and PostgreSQL migration execution require environment-level verification and are not claimed as complete here.

## Phase 29 status

The companion dashboard, authorized adaptive records, deterministic revision v1, evidence-labelled recommendations, optional goals/plans, privacy controls, instructor privacy-threshold status, and platform operations are implemented. AI provider responses, voice delivery, provider-side deletion, cost/latency telemetry, and end-to-end streaming/browser verification remain configuration or environment prerequisites.

## Phase 32 status

Scalability routes, platform-admin protection, capacity-policy records, and
truthful dashboard states are implemented. Multi-instance load tests, paid
autoscaling, read replicas, CDN integration, failover drills, restore evidence,
and global deployment remain environment-level work and are not claimed here.

## Phase 33 status

The free marketplace catalog, bounded search, contributor drafts, resource
versions, human review decisions, collections, review integrity, licensing
metadata, reports, moderation queue, and persisted analytics surfaces are
implemented. External full-text indexing, media scanning, rich asset delivery,
and production engagement telemetry remain deployment work.

## Phase 35 status

The student success dashboard, private ticket lifecycle, evidence-backed signal visibility, student-controlled support plans, consent-gated mentor escalation, published help lookup, persisted outcomes, privacy controls, and aggregate platform overview are implemented. Attachment storage/scanning, automated signal generation, and complete staff knowledge authoring remain follow-up work.

## Phase 36 status

Assessment definitions, published version snapshots, secure attempt state, deterministic grading, integrity review records, appeals, competency records, credential verification, and platform credential controls are implemented. Project artifact validation, background runner grading, live PostgreSQL migration testing, and browser verification remain environment-dependent.

## Phase 34 status

Instructor onboarding, approval records, teaching standards, training
enrollment, quality/peer-review records, analytics privacy states, development
plans, draft-only AI coaching, certification eligibility status, appeals, and
platform oversight are implemented. Certificate issuance, provider-backed AI,
and full rubric scoring require additional verified evidence and configuration.
## Phase 37 — Career readiness

Implemented additively: career dashboard entry points, private talent profiles, evidence-based skill gaps, employer verification gates, reviewed job discovery, opt-in talent contact, and audit/report controls. Remaining work is provider/infrastructure validation for production job workflows and resume rendering.
## Phase 38 — Global learning community

Implemented foundations include community hub, coding clubs, opt-in developer discovery, peer-learning requests, moderated events, capacity-aware registration, public feed, verified reputation summary, safety reports, and platform analytics.

## Phase 39 — Learning gamification

Implemented foundations include verified quest assignments/completions, an
idempotent XP ledger, level-rule support, global challenge and competition
catalog entry points, opt-in leaderboards, competition appeals, integrity-case
storage, gamification analytics, and dedicated route surfaces. Live runner,
competition scale, browser, and migration validation remain release checks.

## Phase 40 — Enterprise audit

Phase 40 inventory and remediation documents now classify the repository by
evidence. Confirmed P1 defects were fixed, but the release remains NO-GO until
staging infrastructure, backup restore, runner isolation, E2E, load, and
security evidence are available.
