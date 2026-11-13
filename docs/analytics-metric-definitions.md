# Analytics metric definitions

- **Active students:** distinct students with an enrollment, lesson-progress update, or challenge submission during the selected UTC period.
- **Completion rate:** eligible enrollments with every published lesson completed divided by eligible enrollments. Enrollments for courses with zero published lessons are excluded.
- **Challenge success rate:** accepted evaluated submissions divided by evaluated submissions. Queued, running, and internal infrastructure failures are excluded.
- **Certificates issued:** non-revoked certificates issued inside the selected period. Revoked credentials are excluded from active counts.
- **Community activity:** published posts and answers created inside the selected period; private or removed content is not counted.

Empty denominators return `0`, never `NaN`. Counts are based on distinct source records and are not inferred from frontend progress values.
