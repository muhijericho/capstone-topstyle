// Offline API Interceptor
// Intercepts API calls and handles them offline when needed

class OfflineAPI {
    constructor() {
        // Store original fetch BEFORE overriding it
        // Use a direct reference to the native fetch to avoid binding issues
        if (typeof window.fetch === 'function') {
            // Store the native fetch function
            this.originalFetch = window.fetch;
            // Create a bound version for safety
            this.boundFetch = window.fetch.bind(window);
            // Also store globally for access from other scripts
            if (!window._originalFetch) {
                window._originalFetch = window.fetch;
                window._boundFetch = window.fetch.bind(window);
            }
        } else {
            console.error('[OfflineAPI] window.fetch is not available!');
        }
        this.init();
    }

    init() {
        // Override fetch to intercept API calls
        const self = this;
        window.fetch = async function(...args) {
            return self.interceptFetch(...args);
        };

        console.log('[OfflineAPI] API interceptor initialized');
        console.log('[OfflineAPI] Original fetch stored:', typeof this.originalFetch);
    }

    async interceptFetch(url, options = {}) {
        // Critical endpoints that should always go through (bypass offline handling)
        const criticalEndpoints = [
            '/staff/add/',
            '/staff/',
            '/login/',
            '/logout/',
            '/api/autosave/',
            '/api/send-sms/',       // ensure CSRF/cookies preserved for SMS
        ];
        
        // Check if this is a critical endpoint that should bypass offline handling
        const urlString = typeof url === 'string' ? url : (url?.url || String(url));
        const isCriticalEndpoint = criticalEndpoints.some(endpoint => urlString.includes(endpoint));
        
        // If it's a critical endpoint, bypass offline handling and go straight to network
        if (isCriticalEndpoint) {
            console.log('[OfflineAPI] Bypassing interceptor for critical endpoint:', urlString);
            try {
                // Use bound fetch for critical endpoints to ensure it works correctly
                const fetchToUse = this.boundFetch || this.originalFetch || window.fetch;
                console.log('[OfflineAPI] Using fetch type:', fetchToUse === this.boundFetch ? 'boundFetch' : 
                           fetchToUse === this.originalFetch ? 'originalFetch' : 'window.fetch');
                
                const response = await fetchToUse(url, options);
                console.log('[OfflineAPI] Critical endpoint response:', response.status, response.statusText);
                return response;
            } catch (error) {
                console.error('[OfflineAPI] Critical endpoint fetch failed:', error);
                console.error('[OfflineAPI] Error details:', {
                    message: error.message,
                    name: error.name,
                    stack: error.stack,
                    url: urlString,
                    method: options.method || 'GET',
                    online: navigator.onLine
                });
                throw error;
            }
        }
        
        const isAPIRequest = typeof url === 'string' && (url.startsWith('/api/') || url.includes('/api/'));
        const isPostRequest = options.method && ['POST', 'PUT', 'DELETE', 'PATCH'].includes(options.method.toUpperCase());

        // If it's an API request with POST/PUT/DELETE and we're offline, queue it
        if (isAPIRequest && isPostRequest && !navigator.onLine) {
            return this.handleOfflineRequest(url, options);
        }

        // If it's a GET API request and we're offline, try to use cache
        if (isAPIRequest && (!options.method || options.method.toUpperCase() === 'GET') && !navigator.onLine) {
            return this.handleOfflineGetRequest(url, options);
        }

        // Normal request - try network first
        try {
            // Use bound fetch to avoid "Illegal invocation" error
            const fetchToUse = this.boundFetch || this.originalFetch || window.fetch;
            const response = await fetchToUse(url, options);
            
            // Cache successful API GET responses for offline use
            if (isAPIRequest && response.ok && (!options.method || options.method.toUpperCase() === 'GET')) {
                this.cacheResponse(url, response).catch(err => {
                    console.warn('[OfflineAPI] Failed to cache response:', err);
                });
            }
            
            return response;
        } catch (error) {
            // Network failed, try cache for GET requests
            if (isAPIRequest && (!options.method || options.method.toUpperCase() === 'GET')) {
                return this.handleOfflineGetRequest(url, options);
            }
            throw error;
        }
    }

