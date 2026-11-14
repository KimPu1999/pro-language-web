const CACHE = "codemaster-shell-v1";
const SHELL = ["/", "/offline/library", "/dashboard/mobile", "/manifest.webmanifest"];
self.addEventListener("install", (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(SHELL)).then(() => self.skipWaiting()));
});
self.addEventListener("activate", (event) => {
  event.waitUntil(caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", (event) => {
  const request = event.request;
  const url = new URL(request.url);
  if (request.method !== "GET" || url.origin !== self.location.origin || url.pathname.startsWith("/api/") || url.pathname.includes("/_next/data/")) return;
  const isStaticAsset = ["script", "style", "font", "image"].includes(request.destination);
  const isOfflineShell = SHELL.includes(url.pathname);
  if (!isStaticAsset && !isOfflineShell) return;
  event.respondWith(fetch(request).then((response) => { if (response.ok) { const copy = response.clone(); caches.open(CACHE).then((cache) => cache.put(request, copy)); } return response; }).catch(() => caches.match(request).then((cached) => cached || caches.match("/offline/library"))));
});
