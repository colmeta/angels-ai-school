const CACHE_NAME = "angels-ai-cache-v1";
const OFFLINE_URLS = ["/", "/index.html", "/manifest.webmanifest"];

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(OFFLINE_URLS);
    }),
  );
  self.skipWaiting();
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) =>
      Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
          return null;
        }),
      ),
    ),
  );
  self.clients.claim();
});

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") {
    return;
  }

  event.respondWith(
    caches.match(request).then((cachedResponse) => {
      if (cachedResponse) {
        event.waitUntil(fetchAndUpdateCache(request));
        return cachedResponse;
      }
      return fetchAndUpdateCache(request);
    }),
  );
});

async function fetchAndUpdateCache(request) {
  try {
    const response = await fetch(request);
    const cache = await caches.open(CACHE_NAME);
    cache.put(request, response.clone());
    return response;
  } catch (error) {
    if (request.mode === "navigate") {
      const cache = await caches.open(CACHE_NAME);
      const cachedResponse = await cache.match("/index.html");
      if (cachedResponse) {
        return cachedResponse;
      }
    }
    throw error;
  }
}

self.addEventListener("sync", (event) => {
  if (event.tag === "sync-offline-queue") {
    event.waitUntil(
      self.clients.matchAll({ includeUncontrolled: true }).then((clients) => {
        clients.forEach((client) => client.postMessage({ type: "SYNC_REQUEST" }));
      }),
    );
  }
});
