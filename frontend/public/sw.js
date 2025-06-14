// Service Worker for caching and performance optimization
const CACHE_NAME = 'local-producer-v1.0.0';
const API_CACHE_NAME = 'local-producer-api-v1.0.0';

// Assets to cache immediately
const STATIC_ASSETS = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  '/favicon.ico',
  '/images/placeholder.jpg',
  '/images/placeholder-product.jpg',
  '/images/placeholder-category.jpg'
];

// API endpoints to cache
const API_ENDPOINTS = [
  '/api/products',
  '/api/categories'
];

// Cache strategies
const CACHE_STRATEGIES = {
  // Cache first, then network (for static assets)
  CACHE_FIRST: 'cache-first',
  // Network first, then cache (for dynamic content)
  NETWORK_FIRST: 'network-first',
  // Stale while revalidate (for API responses)
  STALE_WHILE_REVALIDATE: 'stale-while-revalidate'
};

// Cache duration in milliseconds
const CACHE_DURATION = {
  STATIC: 7 * 24 * 60 * 60 * 1000, // 7 days
  API: 5 * 60 * 1000, // 5 minutes
  IMAGES: 24 * 60 * 60 * 1000 // 24 hours
};

// Install event - cache static assets
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker: Installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('📦 Service Worker: Caching static assets');
        return cache.addAll(STATIC_ASSETS);
      })
      .then(() => {
        console.log('✅ Service Worker: Installation complete');
        return self.skipWaiting();
      })
      .catch((error) => {
        console.error('❌ Service Worker: Installation failed', error);
      })
  );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
  console.log('🚀 Service Worker: Activating...');
  
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => {
        return Promise.all(
          cacheNames
            .filter((cacheName) => {
              // Remove old versions
              return cacheName !== CACHE_NAME && cacheName !== API_CACHE_NAME;
            })
            .map((cacheName) => {
              console.log('🗑️ Service Worker: Deleting old cache', cacheName);
              return caches.delete(cacheName);
            })
        );
      })
      .then(() => {
        console.log('✅ Service Worker: Activation complete');
        return self.clients.claim();
      })
  );
});

// Fetch event - implement caching strategies
self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Skip non-GET requests
  if (request.method !== 'GET') {
    return;
  }
  
  // Determine cache strategy based on request type
  if (isStaticAsset(url)) {
    event.respondWith(handleStaticAsset(request));
  } else if (isAPIRequest(url)) {
    event.respondWith(handleAPIRequest(request));
  } else if (isImageRequest(url)) {
    event.respondWith(handleImageRequest(request));
  } else {
    event.respondWith(handleOtherRequest(request));
  }
});

// Check if request is for a static asset
function isStaticAsset(url) {
  return url.pathname.startsWith('/static/') || 
         url.pathname.endsWith('.js') ||
         url.pathname.endsWith('.css') ||
         url.pathname.endsWith('.ico') ||
         url.pathname === '/manifest.json';
}

// Check if request is for API
function isAPIRequest(url) {
  return url.pathname.startsWith('/api/');
}

// Check if request is for an image
function isImageRequest(url) {
  return url.pathname.match(/\.(jpg|jpeg|png|gif|webp|svg)$/i);
}

// Handle static assets with cache-first strategy
async function handleStaticAsset(request) {
  try {
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      // Check if cache is still valid
      const cacheDate = new Date(cachedResponse.headers.get('date'));
      const now = new Date();
      
      if (now - cacheDate < CACHE_DURATION.STATIC) {
        console.log('📦 Service Worker: Serving from cache (static)', request.url);
        return cachedResponse;
      }
    }
    
    // Fetch from network and update cache
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
      console.log('🌐 Service Worker: Updated cache from network (static)', request.url);
    }
    
    return networkResponse;
  } catch (error) {
    console.error('❌ Service Worker: Error handling static asset', error);
    
    // Return cached version if available
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    
    // Return offline fallback
    return new Response('Asset not available offline', { status: 503 });
  }
}

