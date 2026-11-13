# XP Rules

XP is represented by an idempotent event ledger. Each event must have a user-scoped idempotency key, source type, and verified server-side source before production event handlers award points. Refreshes and duplicate delivery therefore cannot create additional rewards.

The default policy is lesson completion 10 XP, accepted challenge 30 XP, course completion 100 XP, approved project 150 XP, and roadmap completion 300 XP. Threshold definitions are stored in `xp_level_definitions`.
