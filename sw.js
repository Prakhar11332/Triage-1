/**
 * TriageAI – Custom Service Worker
 *
 * Strategy:
 *  - App Shell (HTML, JS, CSS, fonts): Cache-First
 *  - API / AI inference requests:      Network-First with cache fallback
 *
 * NOTE: vite-plugin-pwa (workbox) will INJECT its own precache manifest
 * into this file at build time via `injectManifest` mode, or generate
 * its own sw using `generateSW` (default). The vite.config.js uses
 * `generateSW` so Workbox manages precaching automatically.
 *
 * This file is kept here as a reference / override point. If you want
 * vite-plugin-pwa to USE this file directly, switch to `injectManifest`
 * strategy in vite.config.js and add the `self.__WB_MANIFEST` injection
 * point below.
 */

const CACHE_NAME = 'triageai-shell-v1'

// App shell files to cache on install
const APP_SHELL = [
  '/',
  '/index.html',
]

// ─── Install ────────────────────────────────────────────────────────────────
self.addEventListener('install', (event) => {
  console.log('[SW] Installing TriageAI service worker…')
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] Pre-caching app shell')
      return cache.addAll(APP_SHELL)
    })
  )
  self.skipWaiting()
})

// ─── Activate ───────────────────────────────────────────────────────────────
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating…')
  event.waitUntil(
    caches.keys().then((cacheNames) =>
      Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => {
            console.log('[SW] Deleting old cache:', name)
            return caches.delete(name)
          })
      )
    )
  )
  self.clients.claim()
})

// ─── Fetch ───────────────────────────────────────────────────────────────────
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)

  // Only handle same-origin GET requests
  if (request.method !== 'GET' || url.origin !== self.location.origin) return

  // Network-first for API calls (e.g. /api/*)
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request))
    return
  }

  // Cache-first for everything else (app shell, assets)
  event.respondWith(cacheFirst(request))
})

// ─── Strategies ──────────────────────────────────────────────────────────────

async function cacheFirst(request) {
  const cached = await caches.match(request)
  if (cached) return cached
  try {
    const response = await fetch(request)
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME)
      cache.put(request, response.clone())
    }
    return response
  } catch {
    // Return offline fallback for navigation requests
    if (request.mode === 'navigate') {
      const fallback = await caches.match('/')
      if (fallback) return fallback
    }
    return new Response('Offline – content unavailable', {
      status: 503,
      headers: { 'Content-Type': 'text/plain' },
    })
  }
}

async function networkFirst(request) {
  try {
    const response = await fetch(request)
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME)
      cache.put(request, response.clone())
    }
    return response
  } catch {
    const cached = await caches.match(request)
    if (cached) return cached
    return new Response(JSON.stringify({ error: 'offline' }), {
      status: 503,
      headers: { 'Content-Type': 'application/json' },
    })
  }
}
