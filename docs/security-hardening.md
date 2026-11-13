# Security hardening

Authentication uses server-managed cookies, Argon2 password hashes, normalized emails, CSRF checks for cookie-authenticated mutation, and role dependencies in the API. Authorization is enforced in backend routes; UI visibility is not a security boundary.

Untrusted code is fail-closed when the sandbox runner is disabled. Hidden challenge tests are not returned by public routes. AI context is selected after authorization and provider keys remain server-side. Live-room access is unavailable until a real provider adapter can issue short-lived, role-scoped tokens.

Do not enable production services with development defaults (`COOKIE_SECURE=false`, local CORS, disabled provider flags). Run dependency and secret scans with network access, rotate any accidentally exposed secret, and review logs for passwords, tokens, private code, and private AI content.
