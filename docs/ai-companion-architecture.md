# AI companion architecture

The companion dashboard and adaptive records are separate from the existing tutor transport. Authorized learning context is read from the current user, published courses, enrollment, lesson progress, and verified skill evidence. Existing `/api/v1/ai/conversations/{id}/stream` remains the SSE path; provider secrets stay server-side.
