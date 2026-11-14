# Challenge Builder

The existing instructor challenge administration API remains the source of
truth for challenge creation, hidden tests, review, and publishing. The Phase
39 route `/instructor/challenges/builder` provides the entry surface; it does
not bypass instructor authorization or expose hidden tests.