// Handle API requests with stale-while-revalidate strategy
async function handleAPIRequest(request) {
  try {
    const cache = await caches.open(API_CACHE_NAME);
    const cachedResponse = await cache.match(request);
    
    // Start network request immediately
    const networkPromise = fetch(request.clone())
      .then(response => {
        if (response.ok) {
          // Update cache with new response
          cache.put(request, response.clone());
          console.log('🔄 Service Worker: Updated API cache', request.url);
        }
        return response;
      })
      .catch(error => {
        console.error('🌐 Service Worker: Network error for API', error);
        throw error;
      });
    
    // If we have cached data, return it immediately
    if (cachedResponse) {
      const cacheDate = new Date(cachedResponse.headers.get('date'));
      const now = new Date();
      
      // If cache is fresh, return it and update in background
      if (now - cacheDate < CACHE_DURATION.API) {
        console.log('📦 Service Worker: Serving fresh cache (API)', request.url);
        networkPromise.catch(() => {}); // Update cache in background
        return cachedResponse;
      }
      
      // If cache is stale, try network first but return cache if network fails
      try {
        const networkResponse = await networkPromise;
        console.log('🌐 Service Worker: Serving from network (API)', request.url);
        return networkResponse;
      } catch (error) {
        console.log('📦 Service Worker: Network failed, serving stale cache (API)', request.url);
        return cachedResponse;
      }
    }
    
    // No cache, wait for network
    console.log('🌐 Service Worker: No cache, waiting for network (API)', request.url);
    return await networkPromise;
    
  } catch (error) {
    console.error('❌ Service Worker: Error handling API request', error);
    
    // Return error response with Romanian message
    return new Response(
      JSON.stringify({
        success: false,
        message: 'Serviciul nu este disponibil momentan. Verificați conexiunea la internet.',
        error: 'SERVICE_UNAVAILABLE'
      }),
      {
        status: 503,
        headers: {
          'Content-Type': 'application/json; charset=utf-8'
        }
      }
    );
  }
}

// Handle image requests with cache-first strategy
async function handleImageRequest(request) {
  try {
    const cachedResponse = await caches.match(request);
    
    if (cachedResponse) {
      console.log('📦 Service Worker: Serving from cache (image)', request.url);
      return cachedResponse;
    }
    
    // Fetch from network
    const networkResponse = await fetch(request);
    
    if (networkResponse.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
      console.log('🌐 Service Worker: Cached new image', request.url);
    }
    
    return networkResponse;
  } catch (error) {
    console.error('❌ Service Worker: Error handling image', error);
    
    // Return placeholder image for failed image loads
    return fetch('/images/placeholder.jpg').catch(() => {
      return new Response('', { status: 404 });
    });
  }
}

// Handle other requests with network-first strategy
async function handleOtherRequest(request) {
  try {
    // Try network first
    const networkResponse = await fetch(request);
    
    // Cache successful responses for HTML pages
    if (networkResponse.ok && request.headers.get('accept')?.includes('text/html')) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, networkResponse.clone());
    }
    
    return networkResponse;
  } catch (error) {
    console.error('❌ Service Worker: Network error', error);
    
    // Try to serve from cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      console.log('📦 Service Worker: Serving from cache (fallback)', request.url);
      return cachedResponse;
    }
    
    // Return offline page for navigation requests
    if (request.mode === 'navigate') {
      return caches.match('/') || new Response('Offline', { status: 503 });
    }
    
    throw error;
  }
}

// Background sync for offline actions
self.addEventListener('sync', (event) => {
  console.log('🔄 Service Worker: Background sync triggered', event.tag);
  
  if (event.tag === 'background-sync-cart') {
    event.waitUntil(syncCartActions());
  } else if (event.tag === 'background-sync-analytics') {
    event.waitUntil(syncAnalytics());
  }
});

