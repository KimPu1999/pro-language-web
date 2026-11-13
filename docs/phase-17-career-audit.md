# Phase 17 career audit

Existing career inputs were the Phase 6 career roadmaps and goals, Phase 16 verified skill snapshots, Phase 7 approved student projects and portfolios, Phase 8 AI Tutor, and Phase 11 live-session infrastructure. No prior mentor, resume, interview, or application tables were present.

Migration `0015_career_development` adds career profiles/goals/readiness snapshots, mentor approval and UTC availability, mentorship requests/sessions/feedback, private resume documents and versions, portfolio review requests/feedback, interview questions/sessions/attempts/evaluations, private job applications, and career audit logs.

Known limitations are explicit: no provider-backed meeting links are generated, PDF export returns a truthful not-configured response, and coding interview execution remains behind the existing secure runner rather than the FastAPI process.
