# GitHub integration

GitHub is disabled unless `GITHUB_ENABLED=true` and the required provider configuration is present. The browser never receives an access or installation token. The current integration exposes a truthful status endpoint and refuses repository registration without a verified active connection.

Before enabling OAuth, implement a server-side state/PKCE store, exact callback URL allowlisting, token exchange over the backend, encrypted token storage backed by a deployment secret or KMS, expiry handling, disconnect revocation, and least-privilege GitHub App permissions.

Required configuration fields are documented in `backend/app/config.py`; credentials belong in deployment secret storage, never in source control or `NEXT_PUBLIC_*` variables.
