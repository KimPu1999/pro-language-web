# Challenge security

Hidden tests are stored separately from public challenge responses and are never serialized by catalog or detail endpoints. Submission records are scoped by `user_id`; history queries cannot return another student's source. Admin challenge writes require the existing server-side role checks and CSRF protection.

Production grading must use the Phase 4 isolated runner contract with no API-host subprocess execution, no network access, no host mounts, no credentials, bounded output, immutable runtime images, and queue capacity controls. A disabled or unavailable runner is a safe failure state.
