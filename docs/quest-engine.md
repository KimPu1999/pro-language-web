# Quest Engine

Quest definitions and immutable published versions describe the rule and reward.
Assignments are user-scoped and expire. The implemented rule is
`challenge_solved`, verified against `StudentChallengeProgress.solved`; other
rule types are represented for future server-side evidence adapters and are not
trusted merely because a browser submits them.

Completion is idempotent by assignment and protected by a database uniqueness
constraint. Repeated or racing requests return `already_completed`.
