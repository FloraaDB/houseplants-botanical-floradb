const CACHE_NAME = 'floradb-public-cache-v2026.07.1';
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/favicon.svg',
  '/og-image.png',
  '/samples/floradb_sample.csv',
  '/sitemap.xml',
  '/site.webmanifest'
];

// Install Event — Cache core static assets
self.addEventListener('install', (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(STATIC_ASSETS);
    }).catch((err) => {
      console.warn('PWA sw install cache error:', err);
    })
  );
});

// Activate Event — Clean up outdated caches
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Deleting outdated FloraDB cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Event — Stale-While-Revalidate Strategy with strict CORS/FormSubmit bypass
self.addEventListener('fetch', (event) => {
  // 1. Explicitly bypass non-GET requests (e.g. form API POSTs, OPTIONS preflight)
  if (event.request.method !== 'GET') {
    return;
  }

  // 2. Explicitly bypass cross-origin endpoints (e.g., FormSubmit, Kaggle, iNaturalist image S3 buckets, analytics)
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  // 3. Stale-While-Revalidate for local same-origin GET requests
  event.respondWith(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.match(event.request).then((cachedResponse) => {
        const fetchPromise = fetch(event.request)
          .then((networkResponse) => {
            // Check if network response is valid before caching
            if (networkResponse && networkResponse.status === 200 && networkResponse.type === 'basic') {
              cache.put(event.request, networkResponse.clone());
            }
            return networkResponse;
          })
          .catch((err) => {
            console.warn('Network fetch failed offline, using cached response if available:', event.request.url);
            return cachedResponse;
          });

        return cachedResponse || fetchPromise;
      });
    })
  );
});
