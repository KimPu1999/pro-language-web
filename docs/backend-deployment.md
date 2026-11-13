# Backend deployment

Build and run:

```bash
docker build -t codemaster-api ./backend
docker run --read-only --cap-drop=ALL --security-opt=no-new-privileges \
  -p 8000:8000 --env-file backend/.env codemaster-api
```

The image runs as a non-root user and does not use reload mode. Configure `DATABASE_URL`, strict `CORS_ORIGINS`, secure cookies, and a secret-managed environment. Run `alembic upgrade head` as a controlled release step, then verify `/api/v1/health` and `/api/v1/ready`.
