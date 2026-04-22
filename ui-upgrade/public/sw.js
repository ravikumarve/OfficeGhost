// GhostOffice Service Worker
// Provides offline capability and caching

const CACHE_NAME = 'ghostoffice-v1';
const STATIC_CACHE = 'ghostoffice-static-v1';
const API_CACHE = 'ghostoffice-api-v1';

// Assets to cache on install
const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/icon-192.png',
  '/icon-512.png'
];

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Installing...');
  
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        console.log('[Service Worker] Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        return self.skipWaiting();
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((cacheName) => {
              return cacheName !== STATIC_CACHE && 
                     cacheName !== API_CACHE;
            })
            .map((cacheName) => {
              console.log('[Service Worker] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            })
        );
      })
      .then(() => {
        return self.clients.claim();
      })
  );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  // Handle API requests
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      caches.open(API_CACHE)
        .then((cache) => {
          return cache.match(event.request)
            .then((response) => {
              if (response) {
                // Return cached response if available
                return response;
              }
              
              // Otherwise fetch from network
              return fetch(event.request)
                .then((networkResponse) => {
                  // Cache the response
                  cache.put(event.request, networkResponse.clone());
                  return networkResponse;
                })
                .catch((error) => {
                  console.error('[Service Worker] API fetch failed:', error);
                  // Return a cached response if available, or an error response
                  return cache.match(event.request) || new Response(
                    JSON.stringify({ error: 'Offline - API unavailable' }),
                    { 
                      status: 503,
                      headers: { 'Content-Type': 'application/json' }
                    }
                  );
                });
            });
        })
    );
    return;
  }
  
  // Handle static assets
  event.respondWith(
    caches.open(STATIC_CACHE)
      .then((cache) => {
        return cache.match(event.request)
          .then((response) => {
            if (response) {
              return response;
            }
            
            return fetch(event.request)
              .then((networkResponse) => {
                // Cache successful responses
                if (networkResponse.status === 200) {
                  cache.put(event.request, networkResponse.clone());
                }
                return networkResponse;
              })
              .catch(() => {
                // Return offline page for HTML requests
                if (event.request.headers.get('accept')?.includes('text/html')) {
                  return cache.match('/') || new Response(
                    '<h1>GhostOffice - Offline</h1><p>You are currently offline. Please check your internet connection.</p>',
                    { 
                      status: 503,
                      headers: { 'Content-Type': 'text/html' }
                    }
                  );
                }
              });
          });
      })
  );
});

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('[Service Worker] Background sync:', event.tag);
  
  if (event.tag === 'sync-emails') {
    event.waitUntil(
      // Sync emails when back online
      fetch('/api/emails/sync', { method: 'POST' })
        .then(() => {
          console.log('[Service Worker] Email sync completed');
        })
        .catch((error) => {
          console.error('[Service Worker] Email sync failed:', error);
        })
    );
  }
});

// Push notifications
self.addEventListener('push', (event) => {
  console.log('[Service Worker] Push received');
  
  const options = {
    body: event.data ? event.data.text() : 'New notification from GhostOffice',
    icon: '/icon-192.png',
    badge: '/icon-192.png',
    vibrate: [200, 100, 200],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Open GhostOffice',
        icon: '/icon-192.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('GhostOffice', options)
  );
});

// Notification click handler
self.addEventListener('notificationclick', (event) => {
  console.log('[Service Worker] Notification click received');
  
  event.notification.close();
  
  event.waitUntil(
    clients.openWindow('/')
  );
});
