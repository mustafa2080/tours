/**
 * Setup Message Handler - Ensures login/signup buttons remain visible when setup messages are shown
 */

document.addEventListener('DOMContentLoaded', function() {
    // Function to check for setup messages and ensure buttons are visible
    function checkForSetupMessages() {
        // Check if we have a setup message in the page
        const setupMessageExists = document.querySelector('.alert-info') !== null && 
                                  document.querySelector('.alert-info').textContent.includes('still being set up');
        
        if (setupMessageExists) {
            console.log('Setup message detected by setup-message-handler.js');
            
            // Clear any authentication state
            sessionStorage.removeItem('userAuthenticated');
            if (document.body.classList.contains('user-authenticated')) {
                document.body.classList.remove('user-authenticated');
            }
            
            // Make sure the login/signup container is visible
            const authContainer = document.querySelector('.flex.flex-col.sm\\:flex-row.gap-2.lg\\:gap-3');
            if (authContainer) {
                authContainer.style.display = '';
                console.log('Auth container visibility forced to visible by setup-message-handler.js');
            }
            
            // Make sure the login button is visible
            const loginButtons = document.querySelectorAll('[data-login-btn]');
            loginButtons.forEach(btn => {
                btn.style.display = '';
                console.log('Login button visibility forced to visible by setup-message-handler.js');
            });
            
            // Make sure the signup button is visible
            const signupButtons = document.querySelectorAll('[data-guest-only]');
            signupButtons.forEach(btn => {
                btn.style.display = '';
                console.log('Signup button visibility forced to visible by setup-message-handler.js');
            });
            
            // Hide any logout buttons
            const logoutButtons = document.querySelectorAll('[data-logout-btn]');
            logoutButtons.forEach(btn => {
                btn.style.display = 'none';
                console.log('Logout button visibility forced to hidden by setup-message-handler.js');
            });
        }
    }
    
    // Run immediately
    checkForSetupMessages();
    
    // Also run after a short delay to ensure it catches any dynamically added messages
    setTimeout(checkForSetupMessages, 500);
    
    // Run again if any new messages are added to the DOM
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length > 0) {
                // Check if any of the added nodes are alert messages
                for (let i = 0; i < mutation.addedNodes.length; i++) {
                    const node = mutation.addedNodes[i];
                    if (node.nodeType === 1 && (node.classList.contains('alert') || node.querySelector('.alert'))) {
                        checkForSetupMessages();
                        break;
                    }
                }
            }
        });
    });
    
    // Start observing the document body for changes
    observer.observe(document.body, { childList: true, subtree: true });
});
