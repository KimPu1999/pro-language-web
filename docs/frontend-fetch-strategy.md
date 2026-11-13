# Frontend Fetch Strategy

The shared API client and analytics API client deduplicate simultaneous GET requests by URL. This addresses duplicate requests caused by React development remounts without adding stale cross-user caching. POST, PUT, PATCH and DELETE calls are never deduplicated.

The shared client retains its eight-second timeout and explicit connection/timeout messages. Authentication and authorization errors are preserved as API errors; the client does not fabricate fallback data or bypass access checks.

Client-side query caches were not introduced because the repository does not currently use TanStack Query and adding a second query provider would increase scope. Long-lived cache policy can be added after traffic measurements justify it.
