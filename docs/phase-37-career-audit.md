# Phase 37 career audit

The repository already contained `CareerProfile`, `CareerRoadmap`, `ResumeDocument`/`ResumeVersion`, mentorship, interview practice, `JobApplication`, portfolios, certificates, and verified skill evidence. Phase 37 extends those sources instead of replacing them. New work adds explicit talent visibility, employer verification, reviewed job postings, opt-in discovery, skill-gap evidence views, contact requests, fraud reports, and audit records.

The legacy job application table remains the source of truth for the existing private application tracker. `career_application_events` records its status history. No employer is trusted or exposed until a platform administrator explicitly verifies it.

Known limitations: job applications are still the existing student-owned tracker and are not yet linked to postings; PDF resume export remains not configured; no hiring outcome or readiness prediction is generated.
