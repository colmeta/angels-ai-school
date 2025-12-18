// Service Worker for Offline-First PWA
// Caches assets and API responses for offline access

const CACHE_NAME = 'angels-ai-v1';
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/manifest.json',
    '/offline.html'
];

const API_CACHE = 'angels-ai-api-v1';

// Install - cache static assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(STATIC_ASSETS);
        })
    );
    self.skipWaiting();
});

// Activate - clean old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames
                    .filter((name) => name !== CACHE_NAME && name !== API_CACHE)
                    .map((name) => caches.delete(name))
            );
        })
    );
    self.clients.claim();
});

// Fetch - network first, fallback to cache
self.addEventListener('fetch', (event) => {
    const { request } = event;

    // API requests - Network first, cache fallback
    if (request.url.includes('/api/')) {
        event.respondWith(
            fetch(request)
                .then((response) => {
                    // Clone response to cache it
                    const responseClone = response.clone();
                    caches.open(API_CACHE).then((cache) => {
                        cache.put(request, responseClone);
                    });
                    return response;
                })
                .catch(() => {
                    // Network failed, try cache
                    return caches.match(request);
                })
        );
    }
    // Static assets - Cache first, network fallback
    else {
        event.respondWith(
            caches.match(request).then((cachedResponse) => {
                if (cachedResponse) {
                    return cachedResponse;
                }
                return fetch(request).then((response) => {
                    // Don't cache non-successful responses
                    if (!response || response.status !== 200) {
                        return response;
                    }
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then((cache) => {
                        cache.put(request, responseClone);
                    });
                    return response;
                });
            })
        );
    }
});

// Background sync for offline changes
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-offline-changes') {
        event.waitUntil(syncOfflineChanges());
    }
});

async function syncOfflineChanges() {
    // Get pending changes from IndexedDB
    const db = await openDB();
    const tx = db.transaction('pending_changes', 'readonly');
    const store = tx.objectStore('pending_changes');
    const changes = await store.getAll();

    // Sync each change
    for (const change of changes) {
        try {
            await fetch(change.url, {
                method: change.method,
                headers: change.headers,
                body: JSON.stringify(change.data)
            });

            // Remove from pending after successful sync
            const deleteTx = db.transaction('pending_changes', 'readwrite');
            await deleteTx.objectStore('pending_changes').delete(change.id);
        } catch (error) {
            console.error('Sync failed for:', change, error);
        }
    }
}

function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('AngelsAI', 1);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(request.result);

        request.onupgradeneeded = (event) => {
            const db = event.target.result;
            if (!db.objectStoreNames.contains('pending_changes')) {
                db.createObjectStore('pending_changes', { keyPath: 'id', autoIncrement: true });
            }
        };
    });
}
