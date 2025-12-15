/**
 * ROBUST FRONTEND AUTO-SAVE SERVICE
 * ==================================
 * Automatically saves all form data and application state to localStorage
 * and syncs with backend. Ensures nothing is lost even if the app is closed.
 * 
 * Features:
 * - Auto-save form data as user types
 * - Save application state
 * - Sync with backend
 * - Restore on page load
 * - Change tracking
 */

class AutoSaveService {
    constructor() {
        this.storageKey = 'topstyle_autosave_';
        this.syncInterval = 30000; // Sync every 30 seconds
        this.debounceDelay = 2000; // Save 2 seconds after last change
        this.pendingSaves = new Map();
        this.saveTimers = new Map();
        this.isInitialized = false;
        
        this.init();
    }
    
    /**
     * Initialize the auto-save service
     */
    init() {
        if (this.isInitialized) return;
        
        // Restore saved data on page load
        this.restoreAllData();
        
        // Set up auto-save for all forms
        this.setupFormAutoSave();
        
        // Set up periodic sync
        this.startPeriodicSync();
        
        // Save before page unload
        window.addEventListener('beforeunload', () => this.saveAllPending());
        
        // Save on visibility change (tab switch)
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.saveAllPending();
            }
        });
        
        this.isInitialized = true;
        console.log('[AUTO-SAVE] Service initialized');
    }
    
    /**
     * Set up auto-save for all forms on the page
     */
    setupFormAutoSave() {
        // Find all forms, but exclude forms inside modals (they're temporary)
        const forms = document.querySelectorAll('form');
        
        forms.forEach((form, index) => {
            // Skip forms inside modals - they're temporary and don't need autosave
            const isInModal = form.closest('.modal') !== null;
            if (isInModal) {
                return; // Skip modal forms
            }
            
            const formId = form.id || `form_${index}`;
            
            // Save form data on input
            form.addEventListener('input', (e) => {
                this.debouncedSave(formId, () => this.saveFormData(form));
            });
            
            // Save on form submit
            form.addEventListener('submit', () => {
                this.saveFormData(form);
            });
        });
        
        // Also watch for dynamic form additions
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1 && node.tagName === 'FORM') {
                        this.setupFormAutoSave();
                    }
                });
            });
        });
        
        observer.observe(document.body, { childList: true, subtree: true });
    }
    
    /**
     * Save form data to localStorage
     */
    saveFormData(form) {
        try {
            const formId = form.id || 'unnamed_form';
            const formData = new FormData(form);
            const data = {};
            
            // Convert FormData to object (skip file inputs)
            for (const [key, value] of formData.entries()) {
                // Skip file inputs - we can't restore them anyway
                const input = form.querySelector(`[name="${key}"]`);
                if (input && input.type === 'file') {
                    continue; // Skip file inputs
                }
                
                if (data[key]) {
                    // Handle multiple values (e.g., checkboxes)
                    if (Array.isArray(data[key])) {
                        data[key].push(value);
                    } else {
                        data[key] = [data[key], value];
                    }
                } else {
                    data[key] = value;
                }
            }
            
            // Also get values from inputs not in FormData (e.g., disabled inputs)
            form.querySelectorAll('input, textarea, select').forEach((input) => {
                // Skip file inputs completely - they cannot be saved/restored
                if (input.type === 'file') {
                    return; // Skip file inputs
                }
                
                if (input.name && !data[input.name]) {
                    if (input.type === 'checkbox') {
                        data[input.name] = input.checked;
                    } else if (input.type === 'radio') {
                        if (input.checked) {
                            data[input.name] = input.value;
                        }
                    } else {
                        data[input.name] = input.value;
                    }
                }
            });
            
            // Save to localStorage
            const key = `${this.storageKey}form_${formId}`;
            localStorage.setItem(key, JSON.stringify({
                data: data,
                timestamp: new Date().toISOString(),
                formId: formId
            }));
            
            // Mark for backend sync
            this.pendingSaves.set(key, data);
            
            console.log(`[AUTO-SAVE] Saved form data: ${formId}`);
            
        } catch (error) {
            console.error('[AUTO-SAVE] Error saving form data:', error);
        }
    }
    
    /**
     * Safely set input value - catches InvalidStateError for file inputs
     */
    _safeSetInputValue(input, value) {
        try {
            // Multiple checks to ensure it's not a file input
            const inputType = (input.type || input.getAttribute('type') || '').toLowerCase();
            if (inputType === 'file') {
                return false; // Don't try to set file input values
            }
            
            // Try to set the value
            const valueToSet = value != null ? String(value) : '';
            input.value = valueToSet;
            return true;
        } catch (error) {
            // Silently ignore InvalidStateError and SecurityError (file inputs)
            if (error.name === 'InvalidStateError' || error.name === 'SecurityError') {
                return false; // Expected error for file inputs
            }
            // Re-throw unexpected errors
            throw error;
        }
    }
    
    /**
     * Restore form data from localStorage
     */
    restoreFormData(formId) {
        try {
            const key = `${this.storageKey}form_${formId}`;
            const saved = localStorage.getItem(key);
            
            if (saved) {
                const { data, timestamp } = JSON.parse(saved);
                const form = document.getElementById(formId) || document.querySelector(`form[name="${formId}"]`);
                
                if (form) {
                    // First, filter out any file input names from the data to prevent errors
                    const fileInputs = form.querySelectorAll('input[type="file"]');
                    const fileInputNames = new Set();
                    fileInputs.forEach(fileInput => {
                        if (fileInput.name) {
                            fileInputNames.add(fileInput.name);
                        }
                    });
                    
                    // Restore form values with comprehensive error handling
                    Object.keys(data).forEach((name) => {
                        // Skip if this is a known file input name
                        if (fileInputNames.has(name)) {
                            return; // Skip file inputs completely
                        }
                        
                        try {
                            const input = form.querySelector(`[name="${name}"]`);
                            if (!input) return; // Skip if input not found
                            
                            // Multiple ways to detect file inputs - must check all
                            const inputType = (input.type || input.getAttribute('type') || '').toLowerCase();
                            
                            // ALWAYS skip file inputs - they cannot be restored programmatically
                            if (inputType === 'file') {
                                return; // Skip this iteration completely
                            }
                            
                            // Additional check: if the input tag is INPUT and type is file
                            if (input.tagName && input.tagName.toUpperCase() === 'INPUT' && inputType === 'file') {
                                return; // Skip file inputs
                            }
                            
                            // Handle different input types
                            if (inputType === 'checkbox') {
                                input.checked = Boolean(data[name]);
                            } else if (inputType === 'radio') {
                                const radio = form.querySelector(`[name="${name}"][value="${data[name]}"]`);
                                if (radio) radio.checked = true;
                            } else {
                                // For all other inputs, set value with comprehensive error handling
                                // Use a more defensive approach - check if we can set the value property
                                try {
                                    // Final check - make absolutely sure it's not a file input
                                    const finalCheckType = (input.type || '').toLowerCase();
                                    if (finalCheckType === 'file') {
                                        return; // Skip if somehow it's still a file input
                                    }
                                    
                                    // Use safe setter method that handles file inputs
                                    const success = this._safeSetInputValue(input, data[name]);
                                    if (!success) {
                                        // _safeSetInputValue returned false, likely a file input
                                        return;
                                    }
                                } catch (error) {
                                    // Silently skip InvalidStateError and SecurityError (file inputs)
                                    // These are expected and should not be logged
                                    const errorName = error?.name || error?.constructor?.name || '';
                                    const errorMessage = error?.message || '';
                                    
                                    const isFileInputError = 
                                        errorName === 'InvalidStateError' || 
                                        errorName === 'SecurityError' ||
                                        errorMessage.includes('filename') ||
                                        errorMessage.includes('file input') ||
                                        errorMessage.includes('accepts a filename');
                                    
                                    if (isFileInputError) {
                                        // Silently ignore - this is expected for file inputs
                                        return;
                                    }
                                    // Only log unexpected errors
                                    console.warn('[AUTO-SAVE] Could not restore value for input:', name, error.message);
                                }
                            }
                        } catch (error) {
                            // Catch any errors in the forEach loop and continue
                            // Don't let one input break the entire restore process
                            // Silently ignore InvalidStateError and SecurityError (file inputs)
                            const errorName = error?.name || error?.constructor?.name || '';
                            const errorMessage = error?.message || '';
                            
                            const isFileInputError = 
                                errorName === 'InvalidStateError' || 
                                errorName === 'SecurityError' ||
                                errorMessage.includes('filename') ||
                                errorMessage.includes('file input') ||
                                errorMessage.includes('accepts a filename');
                            
                            if (isFileInputError) {
                                // Silently ignore file input errors - do not log
                                return;
                            }
                            // Only log unexpected errors
                            console.warn('[AUTO-SAVE] Error restoring input:', name, error.message);
                        }
                    });
                    
                    console.log(`[AUTO-SAVE] Restored form data: ${formId} (saved at ${timestamp})`);
                    return true;
                }
            }
            
            return false;
            
        } catch (error) {
            // Don't log InvalidStateError or SecurityError - they're expected for file inputs
            // These errors occur when trying to set values on file inputs, which we intentionally skip
            // Check error name, message, and constructor name to catch all variations
            const errorName = error?.name || error?.constructor?.name || '';
            const errorMessage = error?.message || '';
            
            const isFileInputError = 
                errorName === 'InvalidStateError' || 
                errorName === 'SecurityError' ||
                errorMessage.includes('filename') ||
                errorMessage.includes('file input') ||
                errorMessage.includes('accepts a filename');
            
            if (isFileInputError) {
                // Silently return - file input errors are expected and handled
                // Do not log these errors as they are expected behavior
                return false;
            }
            // Only log unexpected errors
            console.error('[AUTO-SAVE] Error restoring form data:', error);
            return false;
        }
    }
    
    /**
     * Save application state
     */
    saveState(key, value) {
        try {
            const stateKey = `${this.storageKey}state_${key}`;
            const state = {
                value: value,
                timestamp: new Date().toISOString()
            };
            
            localStorage.setItem(stateKey, JSON.stringify(state));
            this.pendingSaves.set(stateKey, value);
            
            console.log(`[AUTO-SAVE] Saved state: ${key}`);
            
        } catch (error) {
            console.error('[AUTO-SAVE] Error saving state:', error);
        }
    }
    
    /**
     * Get saved application state
     */
    getState(key, defaultValue = null) {
        try {
            const stateKey = `${this.storageKey}state_${key}`;
            const saved = localStorage.getItem(stateKey);
            
            if (saved) {
                const { value } = JSON.parse(saved);
                return value;
            }
            
            return defaultValue;
            
        } catch (error) {
            console.error('[AUTO-SAVE] Error getting state:', error);
            return defaultValue;
        }
    }
    
    /**
     * Clear saved data for a form or state
     */
    clear(key) {
        try {
            const formKey = `${this.storageKey}form_${key}`;
            const stateKey = `${this.storageKey}state_${key}`;
            
            localStorage.removeItem(formKey);
            localStorage.removeItem(stateKey);
            this.pendingSaves.delete(formKey);
            this.pendingSaves.delete(stateKey);
            
            console.log(`[AUTO-SAVE] Cleared: ${key}`);
            
        } catch (error) {
            console.error('[AUTO-SAVE] Error clearing:', error);
        }
    }
    
    /**
     * Restore all saved data on page load
     */
    restoreAllData() {
        try {
            // Restore all forms
            const forms = document.querySelectorAll('form');
            forms.forEach((form, index) => {
                const formId = form.id || `form_${index}`;
                this.restoreFormData(formId);
            });
            
            // Trigger restore event
            window.dispatchEvent(new CustomEvent('autosave:restored'));
            
            console.log('[AUTO-SAVE] Restored all saved data');
            
        } catch (error) {
            console.error('[AUTO-SAVE] Error restoring data:', error);
        }
    }
    
    /**
     * Save all pending changes
     */
    saveAllPending() {
        try {
            // Save all forms
            const forms = document.querySelectorAll('form');
            forms.forEach((form) => {
                this.saveFormData(form);
            });
            
            // Sync with backend
            this.syncWithBackend();
            
            console.log('[AUTO-SAVE] Saved all pending changes');
            
        } catch (error) {
            console.error('[AUTO-SAVE] Error saving pending:', error);
        }
    }
    
    /**
     * Sync saved data with backend
     */
    async syncWithBackend() {
        if (this.pendingSaves.size === 0) return;
        
        try {
            // Get CSRF token
            const csrfToken = this.getCSRFToken();
            
            // Prepare sync data
            const syncData = {};
            this.pendingSaves.forEach((value, key) => {
                syncData[key] = value;
            });
            
            // Send to backend
            const response = await fetch('/api/autosave/sync/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    data: syncData,
                    timestamp: new Date().toISOString()
                })
            });
            
            if (response.ok) {
                // Clear pending saves on successful sync
                this.pendingSaves.clear();
                console.log('[AUTO-SAVE] Synced with backend');
            } else {
                console.warn('[AUTO-SAVE] Backend sync failed:', response.status);
            }
            
        } catch (error) {
            console.error('[AUTO-SAVE] Error syncing with backend:', error);
        }
    }
    
    /**
     * Start periodic sync with backend
     */
    startPeriodicSync() {
        setInterval(() => {
            this.syncWithBackend();
        }, this.syncInterval);
    }
    
    /**
     * Debounced save function
     */
    debouncedSave(key, saveFunction) {
        // Clear existing timer
        if (this.saveTimers.has(key)) {
            clearTimeout(this.saveTimers.get(key));
        }
        
        // Set new timer
        const timer = setTimeout(() => {
            saveFunction();
            this.saveTimers.delete(key);
        }, this.debounceDelay);
        
        this.saveTimers.set(key, timer);
    }
    
    /**
     * Get CSRF token from cookies
     */
    getCSRFToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        
        return cookieValue || '';
    }
}

// Initialize auto-save service globally
window.autoSaveService = new AutoSaveService();

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AutoSaveService;
}

