# Platform monitoring

Authenticated platform staff can view persisted service checks at `/api/v1/platform/monitoring`. Health producers submit bounded service, status, latency, and detail values. The API labels the source as persisted health checks and reports `not_configured` when external telemetry is absent.
