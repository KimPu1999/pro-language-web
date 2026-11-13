# Project review workflow

Submission states are `draft`, `submitted`, `in_review`, `changes_requested`, `approved`, and `rejected`. The API rejects invalid transitions and records reviewer, decision, score, comments, timestamps, and audit events.

Approval requires rubric criteria totaling 100 and a score for every criterion. Scores are calculated server-side as the weighted sum of criterion percentages. Approval creates idempotent verified project skill evidence and updates the student project status.
