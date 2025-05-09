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
    } else {
        // Make sure to clear the authentication state if not authenticated
        sessionStorage.removeItem('userAuthenticated');
    }

    // Check for authentication state in sessionStorage
    const storedAuthState = sessionStorage.getItem('userAuthenticated');

    // Function to update UI based on authentication state
    function updateUIForAuthenticatedUser(isAuthenticated) {
        console.log('Updating UI for authentication state:', isAuthenticated);

        // Check if we have a setup message in the page
        const setupMessageExists = document.querySelector('.alert-info') !== null &&
                                  document.querySelector('.alert-info').textContent.includes('still being set up');

        // If we have a setup message, force non-authenticated state
        if (setupMessageExists) {
            console.log('Setup message detected, forcing non-authenticated UI state');
            isAuthenticated = false;
            sessionStorage.removeItem('userAuthenticated');
            if (document.body.classList.contains('user-authenticated')) {
                document.body.classList.remove('user-authenticated');
            }
        }

        // Get all elements that should be shown/hidden based on auth state
        const authOnlyElements = document.querySelectorAll('[data-auth-only]');
        const guestOnlyElements = document.querySelectorAll('[data-guest-only]');

        // Update visibility
        authOnlyElements.forEach(element => {
            element.style.display = isAuthenticated ? '' : 'none';
            console.log('Auth-only element visibility updated:', element, element.style.display);
        });

        guestOnlyElements.forEach(element => {
            element.style.display = isAuthenticated ? 'none' : '';
            console.log('Guest-only element visibility updated:', element, element.style.display);
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
                console.log('Dashboard link visibility updated:', link, link.style.display);
            }
        });

        // Update login/logout buttons
        const loginButtons = document.querySelectorAll('[data-login-btn]');
        const logoutButtons = document.querySelectorAll('[data-logout-btn]');

        // If we have a setup message, always show login buttons
        if (setupMessageExists) {
            loginButtons.forEach(btn => {
                btn.style.display = '';
                console.log('Login button forced visible due to setup message:', btn);
            });

            logoutButtons.forEach(btn => {
                btn.style.display = 'none';
                console.log('Logout button forced hidden due to setup message:', btn);
            });
        } else {
            // Normal behavior
            loginButtons.forEach(btn => {
                btn.style.display = isAuthenticated ? 'none' : '';
                console.log('Login button visibility updated:', btn, btn.style.display);
            });

            logoutButtons.forEach(btn => {
                btn.style.display = isAuthenticated ? '' : 'none';
                console.log('Logout button visibility updated:', btn, btn.style.display);
            });
        }

        // Make sure the login/signup container is visible
        const authContainer = document.querySelector('.flex.flex-col.sm\\:flex-row.gap-2.lg\\:gap-3');
        if (authContainer && (!isAuthenticated || setupMessageExists)) {
            authContainer.style.display = '';
            console.log('Auth container visibility forced to visible:', authContainer);
        }
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

        // Check if we have a setup message in the page
        const setupMessageExists = document.querySelector('.alert-info') !== null &&
                                  document.querySelector('.alert-info').textContent.includes('still being set up');

        // If we have a setup message, login was not successful
        if (setupMessageExists) {
            console.log('Setup message detected, login not successful');
            sessionStorage.removeItem('loginAttempted');
            sessionStorage.removeItem('userAuthenticated');

            // Make sure the login/signup container is visible
            const authContainer = document.querySelector('.flex.flex-col.sm\\:flex-row.gap-2.lg\\:gap-3');
            if (authContainer) {
                authContainer.style.display = '';
                console.log('Auth container visibility forced to visible due to setup message');

                // Make sure the login button is visible
                const loginButton = document.querySelector('[data-login-btn]');
                if (loginButton) {
                    loginButton.style.display = '';
                    console.log('Login button visibility forced to visible due to setup message');
                }

                // Make sure the signup button is visible
                const signupButton = document.querySelector('[data-guest-only]');
                if (signupButton) {
                    signupButton.style.display = '';
                    console.log('Signup button visibility forced to visible due to setup message');
                }
            }
        }
        // If we're not on the login page anymore and no setup message, assume login was successful
        else if (!window.location.href.includes('/login') && !window.location.href.includes('/accounts/login')) {
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

    // Check if we have a setup message in the page
    const setupMessageExists = document.querySelector('.alert-info') !== null &&
                              document.querySelector('.alert-info').textContent.includes('still being set up');

    // If we have a setup message, make sure we're not falsely authenticated
    if (setupMessageExists) {
        console.log('Setup message detected, ensuring user is not falsely authenticated');
        sessionStorage.removeItem('userAuthenticated');
        if (document.body.classList.contains('user-authenticated')) {
            document.body.classList.remove('user-authenticated');
        }
    }

    // Final check to ensure login/signup buttons are visible when not authenticated
    setTimeout(() => {
        // Check again for setup message
        const setupMessageExists = document.querySelector('.alert-info') !== null &&
                                  document.querySelector('.alert-info').textContent.includes('still being set up');

        // If we have a setup message, force buttons to be visible
        if (setupMessageExists) {
            console.log('Setup message detected in final check, forcing buttons to be visible');

            // Make sure the login/signup container is visible
            const authContainer = document.querySelector('.flex.flex-col.sm\\:flex-row.gap-2.lg\\:gap-3');
            if (authContainer) {
                authContainer.style.display = '';
                console.log('Auth container visibility forced to visible due to setup message');

                // Make sure the login button is visible
                const loginButton = document.querySelector('[data-login-btn]');
                if (loginButton) {
                    loginButton.style.display = '';
                    console.log('Login button visibility forced to visible due to setup message');
                }

                // Make sure the signup button is visible
                const signupButton = document.querySelector('[data-guest-only]');
                if (signupButton) {
                    signupButton.style.display = '';
                    console.log('Signup button visibility forced to visible due to setup message');
                }
            }
            return;
        }

        // Normal check for non-authenticated users
        const userIsAuthenticated = document.body.classList.contains('user-authenticated') ||
                                   document.querySelector('[data-user-authenticated="true"]') !== null ||
                                   sessionStorage.getItem('userAuthenticated') === 'true';

        if (!userIsAuthenticated) {
            console.log('Final check: User is not authenticated, ensuring login/signup buttons are visible');

            // Make sure the login/signup container is visible
            const authContainer = document.querySelector('.flex.flex-col.sm\\:flex-row.gap-2.lg\\:gap-3');
            if (authContainer) {
                authContainer.style.display = '';
                console.log('Auth container visibility forced to visible in final check');

                // Make sure the login button is visible
                const loginButton = document.querySelector('[data-login-btn]');
                if (loginButton) {
                    loginButton.style.display = '';
                    console.log('Login button visibility forced to visible in final check');
                }

                // Make sure the signup button is visible
                const signupButton = document.querySelector('[data-guest-only]');
                if (signupButton) {
                    signupButton.style.display = '';
                    console.log('Signup button visibility forced to visible in final check');
                }
            }
        }
    }, 500);
});
