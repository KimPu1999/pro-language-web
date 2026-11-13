# Secure code execution

Lab runs reuse the existing runner availability boundary. With `RUNNER_ENABLED=false` or no worker, the API records `runner_unavailable` and reports that no code was executed. Production execution requires an isolated worker with resource and network controls.
