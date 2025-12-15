// Offline Sync Manager for TopStyle Business Management System
// Handles syncing of offline operations when connection is restored

class OfflineSyncManager {
    constructor() {
        this.syncInProgress = false;
        this.syncInterval = null;
        this.retryCount = 0;
        this.maxRetries = 3;
        this.init();
    }

    async init() {
        // Listen for online/offline events
        window.addEventListener('online', () => this.handleOnline());
        window.addEventListener('offline', () => this.handleOffline());

        // Register background sync if available
        if ('serviceWorker' in navigator && 'sync' in window.ServiceWorkerRegistration.prototype) {
            this.registerBackgroundSync();
        }

        // Start periodic sync check if online
        if (navigator.onLine) {
            this.startPeriodicSync();
        }

        // Listen for service worker messages
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.addEventListener('message', (event) => {
                if (event.data && event.data.type === 'SYNC_OFFLINE_DATA') {
                    this.syncAllOfflineData();
                }
            });
        }
    }

    async handleOnline() {
        console.log('[OfflineSync] Connection restored');
        this.showNotification('Connection restored. Syncing offline data...', 'success');
        
        // Start syncing immediately
        await this.syncAllOfflineData();
        
        // Start periodic sync
        this.startPeriodicSync();
    }

    handleOffline() {
        console.log('[OfflineSync] Connection lost');
        this.showNotification('You are now offline. Changes will sync when connection is restored.', 'warning');
        
        // Stop periodic sync
        this.stopPeriodicSync();
    }

    async syncAllOfflineData() {
        if (this.syncInProgress) {
            console.log('[OfflineSync] Sync already in progress');
            return;
        }

        if (!navigator.onLine) {
            console.log('[OfflineSync] Cannot sync - offline');
            return;
        }

        this.syncInProgress = true;
        console.log('[OfflineSync] Starting sync...');

        try {
            // Sync queued forms first
            await this.syncQueuedForms();
            
            // Sync offline orders
            await this.syncOfflineOrders();
            
            // Sync offline customers
            await this.syncOfflineCustomers();
            
            // Sync offline products
            await this.syncOfflineProducts();
            
            console.log('[OfflineSync] Sync completed successfully');
            this.retryCount = 0;
            this.showNotification('All offline data has been synced successfully!', 'success');
        } catch (error) {
            console.error('[OfflineSync] Sync error:', error);
            this.retryCount++;
            
            if (this.retryCount < this.maxRetries) {
                console.log(`[OfflineSync] Retrying sync (${this.retryCount}/${this.maxRetries})...`);
                setTimeout(() => this.syncAllOfflineData(), 5000);
            } else {
                this.showNotification('Some data failed to sync. It will retry automatically.', 'warning');
            }
        } finally {
            this.syncInProgress = false;
        }
    }

    async syncQueuedForms() {
        if (!window.offlineDB) {
            console.warn('[OfflineSync] offlineDB not available');
            return;
        }

        const queuedForms = await window.offlineDB.getQueuedForms();
        console.log(`[OfflineSync] Syncing ${queuedForms.length} queued forms`);

        for (const form of queuedForms) {
            try {
                const response = await fetch(form.url, {
                    method: form.method || 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken(),
                    },
                    body: JSON.stringify(form.data),
                });

                if (response.ok) {
                    await window.offlineDB.markFormSynced(form.id);
                    console.log(`[OfflineSync] Form synced: ${form.url}`);
                } else {
                    throw new Error(`HTTP ${response.status}`);
                }
            } catch (error) {
                console.error(`[OfflineSync] Failed to sync form ${form.id}:`, error);
                // Mark for retry
                form.retries = (form.retries || 0) + 1;
                if (form.retries >= this.maxRetries) {
                    // Move to failed queue or notify user
                    console.error(`[OfflineSync] Form ${form.id} exceeded max retries`);
                } else {
                    await window.offlineDB.save('form_queue', form);
                }
            }
        }
    }

    async syncOfflineOrders() {
        if (!window.offlineDB) return;

        const pendingOrders = await window.offlineDB.getPendingOrders();
        console.log(`[OfflineSync] Syncing ${pendingOrders.length} offline orders`);

        for (const order of pendingOrders) {
            try {
                const response = await fetch('/api/orders/create/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken(),
                    },
                    body: JSON.stringify(order),
                });

                if (response.ok) {
                    const result = await response.json();
                    await window.offlineDB.updateSyncStatus('orders', order.id, 'synced');
                    console.log(`[OfflineSync] Order synced: ${order.order_identifier}`);
                } else {
                    throw new Error(`HTTP ${response.status}`);
                }
            } catch (error) {
                console.error(`[OfflineSync] Failed to sync order ${order.id}:`, error);
            }
        }
    }

    async syncOfflineCustomers() {
        if (!window.offlineDB) return;

        const pendingCustomers = await window.offlineDB.getPendingCustomers();
        console.log(`[OfflineSync] Syncing ${pendingCustomers.length} offline customers`);

        for (const customer of pendingCustomers) {
            try {
                const response = await fetch('/api/customers/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken(),
                    },
                    body: JSON.stringify(customer),
                });

                if (response.ok) {
                    await window.offlineDB.updateSyncStatus('customers', customer.id, 'synced');
                    console.log(`[OfflineSync] Customer synced: ${customer.name}`);
                } else {
                    throw new Error(`HTTP ${response.status}`);
                }
            } catch (error) {
                console.error(`[OfflineSync] Failed to sync customer ${customer.id}:`, error);
            }
        }
    }

    async syncOfflineProducts() {
        if (!window.offlineDB) return;

        const pendingProducts = await window.offlineDB.getAll('products');
        const filtered = pendingProducts.filter(p => p.sync_status === 'pending');
        console.log(`[OfflineSync] Syncing ${filtered.length} offline products`);

        for (const product of filtered) {
            try {
                const response = await fetch('/api/products/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken(),
                    },
                    body: JSON.stringify(product),
                });

                if (response.ok) {
                    await window.offlineDB.updateSyncStatus('products', product.id, 'synced');
                    console.log(`[OfflineSync] Product synced: ${product.name}`);
                } else {
                    throw new Error(`HTTP ${response.status}`);
                }
            } catch (error) {
                console.error(`[OfflineSync] Failed to sync product ${product.id}:`, error);
            }
        }
    }

    registerBackgroundSync() {
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.ready.then(registration => {
                registration.sync.register('sync-offline-data').catch(err => {
                    console.log('[OfflineSync] Background sync registration failed:', err);
                });
            });
        }
    }

    startPeriodicSync() {
        // Sync every 30 seconds when online
        this.stopPeriodicSync();
        this.syncInterval = setInterval(() => {
            if (navigator.onLine && !this.syncInProgress) {
                this.syncAllOfflineData();
            }
        }, 30000);
    }

    stopPeriodicSync() {
        if (this.syncInterval) {
            clearInterval(this.syncInterval);
            this.syncInterval = null;
        }
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'success' ? 'success' : type === 'warning' ? 'warning' : 'info'} alert-dismissible fade show position-fixed`;
        notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        notification.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(notification);

        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.classList.remove('show');
                setTimeout(() => notification.remove(), 150);
            }
        }, 5000);
    }

    // Manual sync trigger
    async manualSync() {
        if (!navigator.onLine) {
            this.showNotification('Cannot sync while offline', 'warning');
            return;
        }
        await this.syncAllOfflineData();
    }
}

// Create global instance
if (typeof window !== 'undefined') {
    window.offlineSyncManager = new OfflineSyncManager();
}


