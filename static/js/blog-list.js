/**
 * Blog List Page JavaScript
 * Enhances the blog list page with interactive features
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize parallax effect
    initParallax();

    // Initialize masonry layout
    initMasonry();

    // Initialize animations
    initAnimations();

    // Initialize category filter highlighting
    initCategoryFilter();
});

/**
 * Initialize parallax effect for the hero section
 */
function initParallax() {
    // Check if we have simpleParallax.js loaded
    if (typeof simpleParallax !== 'undefined') {
        // Find parallax elements
        const parallaxElements = document.querySelectorAll('.parallax-bg');
        if (parallaxElements.length > 0) {
            // Initialize simpleParallax
            new simpleParallax(parallaxElements, {
                delay: 0.6,
                orientation: 'down',
                scale: 1.3,
                overflow: true
            });
        }

        // Also apply to hero section backgrounds
        const heroBackgrounds = document.querySelectorAll('.bg-cover');
        if (heroBackgrounds.length > 0) {
            new simpleParallax(heroBackgrounds, {
                delay: 0.4,
                orientation: 'down',
                scale: 1.2,
                overflow: true
            });
        }
    } else {
        // Fallback to basic parallax effect
        const parallaxElement = document.querySelector('.parallax-bg');
        if (!parallaxElement) return;

        window.addEventListener('scroll', function() {
            const scrollPosition = window.scrollY;
            parallaxElement.style.transform = `translateY(${scrollPosition * 0.4}px)`;
        });
    }
}

/**
 * Initialize masonry layout for the blog grid
 * Note: This is a simple implementation. For more complex layouts,
 * consider using a library like Masonry.js
 */
function initMasonry() {
    // This is a placeholder for potential masonry implementation
    // For a simple grid layout, CSS Grid is often sufficient

    // If you want to implement a true masonry layout, you can use:
    // const grid = document.querySelector('.blog-grid');
    // if (grid && typeof Masonry !== 'undefined') {
    //     new Masonry(grid, {
    //         itemSelector: '.blog-card',
    //         columnWidth: '.blog-card',
    //         percentPosition: true
    //     });
    // }
}

/**
 * Initialize animations for elements
 */
function initAnimations() {
    const animateElements = document.querySelectorAll('.animate-on-scroll');

    const animateOnScroll = function() {
        animateElements.forEach(element => {
            const elementTop = element.getBoundingClientRect().top;
            const elementVisible = 150;

            if (elementTop < window.innerHeight - elementVisible) {
                const animation = element.dataset.animation || 'fadeIn';
                const delay = element.dataset.delay || '0';

                element.style.animationDelay = `${delay}ms`;
                element.classList.add(`animate-${animation}`);
            }
        });
    };

    // Run on load
    animateOnScroll();

    // Run on scroll
    window.addEventListener('scroll', animateOnScroll);
}

/**
 * Initialize category filter highlighting
 */
function initCategoryFilter() {
    const categoryLinks = document.querySelectorAll('.category-filter a');

    categoryLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            // Remove active class from all links
            categoryLinks.forEach(l => l.classList.remove('active'));

            // Add active class to clicked link
            this.classList.add('active');
        });
    });
}

/**
 * Initialize search functionality
 */
function initSearch() {
    const searchForm = document.querySelector('.search-form');
    const searchInput = document.querySelector('.search-input');

    if (!searchForm || !searchInput) return;

    // Add focus effects
    searchInput.addEventListener('focus', function() {
        searchForm.classList.add('search-focused');
    });

    searchInput.addEventListener('blur', function() {
        searchForm.classList.remove('search-focused');
    });
}
