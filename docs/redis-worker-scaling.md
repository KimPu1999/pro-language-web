# Redis worker scaling

Execution queue publishing is fail-closed when Redis or the runner is unavailable. Queue metrics are persisted through authenticated ingestion. At-least-once processing, dead-letter handling, worker restart recovery, and distributed queue backpressure require a deployed worker and Redis test environment; they are not claimed locally.
