# Phase 16 learning audit

The repository already contains Phase 6 tables and routes for career roadmaps, roadmap enrollment, learning goals, skill definitions, skill evidence, assessments, and the original recommendation records. Phase 8 provides the authenticated AI provider boundary, and Phase 12/13 provide analytics and worker-related operational patterns.

Phase 16 extends those tables instead of duplicating them. The additive migration `0014_learning_intelligence` adds skill prerequisites and snapshots, recommendation feedback, study plans and items, revision items and attempts, private risk indicators, and coach interaction audit records.

Evidence is read from persisted lesson progress, challenge/project evidence, and verified assessments. Scores are intentionally marked `Not Yet Assessed` when evidence is insufficient. Published course filtering is enforced in recommendation queries. AI coach requests are recorded with minimal context and return an unavailable state when the configured provider is disabled.

Known repository limitations: Redis workers are not configured in this development environment, the secure runner is fail-closed by default, and no AI provider is configured. The PostgreSQL migration must be verified against the configured database before release.
