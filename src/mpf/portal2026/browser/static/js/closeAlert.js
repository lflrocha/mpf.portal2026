(function () {
  function getStorage() {
    try {
      localStorage.setItem("__test__", "1");
      localStorage.removeItem("__test__");
      return localStorage;
    } catch (e) {
      try {
        sessionStorage.setItem("__test__", "1");
        sessionStorage.removeItem("__test__");
        return sessionStorage;
      } catch (e) {
        return null;
      }
    }
  }

  function initDismissibleAlert(alertEl) {
    if (!alertEl) return;

    var key =
      alertEl.getAttribute("data-alert-key") ||
      alertEl.id ||
      "mpf_alert";

    var storageKey = "dismissed:" + key;
    var storage = getStorage();

    // Já foi fechado anteriormente
    if (storage && storage.getItem(storageKey) === "1") {
      alertEl.style.display = "none";
      return;
    }

    var closeBtn = alertEl.querySelector("[data-alert-close]");
    if (!closeBtn) return;

    closeBtn.addEventListener("click", function () {
      alertEl.style.display = "none";

      // Se localStorage/sessionStorage estiver disponível
      if (storage) {
        storage.setItem(storageKey, "1");
      }
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    initDismissibleAlert(
      document.getElementById("mpf-alert-transition")
    );
  });
})();
