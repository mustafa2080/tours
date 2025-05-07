/**
 * Performance optimization utilities for the tourism project.
 */

// Lazy loading for images
document.addEventListener('DOMContentLoaded', function() {
    // Initialize lazy loading for images
    const lazyImages = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function(entries, observer) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    if (img.dataset.srcset) {
                        img.srcset = img.dataset.srcset;
                    }
                    img.classList.add('loaded');
                    imageObserver.unobserve(img);
                    
                    console.log('Lazy loaded image:', img.dataset.src);
                }
            });
        });
        
        lazyImages.forEach(function(img) {
            imageObserver.observe(img);
        });
    } else {
        // Fallback for browsers that don't support IntersectionObserver
        lazyImages.forEach(function(img) {
            img.src = img.dataset.src;
            if (img.dataset.srcset) {
                img.srcset = img.dataset.srcset;
            }
            img.classList.add('loaded');
        });
    }
    
    // Add fade-in animation for lazy-loaded images
    const style = document.createElement('style');
    style.textContent = `
        img.loaded {
            animation: fadeIn 0.5s ease-in;
        }
        
        @keyframes fadeIn {
            0% { opacity: 0; }
            100% { opacity: 1; }
        }
    `;
    document.head.appendChild(style);
});

// Debounce function to limit the rate at which a function can fire
function debounce(func, wait, immediate) {
    let timeout;
    return function() {
        const context = this, args = arguments;
        const later = function() {
            timeout = null;
            if (!immediate) func.apply(context, args);
        };
        const callNow = immediate && !timeout;
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
        if (callNow) func.apply(context, args);
    };
}

// Throttle function to limit the rate at which a function can fire
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

// Optimize scroll events
const optimizedScroll = throttle(function() {
    // Handle scroll events here
    console.log('Optimized scroll event fired');
}, 100);

window.addEventListener('scroll', optimizedScroll);

// Optimize resize events
const optimizedResize = debounce(function() {
    // Handle resize events here
    console.log('Optimized resize event fired');
}, 250);

window.addEventListener('resize', optimizedResize);

// Preload critical resources
function preloadResources() {
    const resources = [
        // Add critical CSS, JS, or image URLs here
        '/static/css/output.css',
        '/static/js/vendor/alpine.min.js',
        '/static/css/fonts.css'
    ];
    
    resources.forEach(url => {
        const link = document.createElement('link');
        link.rel = 'preload';
        link.href = url;
        
        if (url.endsWith('.css')) {
            link.as = 'style';
        } else if (url.endsWith('.js')) {
            link.as = 'script';
        } else if (url.endsWith('.woff2') || url.endsWith('.woff')) {
            link.as = 'font';
            link.crossOrigin = 'anonymous';
        } else if (url.endsWith('.jpg') || url.endsWith('.png') || url.endsWith('.webp')) {
            link.as = 'image';
        }
        
        document.head.appendChild(link);
    });
}

// Call preload function early
preloadResources();

// Performance monitoring
function reportPerformanceMetrics() {
    if ('performance' in window && 'getEntriesByType' in performance) {
        // Get navigation timing metrics
        const navigationTiming = performance.getEntriesByType('navigation')[0];
        
        if (navigationTiming) {
            const metrics = {
                // Time to first byte
                ttfb: navigationTiming.responseStart - navigationTiming.requestStart,
                // DOM content loaded
                domContentLoaded: navigationTiming.domContentLoadedEventEnd - navigationTiming.fetchStart,
                // Load event
                loadEvent: navigationTiming.loadEventEnd - navigationTiming.fetchStart,
                // First paint (if available)
                firstPaint: 0,
                // First contentful paint (if available)
                firstContentfulPaint: 0
            };
            
            // Get paint metrics if available
            const paintMetrics = performance.getEntriesByType('paint');
            if (paintMetrics.length > 0) {
                paintMetrics.forEach(entry => {
                    if (entry.name === 'first-paint') {
                        metrics.firstPaint = entry.startTime;
                    } else if (entry.name === 'first-contentful-paint') {
                        metrics.firstContentfulPaint = entry.startTime;
                    }
                });
            }
            
            console.log('Performance metrics:', metrics);
            
            // Send metrics to server (could be implemented)
            // sendMetricsToServer(metrics);
        }
    }
}

// Report performance metrics after page load
window.addEventListener('load', function() {
    // Wait a bit to ensure all metrics are available
    setTimeout(reportPerformanceMetrics, 1000);
});
