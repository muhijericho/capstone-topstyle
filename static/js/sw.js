// Enhanced Service Worker for TopStyle Business Management System
// Version: 4.0 - Full Offline Support

const CACHE_VERSION = 'topstyle-offline-v4';
const STATIC_CACHE = 'topstyle-static-v4';
const DYNAMIC_CACHE = 'topstyle-dynamic-v4';
const API_CACHE = 'topstyle-api-v4';
const IMAGES_CACHE = 'topstyle-images-v4';

// Static assets to cache on install
const STATIC_ASSETS = [
    '/',
    '/static/manifest.json',
    '/static/favicon.ico',
    '/static/js/offline.js',
    '/static/js/offline-db.js',
    '/static/js/offline-sync.js',
    '/static/js/notifications.js',
    '/static/js/auto-save-service.js',
    '/static/images/icon-72x72.png',
    '/static/images/icon-96x96.png',
    '/static/images/icon-128x128.png',
    '/static/images/icon-144x144.png',
    '/static/images/icon-152x152.png',
    '/static/images/icon-192x192.png',
    '/static/images/icon-384x384.png',
    '/static/images/icon-512x512.png',
];

// External CDN resources
const CDN_RESOURCES = [
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://cdn.jsdelivr.net/npm/chart.js',
    'https://cdn.jsdelivr.net/npm/qrcode@1.5.3/build/qrcode.min.js',
    'https://unpkg.com/html5-qrcode',
];

// Pages to cache (navigation requests)
const PAGES_TO_CACHE = [
    '/login/',
    '/dashboard/',
    '/orders/',
    '/inventory/',
    '/customers/',
    '/sales/',
    '/track/',
    '/orders/create/',
    '/offline/',
];

// Install event - Cache static assets
self.addEventListener('install', function(event) {
    console.log('[SW] Installing service worker v4...');
    event.waitUntil(
        Promise.all([
            caches.open(STATIC_CACHE).then(cache => {
                console.log('[SW] Caching static assets');
                return cache.addAll(STATIC_ASSETS.map(url => new Request(url, {cache: 'reload'})));
            }).catch(err => {
                console.error('[SW] Failed to cache static assets:', err);
            }),
            caches.open(STATIC_CACHE).then(cache => {
                console.log('[SW] Caching CDN resources');
                return cache.addAll(CDN_RESOURCES);
            }).catch(err => {
                console.warn('[SW] Some CDN resources failed to cache:', err);
            }),
            // Cache important pages for offline access
            caches.open(DYNAMIC_CACHE).then(cache => {
                console.log('[SW] Pre-caching important pages');
                return cache.addAll(PAGES_TO_CACHE).catch(err => {
                    console.warn('[SW] Some pages failed to cache:', err);
                });
            })
        ]).then(() => {
            console.log('[SW] Service worker installed successfully');
            return self.skipWaiting();
        })
    );
});

// Activate event - Clean up old caches
self.addEventListener('activate', function(event) {
    console.log('[SW] Activating service worker v4...');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== STATIC_CACHE && 
                        cacheName !== DYNAMIC_CACHE && 
                        cacheName !== API_CACHE &&
                        cacheName !== IMAGES_CACHE &&
                        cacheName.startsWith('topstyle-')) {
                        console.log('[SW] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            console.log('[SW] Service worker activated');
            return self.clients.claim();
        })
    );
});

// Fetch event - Comprehensive caching strategy with offline support
self.addEventListener('fetch', function(event) {
    const { request } = event;
    const url = new URL(request.url);

    // Skip chrome-extension and other non-http requests
    if (!url.protocol.startsWith('http')) {
        return;
    }

    // Skip admin and authentication endpoints (but allow logout for offline)
    if (url.pathname.startsWith('/admin/') || 
        url.pathname.includes('/api/auth/')) {
        return;
    }

    // Handle POST/PUT/DELETE requests offline
    if (request.method !== 'GET' && request.method !== 'HEAD') {
        event.respondWith(handleOfflinePostRequest(request, url));
        return;
    }

    event.respondWith(
        handleRequest(request, url)
    );
});

