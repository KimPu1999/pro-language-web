+# Course Content Schema

Existing content records:

- `courses`: published course metadata, language, level, category, outcomes.
- `course_modules`: ordered prerequisite units.
- `lessons`: ordered theory content, bilingual text, duration, publication state.
- `code_examples`: ordered language-specific source examples attached to lessons.
- `course_revisions` and `publishing_reviews`: authoring and publication history.
- `lesson_progress`: private completion and last visited timestamp.
- `lesson_bookmarks`: private user bookmarks with a unique user/lesson constraint.

The `0024_lesson_bookmarks` migration is additive and does not alter existing
student progress or published content.

