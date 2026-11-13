# Roadmap builder

Administrators and instructors with server-side authorization can create roadmap drafts, add stages and steps, attach course/challenge resources, reorder steps, and publish a roadmap. English descriptions are required for publishing. Prerequisites are stored as a directed graph; self-dependencies and cycles are rejected before commit.

Roadmap revisions preserve a place for immutable snapshots as the builder grows. Reordering changes positions and does not delete student progress, which is keyed by roadmap enrollment and step UUID.
