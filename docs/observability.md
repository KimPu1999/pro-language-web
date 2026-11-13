# Observability

FastAPI now returns or propagates `X-Request-ID` and adds baseline `nosniff` and `Referrer-Policy` headers. Logs use the application logger, but external metrics, traces, error tracking, database metrics, Redis metrics, worker metrics, runner metrics, and AI stream metrics are not configured.

Production setup should add OpenTelemetry or an equivalent collector, request latency/error counters, queue depth and age, database pool saturation, runner outcomes, AI quota/provider errors, and provider webhook failures. Redact passwords, tokens, API keys, private source, and private AI content.