// Main request handler with caching strategies
async function handleRequest(request, url) {
    // Strategy 1: Static assets - Cache First
    if (isStaticAsset(url.pathname)) {
        return cacheFirst(request, STATIC_CACHE);
    }

    // Strategy 2: Images - Cache First with Network Fallback
    if (isImage(url.pathname)) {
        return cacheFirst(request, IMAGES_CACHE);
    }

    // Strategy 3: API endpoints - Network First with Cache Fallback
    if (url.pathname.startsWith('/api/')) {
        return networkFirst(request, API_CACHE);
    }

    // Strategy 4: HTML pages - Network First with Cache Fallback
    if (request.mode === 'navigate' || request.headers.get('accept').includes('text/html')) {
        return networkFirst(request, DYNAMIC_CACHE, true);
    }

    // Strategy 5: Everything else - Stale While Revalidate
    return staleWhileRevalidate(request, DYNAMIC_CACHE);
}

// Check if request is for static asset
function isStaticAsset(pathname) {
    return pathname.startsWith('/static/') || 
           pathname === '/' ||
           pathname === '/favicon.ico' ||
           pathname === '/manifest.json';
}

// Check if request is for image
function isImage(pathname) {
    return /\.(jpg|jpeg|png|gif|webp|svg|ico)$/i.test(pathname);
}

// Cache First Strategy - Check cache first, fallback to network
async function cacheFirst(request, cacheName) {
    try {
        const cached = await caches.match(request);
        if (cached) {
            return cached;
        }

        const response = await fetch(request);
        if (response.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, response.clone());
        }
        return response;
    } catch (error) {
        console.error('[SW] Cache first failed:', error);
        // Return offline fallback if it's an HTML request
        if (request.mode === 'navigate') {
            return getOfflinePage();
        }
        throw error;
    }
}

// Network First Strategy - Try network first, fallback to cache
async function networkFirst(request, cacheName, isHTML = false) {
    try {
        const response = await fetch(request);
        
        // Cache successful responses
        if (response.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, response.clone());
        }
        
        return response;
    } catch (error) {
        console.log('[SW] Network request failed, trying cache:', request.url);
        
        // Try to get from cache
        const cached = await caches.match(request);
        if (cached) {
            return cached;
        }

        // If it's an HTML request and we don't have it cached, try to return offline page
        if (isHTML) {
            const offlinePage = await getOfflinePage();
            if (offlinePage) {
                return offlinePage;
            }
        }

        // For API requests, return a JSON response indicating offline
        if (request.url.includes('/api/')) {
            return new Response(JSON.stringify({
                success: false,
                offline: true,
                message: 'You are currently offline. Data will sync when connection is restored.',
                cached: false
            }), {
                headers: { 'Content-Type': 'application/json' }
            });
        }

        throw error;
    }
}

// Stale While Revalidate - Return cache immediately, update in background
async function staleWhileRevalidate(request, cacheName) {
    const cache = await caches.open(cacheName);
    const cached = await cache.match(request);

    // Fetch in background to update cache
    const fetchPromise = fetch(request).then(response => {
        if (response.ok) {
            cache.put(request, response.clone());
        }
        return response;
    }).catch(() => {
        // Network failed, but we already have cached version
    });

    // Return cached version immediately, or wait for network if no cache
    return cached || fetchPromise;
}

// Get offline fallback page
async function getOfflinePage() {
    try {
        // Try dynamic cache first
        const dynamicCache = await caches.open(DYNAMIC_CACHE);
        let offlinePage = await dynamicCache.match('/offline/');
        if (offlinePage) {
            return offlinePage;
        }
        
        // Try static cache
        const staticCache = await caches.open(STATIC_CACHE);
        offlinePage = await staticCache.match('/offline/');
        if (offlinePage) {
            return offlinePage;
        }
        
        // Try to fetch and cache offline page (ignore network errors in service worker)
        try {
            const response = await fetch('/offline/');
            if (response.ok) {
                dynamicCache.put('/offline/', response.clone());
                return response;
            }
        } catch (err) {
            // Network failed, continue to fallback
            console.warn('[SW] Failed to fetch offline page:', err);
        }
    } catch (error) {
        console.error('[SW] Failed to get offline page from cache:', error);
    }

    // Return a basic offline HTML if cached version not available
    return new Response(`
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Offline - TopStyle</title>
            <style>
                body {
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    min-height: 100vh;
                    margin: 0;
                    background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
                    color: white;
                    text-align: center;
                    padding: 20px;
                }
                .offline-container {
                    max-width: 500px;
                }
                h1 { font-size: 2.5em; margin-bottom: 20px; }
                p { font-size: 1.2em; margin-bottom: 30px; opacity: 0.9; }
                .icon { font-size: 5em; margin-bottom: 20px; }
                button {
                    background: white;
                    color: #1e3a8a;
                    border: none;
                    padding: 15px 30px;
                    font-size: 1.1em;
                    border-radius: 8px;
                    cursor: pointer;
                    font-weight: bold;
                }
                button:hover { opacity: 0.9; }
            </style>
        </head>
        <body>
            <div class="offline-container">
                <div class="icon">📡</div>
                <h1>You're Offline</h1>
                <p>Please check your internet connection. You can still use the app with cached data.</p>
                <button onclick="window.location.reload()">Try Again</button>
            </div>
        </body>
        </html>
    `, {
        headers: { 'Content-Type': 'text/html' }
    });
}

