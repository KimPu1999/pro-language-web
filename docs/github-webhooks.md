# GitHub webhooks

`POST /api/v1/github/webhooks` verifies `X-Hub-Signature-256` with the configured webhook secret and requires a delivery ID. Delivery IDs are unique in PostgreSQL, so repeated deliveries receive an idempotent acknowledgement. Payloads are stored by hash with no raw payload response.

The endpoint returns `503` when no webhook secret is configured. Event processing and retry workers remain disabled until GitHub provider configuration is reviewed.