    async handleOfflineRequest(url, options) {
        console.log('[OfflineAPI] Queueing offline request:', url);

        // Store request in IndexedDB queue
        if (window.offlineDB) {
            try {
                // Parse body if it's a string or FormData
                let bodyData = options.body;
                if (bodyData instanceof FormData) {
                    // Convert FormData to object
                    bodyData = {};
                    for (let [key, value] of options.body.entries()) {
                        bodyData[key] = value;
                    }
                } else if (typeof bodyData === 'string') {
                    try {
                        bodyData = JSON.parse(bodyData);
                    } catch (e) {
                        // Keep as string if not JSON
                    }
                }

                const requestData = {
                    url: url,
                    method: options.method || 'POST',
                    headers: options.headers || {},
                    body: bodyData,
                    timestamp: new Date().toISOString(),
                };

                await window.offlineDB.queueForm(url, options.method || 'POST', requestData);

                console.log('[OfflineAPI] Request queued successfully:', url);

                // Return a response indicating the request was queued
                // For createOrder, make it look successful so the flow continues
                if (url.includes('/api/orders/') || url.includes('/api/autosave/') || url.includes('/api/orders/check-materials/')) {
                    return new Response(JSON.stringify({
                        success: true,
                        queued: true,
                        offline: true,
                        available: true, // For material checks, assume available offline
                        message: 'Request queued for sync when connection is restored',
                        timestamp: requestData.timestamp,
                    }), {
                        status: 202, // Accepted
                        statusText: 'Accepted',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    });
                }

                return new Response(JSON.stringify({
                    success: true,
                    queued: true,
                    offline: true,
                    message: 'Request queued for sync when connection is restored',
                    timestamp: requestData.timestamp,
                }), {
                    status: 202, // Accepted
                    statusText: 'Accepted',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                });
            } catch (error) {
                console.error('[OfflineAPI] Error queueing request:', error);
                // Continue with error response below
            }
        }

        // Fallback error if IndexedDB is not available
        return new Response(JSON.stringify({
            success: false,
            offline: true,
            error: 'Cannot queue request - offline storage unavailable',
        }), {
            status: 503, // Service Unavailable
            statusText: 'Service Unavailable',
            headers: {
                'Content-Type': 'application/json',
            },
        });
    }

    async handleOfflineGetRequest(url, options) {
        console.log('[OfflineAPI] Trying cached response for:', url);

        // Try to get from IndexedDB cache
        if (window.offlineDB) {
            const cached = await window.offlineDB.getCachedAPIResponse(url);
            if (cached) {
                console.log('[OfflineAPI] Returning cached response');
                return new Response(JSON.stringify(cached), {
                    status: 200,
                    statusText: 'OK',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Cached': 'true',
                    },
                });
            }
        }

        // Try service worker cache
        try {
            const cache = await caches.open('topstyle-api-v4');
            const cached = await cache.match(url);
            if (cached) {
                console.log('[OfflineAPI] Returning service worker cache');
                return cached;
            }
        } catch (error) {
            console.error('[OfflineAPI] Cache access error:', error);
        }

        // No cache available
        return new Response(JSON.stringify({
            success: false,
            offline: true,
            error: 'No cached data available for this request',
        }), {
            status: 503,
            statusText: 'Service Unavailable',
            headers: {
                'Content-Type': 'application/json',
            },
        });
    }

    // Cache API responses for offline use
    async cacheResponse(url, response) {
        if (window.offlineDB && response.ok) {
            try {
                const data = await response.clone().json();
                await window.offlineDB.cacheAPIResponse(url, data);
            } catch (error) {
                // Response might not be JSON
                console.warn('[OfflineAPI] Could not cache non-JSON response');
            }
        }
    }
}

// Initialize on load
if (typeof window !== 'undefined') {
    window.offlineAPI = new OfflineAPI();
}

