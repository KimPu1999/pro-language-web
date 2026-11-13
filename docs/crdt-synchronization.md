# CRDT synchronization

Document updates are stored as opaque bounded bytes with a monotonically increasing document version. Updates and snapshots are linked to the room document and actor. The API does not interpret or execute CRDT payloads. Yjs multi-client convergence requires a configured gateway and integration test with at least two clients.
