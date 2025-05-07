/**
 * User State Management - Handles user authentication state across pages
 */

document.addEventListener('DOMContentLoaded', function() {
    // Check if user is authenticated
    const userIsAuthenticated = document.body.classList.contains('user-authenticated') ||
                               document.querySelector('[data-user-authenticated="true"]') !== null;

    // Store authentication state in sessionStorage
    if (userIsAuthenticated) {
        sessionStorage.setItem('userAuthenticated', 'true');
    }

    // Check for authentication state in sessionStorage
    const storedAuthState = sessionStorage.getItem('userAuthenticated');

    // Function to update UI based on authentication state
    function updateUIForAuthenticatedUser(isAuthenticated) {
        // Get all elements that should be shown/hidden based on auth state
        const authOnlyElements = document.querySelectorAll('[data-auth-only]');
        const guestOnlyElements = document.querySelectorAll('[data-guest-only]');

        // Update visibility
        authOnlyElements.forEach(element => {
            element.style.display = isAuthenticated ? '' : 'none';
        });

        guestOnlyElements.forEach(element => {
            element.style.display = isAuthenticated ? 'none' : '';
        });

        // Update navigation links
        const navLinks = document.querySelectorAll('.nav-link');
        navLinks.forEach(link => {
            // Check if this is a dashboard/profile link
            const isDashboardLink = link.href.includes('/dashboard') ||
                                   link.href.includes('/profile') ||
                                   link.href.includes('/bookings') ||
                                   link.href.includes('/wishlist');

            if (isDashboardLink) {
                link.style.display = isAuthenticated ? '' : 'none';
            }
        });

        // Update login/logout buttons
        const loginButtons = document.querySelectorAll('[data-login-btn]');
        const logoutButtons = document.querySelectorAll('[data-logout-btn]');

        loginButtons.forEach(btn => {
            btn.style.display = isAuthenticated ? 'none' : '';
        });

        logoutButtons.forEach(btn => {
            btn.style.display = isAuthenticated ? '' : 'none';
        });
    }

    // Apply stored authentication state if available
    if (storedAuthState === 'true') {
        updateUIForAuthenticatedUser(true);

        // Add authenticated class to body if not already present
        if (!document.body.classList.contains('user-authenticated')) {
            document.body.classList.add('user-authenticated');
        }
    }

    // Listen for login/logout events
    window.addEventListener('user-logged-in', function() {
        sessionStorage.setItem('userAuthenticated', 'true');
        updateUIForAuthenticatedUser(true);
        document.body.classList.add('user-authenticated');
    });

    window.addEventListener('user-logged-out', function() {
        sessionStorage.removeItem('userAuthenticated');
        updateUIForAuthenticatedUser(false);
        document.body.classList.remove('user-authenticated');
    });

    // Check for login form submission
    const loginForm = document.querySelector('form[action*="login"]');
    if (loginForm) {
        loginForm.addEventListener('submit', function() {
            // We'll set a flag to check on next page load
            sessionStorage.setItem('loginAttempted', 'true');
            console.log('Login form submitted, setting loginAttempted flag');
        });
    }

    // Also check for login button clicks
    const loginButtons = document.querySelectorAll('[data-login-btn]');
    loginButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            console.log('Login button clicked');
            // We'll set a flag to check on next page load
            sessionStorage.setItem('loginAttempted', 'true');
        });
    });

    // Check for logout form submission
    const logoutForm = document.querySelector('form[action*="logout"]');
    if (logoutForm) {
        logoutForm.addEventListener('submit', function(e) {
            // Clear authentication state immediately
            sessionStorage.removeItem('userAuthenticated');
            // We'll set a flag to check on next page load
            sessionStorage.setItem('logoutAttempted', 'true');
            console.log('Logout form submitted, setting logoutAttempted flag');

            // Add CSRF token to form if not present
            if (!this.querySelector('input[name="csrfmiddlewaretoken"]')) {
                const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');
                if (csrfToken) {
                    const csrfInput = document.createElement('input');
                    csrfInput.type = 'hidden';
                    csrfInput.name = 'csrfmiddlewaretoken';
                    csrfInput.value = csrfToken;
                    this.appendChild(csrfInput);
                    console.log('Added CSRF token to logout form');
                }
            }
        });
    }

    // Also handle logout links
    const logoutLinks = document.querySelectorAll('a[href*="logout"]');
    logoutLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            console.log('Logout link clicked');
            // Set logout attempted flag
            sessionStorage.setItem('logoutAttempted', 'true');
            sessionStorage.removeItem('userAuthenticated');
        });
    });

    // Check if we just logged in (redirect from login page)
    if (sessionStorage.getItem('loginAttempted') === 'true') {
        console.log('Login was attempted, checking if we are on a post-login page');

        // If we're not on the login page anymore, assume login was successful
        if (!window.location.href.includes('/login') && !window.location.href.includes('/accounts/login')) {
            console.log('Not on login page, assuming successful login');
            sessionStorage.removeItem('loginAttempted');
            sessionStorage.setItem('userAuthenticated', 'true');

            // Dispatch event for other scripts
            window.dispatchEvent(new Event('user-logged-in'));

            // Check if user is authenticated in the DOM
            const userAuthenticatedInDOM = document.body.classList.contains('user-authenticated') ||
                                          document.querySelector('[data-user-authenticated="true"]') !== null;

            console.log('User authenticated in DOM:', userAuthenticatedInDOM);
            console.log('User authenticated in session:', true);

            // Refresh the page to ensure all elements are updated
            if (!document.body.classList.contains('user-authenticated')) {
                console.log('Refreshing page to update UI');
                // Add class before reload to prevent flicker
                document.body.classList.add('user-authenticated');
                // Use a timeout to allow console logs to be seen
                setTimeout(() => {
                    window.location.reload();
                }, 500);
            }
        }
    }

    // Check if we just logged out (redirect from logout page)
    if (sessionStorage.getItem('logoutAttempted') === 'true') {
        // If we're not on the logout page anymore, assume logout was successful
        if (!window.location.href.includes('/logout')) {
            sessionStorage.removeItem('logoutAttempted');
            sessionStorage.removeItem('userAuthenticated');
            // Dispatch event for other scripts
            window.dispatchEvent(new Event('user-logged-out'));
            // Refresh the page to ensure all elements are updated
            if (document.body.classList.contains('user-authenticated')) {
                window.location.reload();
            }
        }
    }

    // Check for language change
    const languageForms = document.querySelectorAll('form[action*="setlang"]');
    if (languageForms.length > 0) {
        languageForms.forEach(form => {
            form.addEventListener('submit', function() {
                // Store current authentication state to persist across language change
                if (sessionStorage.getItem('userAuthenticated') === 'true') {
                    sessionStorage.setItem('languageChangeWithAuth', 'true');
                }
            });
        });
    }

    // Check if we just changed language while authenticated
    if (sessionStorage.getItem('languageChangeWithAuth') === 'true') {
        // Restore authentication state after language change
        sessionStorage.setItem('userAuthenticated', 'true');
        sessionStorage.removeItem('languageChangeWithAuth');
        // Update UI for authenticated user
        updateUIForAuthenticatedUser(true);
        // Add authenticated class to body if not already present
        if (!document.body.classList.contains('user-authenticated')) {
            document.body.classList.add('user-authenticated');
        }
    }
});
