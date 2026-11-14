# Phase 28 mobile/offline audit

The repository had no manifest, service worker, IndexedDB store, push subscription model, or offline sync API. Existing course, lesson, bookmark, progress, authentication, CSRF, organization, and platform-RBAC services are reusable. Phase 28 adds a separate mobile boundary and migration `0030_mobile_offline`.

The service worker caches only the explicit app/offline shell and static assets. It excludes `/api/`, Next data, session cookies, private AI data, hidden tests, and platform secrets. Offline lesson completion is a local event until authenticated synchronization applies it as ordinary learning progress.

Verified status: backend mobile tests pass; browser network-disconnection, install-prompt, screen-reader, and push-provider tests require a running browser/provider environment and are not claimed here.
