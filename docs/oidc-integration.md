# OIDC integration

OIDC requires a maintained library and server-side Authorization Code + PKCE flow with state, nonce, issuer, audience, signature and expiry validation. The current environment has no OIDC provider configured, so the API reports `Not Configured` and performs no token exchange.
