// Offline functionality for TopStyle Business Management System

// Register service worker with enhanced offline support
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(function(registration) {
                console.log('[Offline] ServiceWorker registration successful:', registration.scope);
                
                // Check for service worker updates
                registration.addEventListener('updatefound', () => {
                    const newWorker = registration.installing;
                    newWorker.addEventListener('statechange', () => {
                        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
                            // New service worker available
                            console.log('[Offline] New service worker available');
                            if (confirm('New version available. Reload to update?')) {
                                window.location.reload();
                            }
                        }
                    });
                });
            })
            .catch(function(err) {
                console.error('[Offline] ServiceWorker registration failed:', err);
            });
    });
    
    // Listen for service worker messages
    navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data && event.data.type === 'QUEUE_OFFLINE_REQUEST') {
            // Handle queued requests from service worker
            if (window.offlineDB) {
                const data = event.data.data;
                window.offlineDB.queueForm(data.url, data.method, data).catch(err => {
                    console.error('[Offline] Failed to queue request:', err);
                });
            }
        }
    });
}

// Offline detection
function updateOnlineStatus() {
    const status = document.getElementById('connection-status');
    if (navigator.onLine) {
        if (status) {
            status.innerHTML = '<i class="fas fa-wifi text-success"></i> Online';
            status.className = 'badge bg-success';
        }
    } else {
        if (status) {
            status.innerHTML = '<i class="fas fa-wifi-slash text-warning"></i> Offline';
            status.className = 'badge bg-warning';
        }
        showOfflineMessage();
    }
}

// Show offline message
function showOfflineMessage() {
    const message = document.createElement('div');
    message.className = 'alert alert-warning alert-dismissible fade show position-fixed';
    message.style.top = '20px';
    message.style.right = '20px';
    message.style.zIndex = '9999';
    message.innerHTML = `
        <i class="fas fa-wifi-slash me-2"></i>
        You are currently offline. Some features may be limited.
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(message);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (message.parentNode) {
            message.parentNode.removeChild(message);
        }
    }, 5000);
}

// Cache form data for offline use
function cacheFormData(formId, data) {
    if ('localStorage' in window) {
        localStorage.setItem(`form_${formId}`, JSON.stringify(data));
    }
}

// Retrieve cached form data
function getCachedFormData(formId) {
    if ('localStorage' in window) {
        const data = localStorage.getItem(`form_${formId}`);
        return data ? JSON.parse(data) : null;
    }
    return null;
}

// Clear cached form data
function clearCachedFormData(formId) {
    if ('localStorage' in window) {
        localStorage.removeItem(`form_${formId}`);
    }
}

// Initialize offline functionality
document.addEventListener('DOMContentLoaded', async function() {
    // Initialize IndexedDB
    if (window.offlineDB) {
        try {
            await window.offlineDB.init();
            console.log('[Offline] IndexedDB initialized');
        } catch (error) {
            console.error('[Offline] IndexedDB initialization failed:', error);
        }
    }
    
    // Add connection status indicator
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        const statusDiv = document.createElement('div');
        statusDiv.id = 'connection-status';
        statusDiv.className = 'badge bg-success';
        statusDiv.style.cssText = 'margin-left: 10px; cursor: pointer;';
        statusDiv.innerHTML = '<i class="fas fa-wifi text-success"></i> Online';
        statusDiv.title = 'Click to manually sync offline data';
        statusDiv.addEventListener('click', () => {
            if (window.offlineSyncManager && navigator.onLine) {
                window.offlineSyncManager.manualSync();
            }
        });
        navbar.appendChild(statusDiv);
    }
    
    // Listen for online/offline events
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    
    // Initial status check
    updateOnlineStatus();
    
    // Enhanced form submission handling for offline
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', async function(e) {
            if (!navigator.onLine) {
                e.preventDefault();
                
                // Create FormData and convert to object
                const formData = new FormData(form);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    // Handle multiple values for same key
                    if (data[key]) {
                        if (Array.isArray(data[key])) {
                            data[key].push(value);
                        } else {
                            data[key] = [data[key], value];
                        }
                    } else {
                        data[key] = value;
                    }
                }
                
                // Get form action URL
                const formUrl = form.action || window.location.pathname;
                
                // Queue form for offline sync
                if (window.offlineDB) {
                    await window.offlineDB.queueForm(formUrl, form.method || 'POST', data);
                    
                    // Show notification
                    showOfflineFormNotification('Form data saved. It will be submitted when you come back online.');
                    
                    // Optional: Clear form
                    if (form.dataset.clearOnOffline !== 'false') {
                        form.reset();
                    }
                } else {
                    // Fallback to localStorage
                    cacheFormData(form.id || 'default', data);
                    alert('Form data saved for when you come back online.');
                }
            }
        });
    });
    
    // Pre-cache important pages on load
    if (navigator.onLine && 'serviceWorker' in navigator) {
        cacheImportantPages();
    }
});

// Cache important pages for offline access
async function cacheImportantPages() {
    const importantPages = [
        '/dashboard/',
        '/orders/',
        '/inventory/',
        '/customers/',
        '/sales/',
        '/track/',
    ];
    
    if ('caches' in window) {
        const cache = await caches.open('topstyle-dynamic-v4');
        // Use bound fetch to avoid "Illegal invocation" error
        // Prefer the globally stored bound fetch, fallback to window.fetch bound
        const fetchToUse = window._boundFetch || (window.fetch && window.fetch.bind ? window.fetch.bind(window) : window.fetch);
        
        importantPages.forEach(url => {
            fetchToUse(url).then(response => {
                if (response.ok) {
                    cache.put(url, response);
                }
            }).catch(err => {
                console.warn(`[Offline] Failed to cache ${url}:`, err);
            });
        });
    }
}

// Show offline form notification
function showOfflineFormNotification(message) {
    const notification = document.createElement('div');
    notification.className = 'alert alert-info alert-dismissible fade show position-fixed';
    notification.style.cssText = 'top: 80px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        <i class="fas fa-info-circle me-2"></i>${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(notification);
    
    setTimeout(() => {
        if (notification.parentNode) {
            notification.classList.remove('show');
            setTimeout(() => notification.remove(), 150);
        }
    }, 5000);
}

