# Enterprise security

State-changing organization endpoints require the existing double-submit CSRF check. Invitations store token hashes, expire after three days, and can only be accepted by the invited normalized email. The final active owner cannot be removed. Platform organization actions require global admin roles. Support access is scoped, time-limited and audit-recorded.
