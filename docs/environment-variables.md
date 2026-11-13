# Environment variables

Required production values include `DATABASE_URL`, `CORS_ORIGINS`, `APP_BASE_URL`, `COOKIE_SECURE=true`, and a real mail configuration. Redis, AI, video, runner, and storage credentials belong only in the backend/worker environments.

Development defaults intentionally use local services and disable runner, AI, and video. Copy `.env.example`; do not commit `.env`, provider keys, passwords, or production URLs.
