# Ratings and reviews

Reviews have a unique `(resource, reviewer)` constraint, rating bounds of 1–5,
rate limits, self-review prevention, and moderation status. Aggregates are
computed from published persisted reviews; no synthetic ratings are created.
