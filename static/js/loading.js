/**
 * Loading spinner functionality
 * This script handles the loading spinner display and hiding
 */

// Configuration (will be overridden by settings from the server)
const LoadingConfig = {
    enabled: true,
    showDelayMs: 300,
    hideDelayMs: 300
};

// Loading spinner controller
const LoadingSpinner = {
    /**
     * Initialize the loading spinner
     * @param {Object} config - Configuration options
     */
    init: function(config = {}) {
        // Merge config with defaults
        Object.assign(LoadingConfig, config);

        // Add event listeners for AJAX requests
        this._setupAjaxListeners();

        // Add event listeners for form submissions
        this._setupFormListeners();

        // Add event listeners for page navigation
        this._setupNavigationListeners();

        console.log('Loading spinner initialized with config:', LoadingConfig);
    },

    /**
     * Show the loading spinner
     * @param {string} containerId - ID of the container to show the spinner in (optional)
     * @param {string} text - Text to display below the spinner (optional)
     */
    show: function(containerId = null, text = null) {
        if (!LoadingConfig.enabled) return;

        let container;

        if (containerId) {
            container = document.getElementById(containerId);
            if (!container) {
                console.warn(`Container with ID "${containerId}" not found`);
                return;
            }

            // Make sure the container has position relative
            if (window.getComputedStyle(container).position === 'static') {
                container.style.position = 'relative';
            }

            // Find or create the loading container
            let loadingContainer = container.querySelector('.loading-container');
            if (!loadingContainer) {
                loadingContainer = this._createLoadingElement(text);
                container.appendChild(loadingContainer);
            }

            // Show the loading container after a delay
            setTimeout(() => {
                loadingContainer.style.display = 'block';
                loadingContainer.classList.add('fade-in');
            }, LoadingConfig.showDelayMs);
        } else {
            // Show fullscreen loading
            let loadingContainer = document.querySelector('.loading-container.loading-fullscreen');
            if (!loadingContainer) {
                loadingContainer = this._createLoadingElement(text, true);
                document.body.appendChild(loadingContainer);
            }

            // Show the loading container after a delay
            setTimeout(() => {
                loadingContainer.style.display = 'block';
                loadingContainer.classList.add('fade-in');
            }, LoadingConfig.showDelayMs);
        }
    },

    /**
     * Hide the loading spinner
     * @param {string} containerId - ID of the container to hide the spinner in (optional)
     */
    hide: function(containerId = null) {
        if (!LoadingConfig.enabled) return;

        let container;

        if (containerId) {
            container = document.getElementById(containerId);
            if (!container) {
                console.warn(`Container with ID "${containerId}" not found`);
                return;
            }

            // Find the loading container
            let loadingContainer = container.querySelector('.loading-container');
            if (loadingContainer) {
                // Add fade-out class
                loadingContainer.classList.add('fade-out');
                loadingContainer.classList.remove('fade-in');

                // Hide after animation
                setTimeout(() => {
                    loadingContainer.style.display = 'none';
                    loadingContainer.classList.remove('fade-out');
                }, LoadingConfig.hideDelayMs);
            }
        } else {
            // Hide fullscreen loading
            let loadingContainer = document.querySelector('.loading-container.loading-fullscreen');
            if (loadingContainer) {
                // Add fade-out class
                loadingContainer.classList.add('fade-out');
                loadingContainer.classList.remove('fade-in');

                // Hide after animation
                setTimeout(() => {
                    loadingContainer.style.display = 'none';
                    loadingContainer.classList.remove('fade-out');
                }, LoadingConfig.hideDelayMs);
            }
        }
    },

    /**
     * Create a loading element
     * @param {string} text - Text to display below the spinner (optional)
     * @param {boolean} fullscreen - Whether to display the spinner fullscreen (optional)
     * @returns {HTMLElement} - The loading element
     * @private
     */
    _createLoadingElement: function(text = null, fullscreen = false) {
        const loadingContainer = document.createElement('div');
        loadingContainer.className = 'loading-container';
        if (fullscreen) {
            loadingContainer.classList.add('loading-fullscreen');
        }
        loadingContainer.style.display = 'none';

        const spinnerWrapper = document.createElement('div');
        spinnerWrapper.className = 'loading-spinner-wrapper';

        const glassEffect = document.createElement('div');
        glassEffect.className = 'glass-effect';

        // Create dots spinner (default style)
        const spinner = document.createElement('div');
        spinner.className = 'custom-spinner floating';

        // Add 8 dots
        for (let i = 0; i < 8; i++) {
            const dot = document.createElement('div');
            dot.className = 'custom-spinner-dot';
            spinner.appendChild(dot);
        }

        // Add text element
        const textElement = document.createElement('div');
        textElement.className = 'loading-text';
        textElement.textContent = text || 'Loading...';

        glassEffect.appendChild(spinner);
        glassEffect.appendChild(textElement);
        spinnerWrapper.appendChild(glassEffect);
        loadingContainer.appendChild(spinnerWrapper);

        return loadingContainer;
    },

    /**
     * Set up AJAX request listeners
     * @private
     */
    _setupAjaxListeners: function() {
        // Track active AJAX requests
        let activeRequests = 0;

        // Override XMLHttpRequest
        const originalXHR = window.XMLHttpRequest;

        window.XMLHttpRequest = function() {
            const xhr = new originalXHR();

            xhr.addEventListener('loadstart', function() {
                activeRequests++;
                if (activeRequests === 1) {
                    LoadingSpinner.show();
                }
            });

            xhr.addEventListener('loadend', function() {
                activeRequests--;
                if (activeRequests === 0) {
                    LoadingSpinner.hide();
                }
            });

            return xhr;
        };

        // Override fetch
        const originalFetch = window.fetch;

        window.fetch = function() {
            activeRequests++;
            if (activeRequests === 1) {
                LoadingSpinner.show();
            }

            return originalFetch.apply(this, arguments)
                .then(response => {
                    activeRequests--;
                    if (activeRequests === 0) {
                        LoadingSpinner.hide();
                    }
                    return response;
                })
                .catch(error => {
                    activeRequests--;
                    if (activeRequests === 0) {
                        LoadingSpinner.hide();
                    }
                    throw error;
                });
        };
    },

    /**
     * Set up form submission listeners
     * @private
     */
    _setupFormListeners: function() {
        document.addEventListener('submit', function(event) {
            const form = event.target;

            // Skip if the form has data-no-loading attribute
            if (form.hasAttribute('data-no-loading')) {
                return;
            }

            // Skip if the form is for mailto: or tel: links
            const action = form.getAttribute('action');
            if (action && (action.startsWith('mailto:') || action.startsWith('tel:'))) {
                return;
            }

            // Skip if the form contains a submit button with data-no-loading attribute
            const submitButtons = form.querySelectorAll('button[type="submit"], input[type="submit"]');
            for (let i = 0; i < submitButtons.length; i++) {
                if (submitButtons[i].hasAttribute('data-no-loading')) {
                    return;
                }
            }

            // Show loading spinner in the form's container or fullscreen
            const containerId = form.getAttribute('data-loading-container');
            if (containerId) {
                LoadingSpinner.show(containerId);
            } else {
                LoadingSpinner.show();
            }
        });
    },

    /**
     * Set up page navigation listeners
     * @private
     */
    _setupNavigationListeners: function() {
        // Show loading spinner on page navigation, but exclude mailto: and tel: links
        document.addEventListener('click', function(event) {
            // Check if the click was on a link
            let target = event.target;
            while (target && target !== document) {
                if (target.tagName === 'A') {
                    const href = target.getAttribute('href');
                    // Skip mailto: and tel: links
                    if (href && (href.startsWith('mailto:') || href.startsWith('tel:'))) {
                        // Prevent loading spinner for these links
                        return;
                    }
                    break;
                }
                target = target.parentNode;
            }
        });

        // Show loading spinner on page navigation
        window.addEventListener('beforeunload', function(event) {
            // Get the active element that triggered the navigation
            const activeElement = document.activeElement;

            // Skip loading spinner for mailto: and tel: links
            if (activeElement && activeElement.tagName === 'A') {
                const href = activeElement.getAttribute('href');
                if (href && (href.startsWith('mailto:') || href.startsWith('tel:'))) {
                    return;
                }
            }

            LoadingSpinner.show(null, 'Loading page...');
        });
    }
};

// Initialize the loading spinner when the DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Get configuration from the server (if available)
    const serverConfig = window.LOADING_CONFIG || {};

    // Initialize the loading spinner
    LoadingSpinner.init(serverConfig);
});
