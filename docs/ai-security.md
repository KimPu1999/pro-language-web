# AI Security

All AI endpoints require the existing server session and CSRF protection for writes. Conversation IDs are checked against the authenticated user on every read, write, and stream request. Admin inspection requires the existing full-admin authorization dependency.

Student messages, code, repository descriptions, and retrieved lesson text are untrusted input. The provider system instruction treats retrieved content as reference material. Context retrieval is allowlisted and published-only; it does not provide arbitrary database, filesystem, network, runner, hidden-test, or tool access.

The application does not execute code through the AI service. Markdown is displayed as text in the initial tutor UI, which avoids executing assistant HTML. Provider credentials remain server-side and are never logged or returned by admin settings.

The disabled-provider state is a security and correctness requirement when no approved provider is configured. It prevents fabricated responses and prevents accidental external data transfer.
