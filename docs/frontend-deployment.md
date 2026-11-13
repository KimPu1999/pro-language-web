# Frontend deployment

Build with:

```bash
cd frontend
npm ci
npm run lint
npm run typecheck
npm run test:unit
npm run build
```

For Vercel, set `API_INTERNAL_URL` only if a server-side private route is needed and set `NEXT_PUBLIC_API_BASE_URL` only to a public API origin. Never put API keys, database URLs, SMTP credentials, Redis URLs, or signing secrets in `NEXT_PUBLIC_*` variables.

The frontend rewrite targets `API_INTERNAL_URL`; production should use a private service hostname or same-origin gateway. Verify `/`, `/courses`, `/login`, `/platform`, and `/api/v1/health` after deployment.
