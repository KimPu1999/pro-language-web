# Certificates

Certificates are issued from verified backend events and use unpredictable public IDs. Active certificates expose only the title, display name, issuer, issue date, status, and verification URL. Issuance must be idempotent per student, achievement type, and resource.

Certificate PDFs are generated server-side and download through the authenticated certificate library. Revocation records the administrator and reason while public verification reports `revoked`.
