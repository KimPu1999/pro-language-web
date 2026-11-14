# Student success architecture

Student-facing support uses `/api/v1/student-success`. Existing learning and feedback records remain the source of truth. New tables store support tickets, transparent signal evidence, consent, plans, escalations, and audit events. Staff access is role checked on the server; platform views expose aggregate counts only.
