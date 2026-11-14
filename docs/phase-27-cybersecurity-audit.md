# Phase 27 Cybersecurity Audit

The repository already contains reusable authenticated learning labs,
workspace ownership checks, Monaco, Redis-backed secure runner queueing,
challenge submissions, AI Tutor quotas/redaction, learning intelligence,
certificate verification/revocation, organization membership, content review,
and platform RBAC.

Phase 27 adds tenant-aware cybersecurity lab definitions, attempts,
vulnerability findings, remediations, threat models and versions, AI
interactions, security events, and audit logs. Security routes accept owned
workspace IDs only; arbitrary external target URLs are rejected by design.

The secure runner is fail-closed unless configured. OWASP, API security,
defensive analysis, and deployment-style scenarios are catalog/simulation
surfaces until approved isolated target images and workers are deployed. No
public vulnerable service, platform secret, Docker socket, or cluster-admin
credential is exposed.
