# Course System

CodeMaster Academy uses the existing \`courses\`, \`course_modules\`, \`lessons\`,
\`code_examples\`, \`enrollments\`, and \`lesson_progress\` tables. Published
content is public and free to read. Enrollment is required before a verified
student can persist completion state.

The course catalog supports server-side search, language, level, and category
filters. The lesson reader loads a published course with ordered modules and
lessons, keeps source code read-only by default, and offers an optional link
to the existing practice runner.

Lesson completion and bookmarks are private records scoped by authenticated
user. Public course content is safe to cache; progress and bookmarks must
never be placed in a shared public cache.
