(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  function normalize(str) {
    return (str || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .trim();
  }

  // ===== Serviços: Busca + filtros =====
  function initServicesPage() {
    const searchInput = $("#service-search");
    const levelSelect = $("#service-level");
    const scopeSelect = $("#service-scope");
    const countEl = $("#services-count");
    const clearBtn = $("#clear-filters");

    const items = $$(".service-item");
    if (!items.length) return;

    const chips = $$("[data-chip]");
    const categoryLinks = $$("[data-category-link]");

    // estado
    const state = {
      q: "",
      level: "",
      scope: "",
      category: "",
      featuredOnly: false,
    };

    // marca links externos
    items.forEach((li) => {
      const isExternal = li.dataset.external === "true";
      const link = li.querySelector("a");
      if (!link) return;

      if (isExternal) {
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        // opcional: adiciona indicador visual ↗ no final do título
        const title = li.querySelector("h3");
        if (title && !title.querySelector(".ext-indicator")) {
          const span = document.createElement("span");
          span.className = "ext-indicator ml-2 text-gray-400 group-hover:text-gray-600";
          span.setAttribute("aria-hidden", "true");
          span.textContent = "↗";
          title.appendChild(span);
        }
      }
    });

    function setActiveChip(name) {
      chips.forEach((btn) => {
        const active = btn.dataset.chip === name;
        btn.setAttribute("aria-pressed", active ? "true" : "false");
        btn.classList.toggle("bg-gray-900", active);
        btn.classList.toggle("text-white", active);
        btn.classList.toggle("border-gray-900", active);
      });
    }

    function clearChips() {
      chips.forEach((btn) => {
        btn.setAttribute("aria-pressed", "false");
        btn.classList.remove("bg-gray-900", "text-white", "border-gray-900");
      });
    }

    function applyFilters({ scrollToCategory = false } = {}) {
      const q = normalize(state.q);
      const level = normalize(state.level);
      const scope = normalize(state.scope);
      const category = normalize(state.category);

      let visibleCount = 0;

      items.forEach((li) => {
        const title = normalize(li.dataset.title);
        const cat = normalize(li.dataset.category);
        const lvl = normalize(li.dataset.level);
        const scp = normalize(li.dataset.scope);
        const featured = li.dataset.featured === "true";

        const matchQ =
          !q ||
          title.includes(q) ||
          normalize(li.textContent).includes(q);

        const matchLevel = !level || lvl === level;
        const matchScope = !scope || scp === scope;
        const matchCategory = !category || cat === category;
        const matchFeatured = !state.featuredOnly || featured;

        const show = matchQ && matchLevel && matchScope && matchCategory && matchFeatured;

        li.classList.toggle("hidden", !show);
        if (show) visibleCount += 1;
      });

      if (countEl) countEl.textContent = String(visibleCount);

      if (scrollToCategory && category) {
        const anchor = document.getElementById(`cat-${category}`);
        if (anchor) anchor.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    }

    // eventos
    if (searchInput) {
      searchInput.addEventListener("input", (e) => {
        state.q = e.target.value || "";
        applyFilters();
      });
    }

    if (levelSelect) {
      levelSelect.addEventListener("change", (e) => {
        state.level = e.target.value || "";
        applyFilters();
      });
    }

    if (scopeSelect) {
      scopeSelect.addEventListener("change", (e) => {
        state.scope = e.target.value || "";
        applyFilters();
      });
    }

    // chips (ex.: data-chip="featured" / "denuncias" / etc)
    chips.forEach((btn) => {
      btn.addEventListener("click", () => {
        const chip = btn.dataset.chip;

        // reset chip state
        state.featuredOnly = false;
        state.category = "";

        if (chip === "featured") {
          state.featuredOnly = true;
          setActiveChip("featured");
        } else {
          state.category = chip; // chip = categoria
          setActiveChip(chip);
        }

        applyFilters({ scrollToCategory: true });
      });
    });

    // links do aside (scroll + filtra)
    categoryLinks.forEach((a) => {
      a.addEventListener("click", (e) => {
        e.preventDefault();
        const cat = a.dataset.categoryLink;
        state.category = cat || "";
        state.featuredOnly = false;
        clearChips();
        applyFilters({ scrollToCategory: true });
      });
    });

    if (clearBtn) {
      clearBtn.addEventListener("click", () => {
        state.q = "";
        state.level = "";
        state.scope = "";
        state.category = "";
        state.featuredOnly = false;

        if (searchInput) searchInput.value = "";
        if (levelSelect) levelSelect.value = "";
        if (scopeSelect) scopeSelect.value = "";

        clearChips();
        applyFilters();
      });
    }

    // inicializa contagem
    applyFilters();
  }

  document.addEventListener("DOMContentLoaded", initServicesPage);
})();
