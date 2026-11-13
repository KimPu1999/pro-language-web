# Phase 12 analytics

CodeMaster Academy analytics reads the existing users, courses, enrollments, lesson progress, challenge submissions, certificates, and community tables. It does not maintain a second copy of transactional learning data.

Platform analytics is available at `/platform/analytics`. Platform administrators can use all reports. Instructors can use scoped course, instructor, and course analytics for courses they own or are assigned to. Students and untrusted roles receive `403` or `401` responses.

The overview supports UTC date filters and a CSV export. Exports are CSRF protected, administrator-only, and recorded in `analytics_report_exports` and `analytics_audit_logs`.