// Sync cart actions when back online
async function syncCartActions() {
  try {
    // Get pending cart actions from IndexedDB
    const pendingActions = await getPendingCartActions();
    
    for (const action of pendingActions) {
      try {
        // Replay the action
        await fetch(action.url, {
          method: action.method,
          headers: action.headers,
          body: action.body
        });
        
        // Remove from pending actions
        await removePendingCartAction(action.id);
        console.log('✅ Service Worker: Synced cart action', action.id);
      } catch (error) {
        console.error('❌ Service Worker: Failed to sync cart action', error);
      }
    }
  } catch (error) {
    console.error('❌ Service Worker: Error syncing cart actions', error);
  }
}

// Sync analytics when back online
async function syncAnalytics() {
  try {
    // Get pending analytics events
    const pendingEvents = await getPendingAnalytics();
    
    for (const event of pendingEvents) {
      try {
        // Send analytics event
        await fetch('/api/analytics', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(event)
        });
        
        // Remove from pending events
        await removePendingAnalytic(event.id);
        console.log('✅ Service Worker: Synced analytics event', event.id);
      } catch (error) {
        console.error('❌ Service Worker: Failed to sync analytics', error);
      }
    }
  } catch (error) {
    console.error('❌ Service Worker: Error syncing analytics', error);
  }
}

// Message handling for cache management
self.addEventListener('message', (event) => {
  const { type, payload } = event.data;
  
  switch (type) {
    case 'CACHE_INVALIDATE':
      handleCacheInvalidation(payload);
      break;
    case 'CACHE_WARM':
      handleCacheWarming(payload);
      break;
    case 'CACHE_STATS':
      handleCacheStats(event);
      break;
    default:
      console.log('🔔 Service Worker: Unknown message type', type);
  }
});

// Handle cache invalidation
async function handleCacheInvalidation(pattern) {
  try {
    const cacheNames = await caches.keys();
    
    for (const cacheName of cacheNames) {
      const cache = await caches.open(cacheName);
      const requests = await cache.keys();
      
      for (const request of requests) {
        if (request.url.includes(pattern)) {
          await cache.delete(request);
          console.log('🗑️ Service Worker: Invalidated cache', request.url);
        }
      }
    }
  } catch (error) {
    console.error('❌ Service Worker: Error invalidating cache', error);
  }
}

// Handle cache warming
async function handleCacheWarming(urls) {
  try {
    const cache = await caches.open(CACHE_NAME);
    
    for (const url of urls) {
      try {
        const response = await fetch(url);
        if (response.ok) {
          await cache.put(url, response);
          console.log('🔥 Service Worker: Warmed cache', url);
        }
      } catch (error) {
        console.error('❌ Service Worker: Error warming cache for', url, error);
      }
    }
  } catch (error) {
    console.error('❌ Service Worker: Error warming cache', error);
  }
}

// Handle cache statistics request
async function handleCacheStats(event) {
  try {
    const cacheNames = await caches.keys();
    const stats = {};
    
    for (const cacheName of cacheNames) {
      const cache = await caches.open(cacheName);
      const requests = await cache.keys();
      stats[cacheName] = requests.length;
    }
    
    event.ports[0].postMessage({
      type: 'CACHE_STATS_RESPONSE',
      payload: stats
    });
  } catch (error) {
    console.error('❌ Service Worker: Error getting cache stats', error);
    event.ports[0].postMessage({
      type: 'CACHE_STATS_ERROR',
      payload: error.message
    });
  }
}

// Helper functions for IndexedDB operations
async function getPendingCartActions() {
  // Implementation for getting pending cart actions from IndexedDB
  return [];
}

async function removePendingCartAction(id) {
  // Implementation for removing cart action from IndexedDB
}

async function getPendingAnalytics() {
  // Implementation for getting pending analytics from IndexedDB
  return [];
}

async function removePendingAnalytic(id) {
  // Implementation for removing analytics event from IndexedDB
}

console.log('🎯 Service Worker: Loaded successfully');