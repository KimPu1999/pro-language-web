# Video Provider Setup

Default configuration keeps media disabled:

```env
VIDEO_PROVIDER=disabled
VIDEO_ENABLED=false
VIDEO_TOKEN_TTL_SECONDS=900
```

A production adapter must generate short-lived provider tokens server-side, validate participant identity and role, verify provider webhooks, and keep credentials outside the frontend. The current implementation deliberately does not claim live video functionality.
