# Backup monitoring

Backup checks and restore drills are separate records. A successful backup does not imply restore readiness. The API returns `unknown_without_restore_evidence` until a restore drill record with evidence is available.
