const CACHE_NAME = "eyemax-cache-v1";
const ASSETS_TO_CACHE = [
  "/",
  "/logo.png",
  "/icon.png",
  "/manifest.json"
];

// Instalar el Service Worker y almacenar en caché los activos estáticos clave
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log("[Service Worker] Almacenando caché de assets principales");
        return cache.addAll(ASSETS_TO_CACHE);
      })
      .then(() => self.skipWaiting())
  );
});

// Activar el Service Worker y limpiar cachés antiguas
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cache => {
          if (cache !== CACHE_NAME) {
            console.log("[Service Worker] Eliminando caché antigua:", cache);
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Interceptar peticiones y aplicar la estrategia stale-while-revalidate para assets estáticos
self.addEventListener("fetch", event => {
  // Solo interceptar peticiones GET locales
  if (event.request.method !== "GET") return;
  
  const url = new URL(event.request.url);
  
  // Evitar interceptar llamadas a la API (deben ir directo a la red)
  if (url.pathname.startsWith("/api/")) {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(cachedResponse => {
        if (cachedResponse) {
          // Si está en caché, la retornamos pero intentamos actualizarla en segundo plano
          fetch(event.request).then(networkResponse => {
            if (networkResponse.status === 200) {
              caches.open(CACHE_NAME).then(cache => cache.put(event.request, networkResponse));
            }
          }).catch(() => {});
          return cachedResponse;
        }

        return fetch(event.request).then(networkResponse => {
          // Guardar dinámicamente recursos en caché si la respuesta es exitosa
          if (networkResponse.status === 200 && networkResponse.type === "basic") {
            const responseToCache = networkResponse.clone();
            caches.open(CACHE_NAME).then(cache => {
              cache.put(event.request, responseToCache);
            });
          }
          return networkResponse;
        }).catch(err => {
          console.error("[Service Worker] Error al buscar en la red:", err);
        });
      })
  );
});
