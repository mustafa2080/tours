/**
 * Service Worker for Tourism Website
 * Provides offline functionality and caching
 */

// Cache name - update version to force cache refresh
const CACHE_NAME = 'tourism-cache-v1';

// Resources to cache on install
const INITIAL_CACHED_RESOURCES = [
    '/',
    '/static/css/style.css',
    '/static/js/main.js',
    '/static/js/cache-service.js',
    '/static/js/alpine.min.js'
];

// Install event - cache initial resources
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Caching initial resources');
                return cache.addAll(INITIAL_CACHED_RESOURCES);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.filter(cacheName => {
                    return cacheName.startsWith('tourism-cache-') && cacheName !== CACHE_NAME;
                }).map(cacheName => {
                    console.log('Deleting old cache:', cacheName);
                    return caches.delete(cacheName);
                })
            );
        })
    );
});

// Fetch event - serve from cache or network
self.addEventListener('fetch', event => {
    // Skip for API requests and admin pages
    if (event.request.url.includes('/api/') || 
        event.request.url.includes('/admin/') || 
        event.request.url.includes('chrome-extension://')) {
        return;
    }
    
    // Handle GET requests only
    if (event.request.method !== 'GET') {
        return;
    }
    
    event.respondWith(
        caches.match(event.request)
            .then(cachedResponse => {
                // Return cached response if available
                if (cachedResponse) {
                    return cachedResponse;
                }
                
                // Otherwise fetch from network
                return fetch(event.request)
                    .then(response => {
                        // Don't cache if not a valid response
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }
                        
                        // Clone the response as it can only be consumed once
                        const responseToCache = response.clone();
                        
                        // Cache the response for future use
                        caches.open(CACHE_NAME)
                            .then(cache => {
                                cache.put(event.request, responseToCache);
                            });
                        
                        return response;
                    })
                    .catch(error => {
                        // If fetch fails (offline), try to return the cached home page
                        if (event.request.mode === 'navigate') {
                            return caches.match('/');
                        }
                        
                        console.error('Fetch failed:', error);
                        return new Response('Network error', { status: 408, headers: { 'Content-Type': 'text/plain' } });
                    });
            })
    );
});