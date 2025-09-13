// Offline functionality for TopStyle Business Management System

// Register service worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/js/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed');
            });
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
document.addEventListener('DOMContentLoaded', function() {
    // Add connection status indicator
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        const statusDiv = document.createElement('div');
        statusDiv.id = 'connection-status';
        statusDiv.className = 'badge bg-success';
        statusDiv.innerHTML = '<i class="fas fa-wifi text-success"></i> Online';
        navbar.appendChild(statusDiv);
    }
    
    // Listen for online/offline events
    window.addEventListener('online', updateOnlineStatus);
    window.addEventListener('offline', updateOnlineStatus);
    
    // Initial status check
    updateOnlineStatus();
    
    // Cache form submissions when offline
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!navigator.onLine) {
                e.preventDefault();
                const formData = new FormData(form);
                const data = {};
                for (let [key, value] of formData.entries()) {
                    data[key] = value;
                }
                cacheFormData(form.id || 'default', data);
                alert('Form data saved for when you come back online.');
            }
        });
    });
});

