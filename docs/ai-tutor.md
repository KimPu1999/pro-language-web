# AI Tutor

The AI Tutor is an authenticated, user-owned conversation service at `/ai-tutor`. It supports conversation history, rename/delete, SSE response streaming, cancellation from the browser, retrying failed requests, copyable responses, and a persisted English/Myanmar preference.

The backend stores user and assistant messages with explicit statuses. A normal completion emits `token` events followed by `complete`. Provider failures emit `error`, mark the assistant message as failed, and do not present an invented answer.

Lesson and challenge assistance must provide an authorized published record identifier. The server retrieves only the minimum published English content required for the request. Hidden tests, private instructor material, and other student data are never context sources.

Automated tests use the provider abstraction and do not call a paid service. Set `AI_PROVIDER=mock` and `AI_ENABLED=true` only for local contract testing; this returns a clearly synthetic response.
