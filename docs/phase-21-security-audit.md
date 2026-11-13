# Phase 21 security audit

The existing application uses Argon2id password hashes, HttpOnly session cookies, CSRF cookies/headers, expiring sessions, email verification, password reset tokens, global role checks, organization membership checks and additive PostgreSQL migrations. Phase 20 did not include SSO, MFA, passkeys, SCIM, security policy, access-review, compliance, retention, or privacy-request records.

Phase 21 adds tenant-scoped security records and server-side management workflows. OIDC, SAML, TOTP and WebAuthn are explicitly `Not Configured` unless maintained protocol libraries, provider settings, origin/audience configuration, and integration tests are supplied. No protocol cryptography is implemented manually.

Known limitations: provider callback flows are unavailable; MFA secrets are never generated; SCIM is disabled by default; PostgreSQL RLS is still a defense-in-depth follow-up; compliance controls are readiness records and do not imply SOC 2, ISO 27001, or any certification.
