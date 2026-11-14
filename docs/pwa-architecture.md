# PWA architecture

`public/manifest.webmanifest`, `public/sw.js`, and `components/pwa-register.tsx` provide the installable shell. The worker uses versioned cache-first fallback only for static assets and `/`, `/offline/library`, `/dashboard/mobile`, and the manifest. Authenticated API responses are never cached.
