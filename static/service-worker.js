const CACHE_NAME = "usalama-public-v1";
const OFFLINE_PAGE = "<!doctype html><html lang=\"fr\"><meta charset=\"utf-8\"><meta name=\"viewport\" content=\"width=device-width\"><title>Hors connexion</title><body><main><h1>Connexion indisponible</h1><p>Cette page n'a pas encore été enregistrée. Connecte-toi puis utilise le bouton « Enregistrer les guides hors connexion ».</p></main></body></html>";

function isCacheable(url) {
  return url.origin === self.location.origin && (
    url.pathname === "/" ||
    url.pathname === "/analyse/" ||
    url.pathname === "/bibliotheque/" ||
    url.pathname.startsWith("/bibliotheque/arnaque/") ||
    url.pathname === "/bibliotheque/urgence/" ||
    url.pathname.startsWith("/bibliotheque/urgence/") ||
    url.pathname === "/analyse/regles.json" ||
    url.pathname.startsWith("/static/")
  );
}

self.addEventListener("install", function (event) {
  event.waitUntil(self.skipWaiting());
});

self.addEventListener("activate", function (event) {
  event.waitUntil((async function () {
    const names = await caches.keys();
    await Promise.all(names.filter(function (name) {
      return name.startsWith("usalama-") && name !== CACHE_NAME;
    }).map(function (name) { return caches.delete(name); }));
    await self.clients.claim();
  })());
});

self.addEventListener("message", function (event) {
  if (!event.data || event.data.type !== "CACHE_URLS" || !Array.isArray(event.data.urls)) return;
  const port = event.ports[0];
  event.waitUntil((async function () {
    let ok = true;
    const cache = await caches.open(CACHE_NAME);
    for (const value of event.data.urls) {
      try {
        const url = new URL(value, self.location.origin);
        if (!isCacheable(url)) continue;
        const response = await fetch(url.href, { credentials: "same-origin" });
        if (!response.ok) {
          ok = false;
          continue;
        }
        await cache.put(url.href, response);
      } catch (error) {
        ok = false;
      }
    }
    if (port) port.postMessage({ ok: ok });
  })());
});

self.addEventListener("fetch", function (event) {
  const request = event.request;
  if (request.method !== "GET") return;
  const url = new URL(request.url);
  if (!isCacheable(url)) return;

  event.respondWith((async function () {
    const cache = await caches.open(CACHE_NAME);
    try {
      const response = await fetch(request);
      if (response.ok) await cache.put(request, response.clone());
      return response;
    } catch (error) {
      const cached = await cache.match(request);
      if (cached) return cached;
      if (request.mode === "navigate") {
        return new Response(OFFLINE_PAGE, {
          headers: { "Content-Type": "text/html; charset=utf-8" },
          status: 503,
        });
      }
      throw error;
    }
  })());
});
