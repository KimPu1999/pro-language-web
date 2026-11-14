# Workspace Security

The API never invokes a student shell. It never mounts a host Docker socket,
creates privileged containers, or exposes cluster-admin credentials. Runner
jobs are idempotent and fail closed when Redis or the isolated worker is not
configured. Production execution requires rootless containers or microVMs,
network policy, CPU/memory/process limits, timeouts, output limits, and cleanup
outside the FastAPI host.
