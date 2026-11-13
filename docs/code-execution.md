# Interactive classroom

Phase 4 adds the execution contract without running untrusted source inside FastAPI. Students use the Monaco editor on the lesson page. `POST /api/v1/runner/execute` creates an idempotent job, and the queue adapter publishes it to Redis only when `RUNNER_ENABLED=true`.

The default development behavior is deliberately safe: the API records `runner_unavailable` and returns a clear result. This means the classroom UI is functional as an editor and job-status surface while execution remains disabled until a hardened worker is deployed.

Supported runtime identifiers are Python, JavaScript, TypeScript, Java, C++, and PHP. The registry records a version, filename, and image reference for a future worker. Exercises expose public test cases only; hidden tests remain server-side.
