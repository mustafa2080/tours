/**
 * CSRF Management for Tourism Project
 * This script handles CSRF token management for AJAX requests
 */

// Function to get CSRF token from cookie
function getCookie(name) {
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
    return cookieValue;
}

// Function to set CSRF token in all forms
function addCSRFToForms() {
    const csrftoken = getCookie('csrftoken');
    
    // If no CSRF token found, try to get it from meta tag
    if (!csrftoken) {
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            csrftoken = metaTag.getAttribute('content');
        }
    }
    
    // If still no CSRF token, log error
    if (!csrftoken) {
        console.error('CSRF token not found. Forms may not submit correctly.');
        return;
    }
    
    // Add CSRF token to all forms
    document.querySelectorAll('form').forEach(form => {
        // Skip forms that already have CSRF token
        if (form.querySelector('input[name="csrfmiddlewaretoken"]')) {
            return;
        }
        
        // Create input element
        const input = document.createElement('input');
        input.type = 'hidden';
        input.name = 'csrfmiddlewaretoken';
        input.value = csrftoken;
        
        // Add to form
        form.appendChild(input);
        
        console.log('Added CSRF token to form:', form);
    });
}

// Function to ensure CSRF token is present in cookie
function ensureCSRFCookie() {
    // Check if CSRF cookie exists
    if (!getCookie('csrftoken')) {
        // If not, make a GET request to the server to set it
        fetch('/csrf/', { 
            method: 'GET',
            credentials: 'same-origin'
        })
        .then(response => {
            console.log('CSRF cookie refreshed');
            // After getting response, add CSRF to forms
            addCSRFToForms();
        })
        .catch(error => {
            console.error('Error refreshing CSRF cookie:', error);
        });
    } else {
        // If cookie exists, add CSRF to forms
        addCSRFToForms();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Ensure CSRF cookie exists
    ensureCSRFCookie();
    
    // Add event listener for form submissions
    document.addEventListener('submit', function(e) {
        const form = e.target;
        
        // Check if form has CSRF token
        if (!form.querySelector('input[name="csrfmiddlewaretoken"]')) {
            // Prevent form submission
            e.preventDefault();
            
            // Add CSRF token
            addCSRFToForms();
            
            // Resubmit form
            setTimeout(() => {
                form.submit();
            }, 10);
        }
    });
});
