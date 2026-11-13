# WebSocket security

The gateway uses the existing session cookie, validates the request origin against configured CORS origins, checks active room membership, limits message size, and accepts only presence, chat and bounded CRDT update events. Session revocation is checked when the socket is opened. Production deployment should add connection quotas, distributed fan-out and periodic revalidation.
