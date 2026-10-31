(function () {
  const serviceWorkerRegistration = "serviceWorker" in navigator
    ? navigator.serviceWorker.register("/sw.js")
    : null;
  if (serviceWorkerRegistration) {
    serviceWorkerRegistration.catch(function (error) {
      console.error("USALAMA service worker registration failed.", error);
    });
  }

  document.querySelectorAll("[data-cache-offline]").forEach(function (button) {
    button.addEventListener("click", async function () {
      const output = button.parentElement.querySelector("output");
      if (!("serviceWorker" in navigator)) {
        output.textContent = "Le mode hors connexion n'est pas disponible dans ce navigateur.";
        return;
      }

      try {
        await serviceWorkerRegistration;
        const registration = await navigator.serviceWorker.ready;
        const worker = registration.active;
        if (!worker) {
          output.textContent = "Impossible d'activer le mode hors connexion.";
          return;
        }

        const urls = Array.from(document.querySelectorAll(".links a[href]"))
          .map(function (link) { return link.href; });
        const channel = new MessageChannel();
        channel.port1.onmessage = function (event) {
          output.textContent = event.data && event.data.ok
            ? "Les guides affichés sont disponibles hors connexion."
            : "Certains guides n'ont pas pu être enregistrés. Vérifie ta connexion et réessaie.";
        };
        worker.postMessage({ type: "CACHE_URLS", urls: urls }, [channel.port2]);
      } catch (error) {
        output.textContent = "Impossible d'activer le mode hors connexion.";
      }
    });
  });
})();
