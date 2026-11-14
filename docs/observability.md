# Observability

FastAPI emits request IDs, route, status, duration, and error category without credentials or request bodies. The current repository does not configure an OpenTelemetry exporter, Prometheus scrape endpoint, or external error-tracking DSN. Those integrations require deployment configuration and verification before being called healthy.
