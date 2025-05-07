/**
 * Cache Service for the Tourism Website
 * 
 * This service handles client-side caching of content
 * to improve performance and provide offline capabilities.
 */

document.addEventListener('alpine:init', () => {
    Alpine.data('cacheService', () => ({
        // Cache settings
        cacheEnabled: true,
        cacheDuration: 30 * 60 * 1000, // 30 minutes in milliseconds
        cachePrefix: 'tourism_cache_',
        
        /**
         * Initialize the cache service
         */
        init() {
            // Check if caching is supported
            if (!('localStorage' in window)) {
                this.cacheEnabled = false;
                console.warn('Local storage not supported. Caching disabled.');
            }
            
            // Clean expired cache items
            this.cleanExpiredCache();
        },
        
        /**
         * Get an item from cache
         * @param {string} key - Cache key
         * @returns {any|null} - Cached data or null if not found or expired
         */
        get(key) {
            if (!this.cacheEnabled) return null;
            
            const cacheKey = this.cachePrefix + key;
            const cachedItem = localStorage.getItem(cacheKey);
            
            if (!cachedItem) return null;
            
            try {
                const { data, expiry } = JSON.parse(cachedItem);
                
                // Check if cache has expired
                if (expiry < Date.now()) {
                    this.remove(key);
                    return null;
                }
                
                return data;
            } catch (error) {
                console.error('Error retrieving cache:', error);
                this.remove(key);
                return null;
            }
        },
        
        /**
         * Store an item in cache
         * @param {string} key - Cache key
         * @param {any} data - Data to cache
         * @param {number} [duration] - Custom cache duration in milliseconds
         */
        set(key, data, duration) {
            if (!this.cacheEnabled) return;
            
            const cacheKey = this.cachePrefix + key;
            const expiry = Date.now() + (duration || this.cacheDuration);
            
            try {
                localStorage.setItem(cacheKey, JSON.stringify({ data, expiry }));
            } catch (error) {
                console.error('Error setting cache:', error);
                
                // If storage is full, clear some space
                if (error.name === 'QuotaExceededError') {
                    this.clearOldestCacheItems();
                    
                    // Try again
                    try {
                        localStorage.setItem(cacheKey, JSON.stringify({ data, expiry }));
                    } catch (retryError) {
                        console.error('Failed to set cache after clearing space:', retryError);
                    }
                }
            }
        },
        
        /**
         * Remove an item from cache
         * @param {string} key - Cache key
         */
        remove(key) {
            if (!this.cacheEnabled) return;
            
            const cacheKey = this.cachePrefix + key;
            localStorage.removeItem(cacheKey);
        },
        
        /**
         * Clear all cached items for this application
         */
        clearAll() {
            if (!this.cacheEnabled) return;
            
            Object.keys(localStorage).forEach(key => {
                if (key.startsWith(this.cachePrefix)) {
                    localStorage.removeItem(key);
                }
            });
        },
        
        /**
         * Clean expired cache items
         */
        cleanExpiredCache() {
            if (!this.cacheEnabled) return;
            
            const now = Date.now();
            
            Object.keys(localStorage).forEach(key => {
                if (key.startsWith(this.cachePrefix)) {
                    try {
                        const { expiry } = JSON.parse(localStorage.getItem(key));
                        
                        if (expiry < now) {
                            localStorage.removeItem(key);
                        }
                    } catch (error) {
                        // Invalid cache item, remove it
                        localStorage.removeItem(key);
                    }
                }
            });
        },
        
        /**
         * Clear oldest cache items to free up space
         */
        clearOldestCacheItems() {
            if (!this.cacheEnabled) return;
            
            const cacheItems = [];
            
            // Collect all cache items with their expiry
            Object.keys(localStorage).forEach(key => {
                if (key.startsWith(this.cachePrefix)) {
                    try {
                        const { expiry } = JSON.parse(localStorage.getItem(key));
                        cacheItems.push({ key, expiry });
                    } catch (error) {
                        localStorage.removeItem(key);
                    }
                }
            });
            
            // Sort by expiry (oldest first)
            cacheItems.sort((a, b) => a.expiry - b.expiry);
            
            // Remove the oldest 20% of items
            const itemsToRemove = Math.max(1, Math.floor(cacheItems.length * 0.2));
            
            for (let i = 0; i < itemsToRemove; i++) {
                if (cacheItems[i]) {
                    localStorage.removeItem(cacheItems[i].key);
                }
            }
        }
    }));
});