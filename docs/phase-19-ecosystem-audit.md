# Phase 19 ecosystem audit

The existing application has session-cookie authentication, server-side role checks, PostgreSQL migrations, Redis-backed worker configuration, team collaboration, portfolios, notifications, project reviews and the secure runner boundary. Before this phase there was no GitHub connection, webhook, repository sync, contribution, or public developer profile model.

Phase 19 adds additive tables and routes for those records. Public repository data is limited to approved and public records. Contribution records are private by default and are returned only when server-synced evidence is marked verified. GitHub credentials are never returned by an API response.

The GitHub provider is currently **Not Configured** by default. OAuth callback/PKCE exchange, encrypted token persistence, repository sync workers, and provider API calls remain disabled until deployment credentials and a reviewed provider implementation are supplied. The application therefore does not claim that GitHub is connected or that contributions are verified.

## Risks and follow-up

| Area | Status | Risk |
| --- | --- | --- |
| OAuth/PKCE | unavailable until configured | Do not enable connect UI without a state store and callback allowlist |
| Token encryption | storage column reserved; no token exchange enabled | Use a managed secret/KMS-backed encryption implementation before storing tokens |
| Webhooks | HMAC and delivery deduplication endpoint implemented | Background event processing is not enabled until GitHub is configured |
| Repository sync | schema and status surface added | Provider rate-limit and retry worker still required |
| Contributions | verified-only query paths | No user-submitted URL can create verified evidence |
| Privacy | public profiles are opt-in; private profiles return 404 | Continue reviewing profile and repository visibility in future sync work |

See [GitHub integration](github-integration.md), [webhooks](github-webhooks.md), and [contribution verification](contribution-verification.md).
