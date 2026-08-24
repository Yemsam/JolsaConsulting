// Minimal service worker — exists only to satisfy browsers' PWA
// installability checks (Chrome's automatic install prompt still looks
// for a registered fetch handler). It intentionally does NOT cache
// anything, so the site always loads fresh from the network exactly like
// it did before — no offline mode, no stale-content risk.
self.addEventListener("install", () => {
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener("fetch", (event) => {
  event.respondWith(fetch(event.request));
});
