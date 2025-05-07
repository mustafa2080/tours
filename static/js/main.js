/**
 * Main JavaScript file for Tourism Website
 */

document.addEventListener('alpine:init', () => {
    // Navbar component
    Alpine.data('navbar', () => ({
        open: false,
        langMenuOpen: false,
        userMenuOpen: false,
        
        toggle() {
            this.open = !this.open;
        },
        
        toggleLangMenu() {
            this.langMenuOpen = !this.langMenuOpen;
        },
        
        toggleUserMenu() {
            this.userMenuOpen = !this.userMenuOpen;
        },
        
        close() {
            this.open = false;
            this.langMenuOpen = false;
            this.userMenuOpen = false;
        }
    }));
    
    // Hero carousel component
    Alpine.data('heroCarousel', () => ({
        currentIndex: 0,
        items: [],
        autoplayInterval: null,
        
        init() {
            // Get all slides
            this.items = Array.from(this.$el.querySelectorAll('[data-carousel-item]'));
            
            if (this.items.length > 0) {
                // Show first slide
                this.goToSlide(0);
                
                // Start autoplay
                this.startAutoplay();
            }
        },
        
        startAutoplay() {
            this.autoplayInterval = setInterval(() => {
                this.next();
            }, 5000);
        },
        
        stopAutoplay() {
            if (this.autoplayInterval) {
                clearInterval(this.autoplayInterval);
            }
        },
        
        next() {
            this.goToSlide((this.currentIndex + 1) % this.items.length);
        },
        
        prev() {
            this.goToSlide((this.currentIndex - 1 + this.items.length) % this.items.length);
        },
        
        goToSlide(index) {
            // Hide all slides
            this.items.forEach((item, i) => {
                item.classList.add('hidden');
                item.setAttribute('aria-hidden', 'true');
            });
            
            // Show selected slide
            this.items[index].classList.remove('hidden');
            this.items[index].setAttribute('aria-hidden', 'false');
            
            this.currentIndex = index;
        }
    }));
    
    // Alert component
    Alpine.data('alert', () => ({
        show: true,
        
        close() {
            this.show = false;
        }
    }));
    
    // Language switcher component
    Alpine.data('languageSwitcher', () => ({
        open: false,
        currentLanguage: document.documentElement.lang || 'ar',
        languages: [
            { code: 'ar', name: 'العربية', dir: 'rtl' },
            { code: 'en', name: 'English', dir: 'ltr' },
            { code: 'fr', name: 'Français', dir: 'ltr' },
            { code: 'de', name: 'Deutsch', dir: 'ltr' }
        ],
        
        init() {
            // Set direction based on current language
            this.setDirection(this.currentLanguage);
        },
        
        setDirection(langCode) {
            const lang = this.languages.find(l => l.code === langCode);
            if (lang) {
                document.documentElement.dir = lang.dir;
                document.documentElement.lang = lang.code;
                
                if (lang.dir === 'rtl') {
                    document.documentElement.classList.add('rtl');
                } else {
                    document.documentElement.classList.remove('rtl');
                }
            }
        },
        
        toggle() {
            this.open = !this.open;
        },
        
        switchLanguage(langCode) {
            // Update language in cookies and redirect
            this.setLanguageCookie(langCode);
            this.setDirection(langCode);
            
            // Close dropdown
            this.open = false;
            
            // Refresh page to update language
            window.location.reload();
        },
        
        setLanguageCookie(langCode) {
            document.cookie = `django_language=${langCode}; path=/; max-age=31536000; SameSite=Lax`;
        }
    }));
});

// Initialize AlpineJS when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Check if service worker is supported
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('/static/js/service-worker.js')
            .then(registration => {
                console.log('Service Worker registered with scope:', registration.scope);
            })
            .catch(error => {
                console.error('Service Worker registration failed:', error);
            });
    }
});