// IndexedDB Wrapper for Offline Data Storage
// TopStyle Business Management System

const DB_NAME = 'TopStyleOfflineDB';
const DB_VERSION = 1;

class OfflineDB {
    constructor() {
        this.db = null;
    }

    // Initialize database
    async init() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(DB_NAME, DB_VERSION);

            request.onerror = () => {
                console.error('[OfflineDB] Failed to open database');
                reject(request.error);
            };

            request.onsuccess = () => {
                this.db = request.result;
                console.log('[OfflineDB] Database opened successfully');
                resolve(this.db);
            };

            request.onupgradeneeded = (event) => {
                const db = event.target.result;

                // Object stores for different data types
                if (!db.objectStoreNames.contains('orders')) {
                    const ordersStore = db.createObjectStore('orders', { keyPath: 'id', autoIncrement: true });
                    ordersStore.createIndex('order_identifier', 'order_identifier', { unique: false });
                    ordersStore.createIndex('status', 'status', { unique: false });
                    ordersStore.createIndex('sync_status', 'sync_status', { unique: false });
                    ordersStore.createIndex('created_at', 'created_at', { unique: false });
                }

                if (!db.objectStoreNames.contains('customers')) {
                    const customersStore = db.createObjectStore('customers', { keyPath: 'id', autoIncrement: true });
                    customersStore.createIndex('phone', 'phone', { unique: false });
                    customersStore.createIndex('email', 'email', { unique: false });
                    customersStore.createIndex('sync_status', 'sync_status', { unique: false });
                }

                if (!db.objectStoreNames.contains('products')) {
                    const productsStore = db.createObjectStore('products', { keyPath: 'id', autoIncrement: true });
                    productsStore.createIndex('name', 'name', { unique: false });
                    productsStore.createIndex('product_type', 'product_type', { unique: false });
                    productsStore.createIndex('sync_status', 'sync_status', { unique: false });
                }

                if (!db.objectStoreNames.contains('inventory')) {
                    const inventoryStore = db.createObjectStore('inventory', { keyPath: 'id', autoIncrement: true });
                    inventoryStore.createIndex('product_id', 'product_id', { unique: false });
                    inventoryStore.createIndex('sync_status', 'sync_status', { unique: false });
                }

                if (!db.objectStoreNames.contains('form_queue')) {
                    const formStore = db.createObjectStore('form_queue', { keyPath: 'id', autoIncrement: true });
                    formStore.createIndex('url', 'url', { unique: false });
                    formStore.createIndex('timestamp', 'timestamp', { unique: false });
                    formStore.createIndex('sync_status', 'sync_status', { unique: false });
                }

                if (!db.objectStoreNames.contains('api_cache')) {
                    const apiStore = db.createObjectStore('api_cache', { keyPath: 'url' });
                    apiStore.createIndex('timestamp', 'timestamp', { unique: false });
                }

                console.log('[OfflineDB] Database structure created');
            };
        });
    }

    // Generic method to save data
    async save(storeName, data) {
        if (!this.db) await this.init();
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            
            // Add sync status if not present
            if (!data.sync_status) {
                data.sync_status = 'pending';
            }
            if (!data.timestamp) {
                data.timestamp = new Date().toISOString();
            }

            const request = store.put(data);

            request.onsuccess = () => {
                console.log(`[OfflineDB] Saved to ${storeName}:`, data);
                resolve(request.result);
            };

            request.onerror = () => {
                console.error(`[OfflineDB] Failed to save to ${storeName}:`, request.error);
                reject(request.error);
            };
        });
    }

    // Generic method to get all data
    async getAll(storeName, indexName = null, query = null) {
        if (!this.db) await this.init();
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const source = indexName ? store.index(indexName) : store;
            const request = query ? source.getAll(query) : source.getAll();

            request.onsuccess = () => {
                resolve(request.result || []);
            };

            request.onerror = () => {
                console.error(`[OfflineDB] Failed to get from ${storeName}:`, request.error);
                reject(request.error);
            };
        });
    }

    // Generic method to get single item
    async get(storeName, key) {
        if (!this.db) await this.init();
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.get(key);

            request.onsuccess = () => {
                resolve(request.result);
            };

            request.onerror = () => {
                console.error(`[OfflineDB] Failed to get from ${storeName}:`, request.error);
                reject(request.error);
            };
        });
    }

    // Generic method to delete
    async delete(storeName, key) {
        if (!this.db) await this.init();
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.delete(key);

            request.onsuccess = () => {
                console.log(`[OfflineDB] Deleted from ${storeName}:`, key);
                resolve();
            };

            request.onerror = () => {
                console.error(`[OfflineDB] Failed to delete from ${storeName}:`, request.error);
                reject(request.error);
            };
        });
    }

    // Order operations
    async saveOrder(order) {
        return this.save('orders', order);
    }

    async getAllOrders() {
        return this.getAll('orders');
    }

    async getOrder(id) {
        return this.get('orders', id);
    }

    async getPendingOrders() {
        const orders = await this.getAllOrders();
        return orders.filter(order => order.sync_status === 'pending');
    }

    // Customer operations
    async saveCustomer(customer) {
        return this.save('customers', customer);
    }

    async getAllCustomers() {
        return this.getAll('customers');
    }

    async getCustomer(id) {
        return this.get('customers', id);
    }

    async getPendingCustomers() {
        const customers = await this.getAllCustomers();
        return customers.filter(customer => customer.sync_status === 'pending');
    }

    // Product operations
    async saveProduct(product) {
        return this.save('products', product);
    }

    async getAllProducts() {
        return this.getAll('products');
    }

    async getProduct(id) {
        return this.get('products', id);
    }

    // Form queue operations (for offline form submissions)
    async queueForm(url, method, data) {
        const formData = {
            url: url,
            method: method,
            data: data,
            timestamp: new Date().toISOString(),
            sync_status: 'pending',
            retries: 0
        };
        return this.save('form_queue', formData);
    }

    async getQueuedForms() {
        const forms = await this.getAll('form_queue');
        return forms.filter(form => form.sync_status === 'pending').sort((a, b) => 
            new Date(a.timestamp) - new Date(b.timestamp)
        );
    }

    async markFormSynced(id) {
        const form = await this.get('form_queue', id);
        if (form) {
            form.sync_status = 'synced';
            return this.save('form_queue', form);
        }
    }

    async deleteForm(id) {
        return this.delete('form_queue', id);
    }

    // API cache operations
    async cacheAPIResponse(url, response) {
        const cacheData = {
            url: url,
            response: response,
            timestamp: new Date().toISOString()
        };
        return this.save('api_cache', cacheData);
    }

    async getCachedAPIResponse(url) {
        const cached = await this.get('api_cache', url);
        if (cached) {
            // Check if cache is older than 1 hour
            const cacheAge = Date.now() - new Date(cached.timestamp).getTime();
            if (cacheAge < 3600000) { // 1 hour
                return cached.response;
            } else {
                // Delete stale cache
                await this.delete('api_cache', url);
            }
        }
        return null;
    }

    // Update sync status
    async updateSyncStatus(storeName, id, status) {
        const item = await this.get(storeName, id);
        if (item) {
            item.sync_status = status;
            return this.save(storeName, item);
        }
    }

    // Clear all data (use with caution)
    async clear(storeName) {
        if (!this.db) await this.init();
        
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.clear();

            request.onsuccess = () => {
                console.log(`[OfflineDB] Cleared ${storeName}`);
                resolve();
            };

            request.onerror = () => {
                console.error(`[OfflineDB] Failed to clear ${storeName}:`, request.error);
                reject(request.error);
            };
        });
    }

    // Get database size (approximate)
    async getSize() {
        if (!this.db) await this.init();
        
        const stores = ['orders', 'customers', 'products', 'inventory', 'form_queue', 'api_cache'];
        let totalSize = 0;

        for (const storeName of stores) {
            const data = await this.getAll(storeName);
            totalSize += JSON.stringify(data).length;
        }

        return {
            bytes: totalSize,
            kb: (totalSize / 1024).toFixed(2),
            mb: (totalSize / (1024 * 1024)).toFixed(2)
        };
    }
}

// Create global instance
const offlineDB = new OfflineDB();

// Make available globally
if (typeof window !== 'undefined') {
    window.offlineDB = offlineDB;
    
    // Initialize on load (but don't wait - let it initialize asynchronously)
    offlineDB.init().catch(err => {
        console.error('[OfflineDB] Initialization error:', err);
    });
}

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = OfflineDB;
}

