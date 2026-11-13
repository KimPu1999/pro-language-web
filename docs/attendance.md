# Attendance

Attendance is based on authenticated presence events and a unique session/user attendance row. Presence event keys are idempotent to handle reconnects and duplicate provider callbacks. Client-only attendance flags are not trusted.
