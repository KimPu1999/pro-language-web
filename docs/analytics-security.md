# Analytics security

Platform-wide analytics and exports require `admin` or `super_admin`. Instructor analytics are scoped to owned or assigned courses. Student accounts cannot access platform analytics. Export requests require the server-managed session and CSRF token, and every export writes an audit record.

Analytics responses contain aggregate values and limited administrator-authorized rows. Password hashes, session tokens, private community content, and raw student submissions are never returned by these endpoints. Date ranges and pagination are validated server-side.
