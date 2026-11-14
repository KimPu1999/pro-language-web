# Offline download manager

The browser stores downloaded packages in the versioned `codemaster-offline` IndexedDB database. Course records can be removed locally. Server manifests are account-scoped; partial browser failures remain local and can be retried. Storage quota errors are surfaced to the UI rather than hidden.
