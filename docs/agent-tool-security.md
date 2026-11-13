# Agent tool security

Workflow and agent inputs are untrusted. The server uses allowlisted tool/action names, organization membership checks, input validation, output boundaries, audit records, and provider status checks. Arbitrary shell, SQL, filesystem, or unrestricted HTTP execution is not available.
