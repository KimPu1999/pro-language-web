# Real-time collaboration

Rooms are owned by users and may optionally be associated with an organization. Active room membership is required for room reads, chat, documents, snapshots and execution requests. The WebSocket endpoint is `/api/v1/ws/collaboration/{room_id}` and authenticates the existing HttpOnly session cookie.

The gateway is disabled unless `COLLABORATION_ENABLED=true`. It validates origin, membership, message size and event type. The current gateway persists updates and acknowledges the sending client; a multi-process broadcast layer and Yjs provider still require deployment configuration.