// Background Sync - Sync data when connection is restored
self.addEventListener('sync', function(event) {
    console.log('[SW] Background sync triggered:', event.tag);
    
    if (event.tag === 'sync-offline-data') {
        event.waitUntil(syncOfflineData());
    } else if (event.tag === 'sync-forms') {
        event.waitUntil(syncOfflineForms());
    }
});

// Sync offline data from IndexedDB
async function syncOfflineData() {
    try {
        // Send message to clients to trigger sync
        const clients = await self.clients.matchAll();
        clients.forEach(client => {
            client.postMessage({
                type: 'SYNC_OFFLINE_DATA',
                action: 'start'
            });
        });
        console.log('[SW] Background sync initiated');
    } catch (error) {
        console.error('[SW] Background sync failed:', error);
    }
}

// Sync offline form submissions
async function syncOfflineForms() {
    try {
        const clients = await self.clients.matchAll();
        clients.forEach(client => {
            client.postMessage({
                type: 'SYNC_OFFLINE_FORMS',
                action: 'start'
            });
        });
        console.log('[SW] Form sync initiated');
    } catch (error) {
        console.error('[SW] Form sync failed:', error);
    }
}

// Push notifications
self.addEventListener('push', function(event) {
    console.log('[SW] Push notification received');
    
    const options = {
        body: event.data ? event.data.text() : 'New notification from TopStyle',
        icon: '/static/images/icon-192x192.png',
        badge: '/static/images/icon-72x72.png',
        vibrate: [200, 100, 200],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'Open App',
                icon: '/static/images/icon-96x96.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/images/icon-96x96.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('TopStyle Business', options)
    );
});

// Notification click handler
self.addEventListener('notificationclick', function(event) {
    console.log('[SW] Notification clicked:', event.action);
    
    event.notification.close();
    
    if (event.action === 'explore' || !event.action) {
        event.waitUntil(
            clients.openWindow('/dashboard/')
        );
    }
});

// Message handler for communication with clients
self.addEventListener('message', function(event) {
    console.log('[SW] Message received:', event.data);
    
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
    
    if (event.data && event.data.type === 'CACHE_URLS') {
        event.waitUntil(
            cacheUrls(event.data.urls)
        );
    }
});

// Cache specific URLs
async function cacheUrls(urls) {
    const cache = await caches.open(DYNAMIC_CACHE);
    try {
        await cache.addAll(urls);
        console.log('[SW] URLs cached successfully');
    } catch (error) {
        console.error('[SW] Failed to cache URLs:', error);
    }
}

// Handle POST/PUT/DELETE requests when offline
async function handleOfflinePostRequest(request, url) {
    try {
        // Try network first
        const response = await fetch(request);
        
        // If successful, cache the response (for idempotent operations)
        if (response.ok && request.method === 'GET') {
            const cache = await caches.open(API_CACHE);
            cache.put(request, response.clone());
        }
        
        return response;
    } catch (error) {
        // Network failed - queue request for later
        console.log('[SW] Network request failed, queueing for sync:', url.pathname);
        
        // Store request in IndexedDB via message to client
        const clients = await self.clients.matchAll();
        clients.forEach(client => {
            client.postMessage({
                type: 'QUEUE_OFFLINE_REQUEST',
                data: {
                    url: url.pathname,
                    method: request.method,
                    timestamp: new Date().toISOString()
                }
            });
        });

        // Return a response indicating the request was queued
        return new Response(JSON.stringify({
            success: false,
            queued: true,
            offline: true,
            message: 'Request queued for sync when connection is restored',
            url: url.pathname,
            method: request.method
        }), {
            status: 202,
            statusText: 'Accepted',
            headers: {
                'Content-Type': 'application/json',
            },
        });
    }
}
