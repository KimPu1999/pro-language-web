# Learning path architecture

The roadmap service is the source of truth for stage ordering and prerequisites. It does not copy course content. `roadmap_step_resources` references existing resource IDs, while `student_roadmap_progress` remains an evidence record and does not replace lesson progress.

Public endpoints scope records to `published = true`. Admin creation and publishing remain protected by the existing admin dependencies and CSRF checks. Prerequisite creation rejects self-dependencies and cycles before writing the edge.
