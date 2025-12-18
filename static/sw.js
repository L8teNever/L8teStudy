const CACHE_NAME = 'l8testudy-v1';
const ASSETS_TO_CACHE = [
    '/',
    'https://unpkg.com/lucide@latest'
];

self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
});

self.addEventListener('fetch', (event) => {
    // For navigation requests (HTML), try network first, then cache
    if (event.request.mode === 'navigate') {
        event.respondWith(
            fetch(event.request).catch(() => {
                return caches.match('/');
            })
        );
        return;
    }

    // API Caching Strategy (Network First, then Cache)
    if (event.request.url.includes('/api/') && event.request.method === 'GET') {
        event.respondWith(
            fetch(event.request)
                .then((response) => {
                    // Check if we received a valid response
                    if (!response || response.status !== 200 || response.type !== 'basic') {
                        return response;
                    }

                    // Clone the response
                    const responseToCache = response.clone();

                    caches.open(CACHE_NAME)
                        .then((cache) => {
                            cache.put(event.request, responseToCache);
                        });

                    return response;
                })
                .catch(() => {
                    return caches.match(event.request);
                })
        );
        return;
    }

    // Ignore non-GET requests for the fallback (let network handle POST/PUT/DELETE)
    if (event.request.method !== 'GET') {
        return;
    }

    // Static Assets (Cache First)
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request).catch(err => {
                console.warn('[SW] Fetch failed for:', event.request.url, err);
                return new Response('Offline oder Verbindungsfehler', {
                    status: 503,
                    headers: { 'Content-Type': 'text/plain' }
                });
            });
        })
    );
});

self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keyList) => {
            return Promise.all(keyList.map((key) => {
                if (key !== CACHE_NAME) {
                    return caches.delete(key);
                }
            }));
        })
    );
});

