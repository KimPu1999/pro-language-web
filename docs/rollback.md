# Rollback

1. Stop the release and capture request IDs, deployment version, and failing checks.
2. Roll back the application artifact to the last known-good version when the schema remains compatible.
3. Do not automatically reverse migrations. Use forward-compatible repair migrations after review.
4. If data integrity is involved, isolate writes, restore into staging, reconcile records, and obtain explicit approval before production action.
5. Run health, readiness, authentication, public-course, and critical smoke checks before reopening traffic.
