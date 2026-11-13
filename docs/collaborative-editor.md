# Collaborative editor

Team code documents include durable CRDT-state metadata, versions, and snapshot records. The production gateway must use an authenticated CRDT protocol such as Yjs over WebSockets, persist state outside Redis Pub/Sub, validate team membership on every connection, and enforce payload/rate limits. Until that gateway is deployed, the API reports collaboration as unavailable.
