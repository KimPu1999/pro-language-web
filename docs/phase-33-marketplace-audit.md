# Phase 33 marketplace audit

The existing catalog uses `courses`, `enrollments`, `users`, `user_profiles`,
publishing reviews, community posts, learning recommendations, and platform
RBAC. Phase 33 reuses published courses and instructor identities, and adds an
additive resource/review/moderation domain for community educational content.
No payment, checkout, subscription, or revenue model was added.

Public discovery reads only `status=published` and `visibility=public`.
Contributor drafts are owner-scoped. Publishing requires an authorized human
moderation decision. Ratings, reviews, enrollment counts, and analytics are
read from persisted records; empty datasets remain empty.

Known limitations: full-text search indexing, asset malware scanning, external
license verification, course-level marketplace ratings, and production search
telemetry require deployment services and are not claimed locally.
