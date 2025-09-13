// Service Worker for TopStyle Business Management System
const CACHE_NAME = 'topstyle-business-v3';
const STATIC_CACHE = 'topstyle-static-v3';
const DYNAMIC_CACHE = 'topstyle-dynamic-v3';

const urlsToCache = [
    '/',
    '/static/js/sw.js',
    '/static/manifest.json',
    '/static/favicon.ico',
    '/static/images/icon-72x72.png',
    '/static/images/icon-96x96.png',
    '/static/images/icon-128x128.png',
    '/static/images/icon-144x144.png',
    '/static/images/icon-152x152.png',
    '/static/images/icon-192x192.png',
    '/static/images/icon-384x384.png',
    '/static/images/icon-512x512.png',
    '/login/',
    '/dashboard/',
    '/orders/',
    '/inventory/',
    '/sales/',
    '/track/',
    '/orders/create/',
    '/payment/method/',
    '/payment/process/',
    '/orders/receipt/',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://cdn.jsdelivr.net/npm/chart.js',
    'https://cdn.jsdelivr.net/npm/qrcode@1.5.3/build/qrcode.min.js',
    'https://unpkg.com/html5-qrcode'
];

// Install event
self.addEventListener('install', function(event) {
    console.log('Service Worker installing...');
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(function(cache) {
                console.log('Static cache opened');
                return cache.addAll(urlsToCache);
            })
            .then(() => {
                console.log('Service Worker installed successfully');
                return self.skipWaiting();
            })
            .catch(function(error) {
                console.error('Service Worker installation failed:', error);
            })
    );
});

// Activate event
self.addEventListener('activate', function(event) {
    console.log('Service Worker activating...');
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => {
            console.log('Service Worker activated');
            return self.clients.claim();
        })
    );
});

// Fetch event with enhanced caching strategy
self.addEventListener('fetch', function(event) {
    const request = event.request;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Skip Chrome extension requests
    if (url.protocol === 'chrome-extension:') {
        return;
    }
    
    event.respondWith(
        caches.match(request)
            .then(function(response) {
                // Return cached version if available
                if (response) {
                    console.log('Serving from cache:', request.url);
                    return response;
                }
                
                // Fetch from network
                return fetch(request)
                    .then(function(response) {
                        // Don't cache non-successful responses
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }
                        
                        // Clone the response
                        const responseToCache = response.clone();
                        
                        // Cache dynamic content
                        caches.open(DYNAMIC_CACHE)
                            .then(function(cache) {
                                cache.put(request, responseToCache);
                            });
                        
                        return response;
                    })
                    .catch(function(error) {
                        console.error('Fetch failed:', error);
                        
                        // Return offline page for navigation requests
                        if (request.mode === 'navigate') {
                            return caches.match('/offline/') || new Response(
                                '<html><body><h1>Offline</h1><p>Please check your internet connection.</p></body></html>',
                                { headers: { 'Content-Type': 'text/html' } }
                            );
                        }
                        
                        throw error;
                    });
            })
    );
});

// Background sync for offline data
self.addEventListener('sync', function(event) {
    if (event.tag === 'background-sync') {
        console.log('Background sync triggered');
        event.waitUntil(doBackgroundSync());
    }
});

// Push notifications
self.addEventListener('push', function(event) {
    console.log('Push notification received');
    
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
    console.log('Notification clicked:', event.action);
    
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/dashboard/')
        );
    }
});

// Helper function for background sync
function doBackgroundSync() {
    return new Promise(function(resolve, reject) {
        // Implement background sync logic here
        console.log('Performing background sync...');
        resolve();
    });
}

