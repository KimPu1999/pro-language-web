# Learning paths

Learning paths are published career roadmaps backed by the existing `career_roadmaps`, `roadmap_stages`, `roadmap_steps`, and `roadmap_step_resources` tables. A step can reference an existing course, challenge, or approved project; course and lesson progress remains in the existing progress tables.

The public catalog is available at `/learning-paths`. It reads only published records and supports search, category, level, and pagination filters. `/learning-paths/{slug}` shows the reviewed roadmap and uses `/courses/{slug}` links for course content.

Path duration is editorial data stored on the roadmap. If it is zero, the UI displays `Editorial estimate pending` rather than inventing a duration.

Users can enroll, pause, resume, and bookmark paths. Completion is derived from verified course, challenge, and approved project evidence. Optional resources do not increase mandatory completion totals.
