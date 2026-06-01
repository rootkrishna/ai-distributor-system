/**
 * AI Distributor Management System - Frontend Script
 * Handles modals, forms, and UI interactions
 */

// ===========================
// MODAL FUNCTIONS
// ===========================

/**
 * Open a modal by ID
 */
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'block';
    }
}

/**
 * Close a modal by ID
 */
function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * Close modal when clicking outside of it
 */
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
};

// ===========================
// MENU FUNCTIONS
// ===========================

/**
 * Show export menu modal
 */
function showExportMenu() {
    openModal('exportModal');
}

/**
 * Show AI tools menu modal
 */
function showAIMenu() {
    openModal('aiModal');
}

// ===========================
// AI FEATURES
// ===========================

/**
 * Clean duplicate records from database
 */
function cleanDuplicates() {
    if (!confirm('This will remove duplicate user records. Continue?')) return;

    fetch('/api/ai/clean-duplicates', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                alert(`✓ Success!\n${data.message}`);
                location.reload();
            } else {
                alert(`✗ Error: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while cleaning duplicates');
        });
}

/**
 * Generate system summary report
 */
function generateSummary() {
    fetch('/api/ai/generate-summary', { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                closeModal('aiModal');
                document.getElementById('summaryText').value = data.summary;
                openModal('summaryModal');
            } else {
                alert(`✗ Error: ${data.message}`);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while generating summary');
        });
}

/**
 * Download summary as text file
 */
function downloadSummary() {
    const text = document.getElementById('summaryText').value;
    const blob = new Blob([text], { type: 'text/plain' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `summary_${new Date().getTime()}.txt`;
    a.click();
    window.URL.revokeObjectURL(url);
}

// ===========================
// TIME DISPLAY
// ===========================

/**
 * Update current time in top bar
 */
function updateTime() {
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    const timeElement = document.getElementById('current-time');
    if (timeElement) {
        timeElement.textContent = timeString;
    }
}

// Update time every second
setInterval(updateTime, 1000);
updateTime();

// ===========================
// NOTIFICATIONS
// ===========================

/**
 * Show a notification
 */
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `alert alert-${type}`;
    notification.innerHTML = `
        ${message}
        <button onclick="this.parentElement.style.display='none';">&times;</button>
    `;
    document.querySelector('.content-area').prepend(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// ===========================
// FORM VALIDATION
// ===========================

/**
 * Validate email format
 */
function isValidEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Validate phone number
 */
function isValidPhone(phone) {
    const re = /^[\d\s\-\+\(\)]+$/;
    return re.test(phone) && phone.replace(/\D/g, '').length >= 10;
}

// ===========================
// UTILITY FUNCTIONS
// ===========================

/**
 * Format currency
 */
function formatCurrency(amount) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'INR'
    }).format(amount);
}

/**
 * Format date
 */
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

/**
 * Debounce function for search
 */
function debounce(func, delay) {
    let timeoutId;
    return function (...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func.apply(this, args), delay);
    };
}

// ===========================
// DOCUMENT READY
// ===========================

document.addEventListener('DOMContentLoaded', function() {
    console.log('✓ AI Distributor Management System loaded');
});
