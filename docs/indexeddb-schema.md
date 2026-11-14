# IndexedDB schema

Database `codemaster-offline`, version 1, contains `courses` keyed by `manifest_id` and `events` keyed by unique `event_id`. A future schema must use an explicit upgrade handler and preserve account logout cleanup. The client never stores access or refresh tokens in IndexedDB.
