(() => {
  /* =========================================================
     Helpers
  ========================================================= */
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const isFn = (v) => typeof v === "function";

  const getCssMs = (varName, fallbackMs) => {
    const v = getComputedStyle(document.documentElement).getPropertyValue(varName).trim();
    const n = parseFloat(v);
    return Number.isFinite(n) ? n : fallbackMs;
  };

  const waitForTransition = (el, fallbackMs) =>
    new Promise((resolve) => {
      let done = false;

      const finish = () => {
        if (done) return;
        done = true;
        el.removeEventListener("transitionend", onEnd);
        resolve();
      };

      const onEnd = (e) => {
        if (e.target === el) finish();
      };

      el.addEventListener("transitionend", onEnd);
      window.setTimeout(finish, fallbackMs);
    });

  /* =========================================================
     Global handlers registry (reduz listeners duplicados)
  ========================================================= */
  const globalHandlers = {
    onDocClick: [],
    onDocKeydown: [],
  };

  const addDocClick = (fn) => globalHandlers.onDocClick.push(fn);
  const addDocKeydown = (fn) => globalHandlers.onDocKeydown.push(fn);

  document.addEventListener("click", (e) => {
    globalHandlers.onDocClick.forEach((fn) => fn(e));
  });

  document.addEventListener("keydown", (e) => {
    globalHandlers.onDocKeydown.forEach((fn) => fn(e));
  });

  /* =========================================================
     1) Ano no footer
  ========================================================= */
  (() => {
    const yearEl = $("#year");
    if (yearEl) yearEl.textContent = String(new Date().getFullYear());
  })();

  /* =========================================================
     2) Menu mobile (a11y + animação) + FIX sticky (portal p/ body)
  ========================================================= */
  const mobileMenu = (() => {
    const btn = $("[data-menu-button]");
    const panel = $("[data-menu-panel]");
    const overlay = $("[data-menu-overlay]");
    const closeBtn = $("[data-menu-close]");
    if (!btn || !panel || !overlay) return null;

    const root = document.documentElement;
    const slowMs = getCssMs("--t-slow", 320);

    let lastFocus = null;

    const focusableSelector =
      'a[href], button:not([disabled]), input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])';

    const getFocusable = () => $$(focusableSelector, panel);
    const isOpen = () => btn.getAttribute("aria-expanded") === "true";

    // --- FIX sticky: mover overlay/panel pro body ao abrir (evita stacking/transform do header)
    const originalParents = {
      panelParent: panel.parentElement,
      overlayParent: overlay.parentElement,
      panelNext: panel.nextSibling,
      overlayNext: overlay.nextSibling,
    };

    const portalToBody = () => {
      if (panel.parentElement !== document.body) document.body.appendChild(panel);
      if (overlay.parentElement !== document.body) document.body.appendChild(overlay);
    };

    const restoreParents = () => {
      const { panelParent, overlayParent, panelNext, overlayNext } = originalParents;

      if (panelParent) {
        if (panelNext) panelParent.insertBefore(panel, panelNext);
        else panelParent.appendChild(panel);
      }
      if (overlayParent) {
        if (overlayNext) overlayParent.insertBefore(overlay, overlayNext);
        else overlayParent.appendChild(overlay);
      }
    };

    const open = () => {
      if (isOpen()) return;

      // fecha dropdowns/menus abertos do header ao abrir menu mobile
      if (isFn(window.__mpfCloseAllDropdowns)) window.__mpfCloseAllDropdowns();
      if (isFn(window.__mpfCloseMoreMenu)) window.__mpfCloseMoreMenu();

      lastFocus = document.activeElement;

      // ✅ portaliza primeiro (evita sticky/transform “sumir”)
      portalToBody();

      panel.hidden = false;
      overlay.hidden = false;

      // reflow
      // eslint-disable-next-line no-unused-expressions
      panel.offsetHeight;

      btn.setAttribute("aria-expanded", "true");
      btn.setAttribute("aria-label", "Menu aberto");
      root.classList.add("menu-open");
      document.body.style.overflow = "hidden";

      const focusables = getFocusable();
      const target = closeBtn || focusables[0] || panel;
      target.focus();
    };

    const close = async () => {
      if (!isOpen()) return;

      btn.setAttribute("aria-expanded", "false");
      btn.setAttribute("aria-label", "Abrir menu");
      root.classList.remove("menu-open");
      document.body.style.overflow = "";

      await waitForTransition(panel, slowMs);

      panel.hidden = true;
      overlay.hidden = true;

      // ✅ devolve pro lugar original (mantém DOM do header organizado)
      restoreParents();

      if (lastFocus && isFn(lastFocus.focus)) lastFocus.focus();
    };

    const toggle = () => (isOpen() ? close() : open());

    const trapFocus = (e) => {
      if (!isOpen() || e.key !== "Tab") return;

      const focusables = getFocusable();
      if (!focusables.length) return;

      const first = focusables[0];
      const last = focusables[focusables.length - 1];

      if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
      } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
      }
    };

    btn.addEventListener("click", toggle);
    overlay.addEventListener("click", close);
    if (closeBtn) closeBtn.addEventListener("click", close);

    addDocKeydown((e) => {
      if (e.key === "Escape" && isOpen()) close();
      trapFocus(e);
    });

    return { open, close, isOpen };
  })();

  /* =========================================================
     3) Contraste (switch)
  ========================================================= */
  (() => {
    const buttons = $$("[data-contrast-toggle]");
    if (!buttons.length) return;

    const storageKey = "mpf-contrast";

    const setContrast = (enabled) => {
      document.body.classList.toggle("hc", enabled);
      buttons.forEach((b) => b.setAttribute("aria-checked", String(enabled)));
      localStorage.setItem(storageKey, enabled ? "1" : "0");
    };

    if (localStorage.getItem(storageKey) === "1") setContrast(true);

    buttons.forEach((b) => {
      b.addEventListener("click", () => {
        setContrast(!document.body.classList.contains("hc"));
      });
    });
  })();

  /* =========================================================
     4) Tamanho da fonte (A-/A/A+)
  ========================================================= */
  (() => {
    const buttons = $$("[data-font]");
    if (!buttons.length) return;

    const storageKey = "mpf-font-scale";
    const min = 14;
    const max = 20;
    const defaultSize = 16;

    const getCurrentBase = () => {
      const computed = getComputedStyle(document.documentElement).fontSize;
      return Math.round(parseFloat(computed));
    };

    const setBaseFont = (px) => {
      const clamped = Math.max(min, Math.min(max, px));
      document.documentElement.style.setProperty("--base-font-size", `${clamped}px`);
      localStorage.setItem(storageKey, String(clamped));
    };

    const saved = localStorage.getItem(storageKey);
    if (saved) setBaseFont(parseInt(saved, 10));

    buttons.forEach((b) => {
      b.addEventListener("click", () => {
        const action = b.getAttribute("data-font");
        const current = getCurrentBase();

        if (action === "increase") setBaseFont(current + 1);
        if (action === "decrease") setBaseFont(current - 1);
        if (action === "reset") setBaseFont(defaultSize);
      });
    });
  })();

  /* =========================================================
     4.5) Accordion genérico (mobile e desktop nível 2)
  ========================================================= */
  (() => {
    const init = () => {
      const buttons = $$("[data-acc-button]");
      if (!buttons.length) return;

      const getPanel = (btn) => {
        const id = btn.getAttribute("data-acc-button");
        return id ? document.getElementById(id) : null;
      };

      const getScope = (btn) =>
        btn.closest("[data-acc-panel]") ||
        btn.closest("[data-dd-menu]") ||
        btn.closest("[data-menu-panel]") ||
        btn.parentElement;

      const closeBtn = (btn) => {
        const panel = getPanel(btn);
        btn.setAttribute("aria-expanded", "false");
        if (panel) panel.hidden = true;
      };

      const openBtn = (btn) => {
        const panel = getPanel(btn);
        btn.setAttribute("aria-expanded", "true");
        if (panel) panel.hidden = false;
      };

      const closeOthersInScope = (btn) => {
        const scope = getScope(btn);
        if (!scope) return;
        const others = $$("[data-acc-button]", scope).filter((b) => b !== btn);
        others.forEach(closeBtn);
      };

      // garante fechado no load
      buttons.forEach(closeBtn);

      buttons.forEach((btn) => {
        btn.addEventListener("click", (e) => {
          e.stopPropagation();
          const isOpen = btn.getAttribute("aria-expanded") === "true";

          if (isOpen) return closeBtn(btn);

          closeOthersInScope(btn);
          openBtn(btn);
        });
      });
    };

    if (document.readyState === "loading") {
      document.addEventListener("DOMContentLoaded", init, { once: true });
    } else {
      init();
    }
  })();

  /* =========================================================
     5) “Mais” no menu desktop (overflow → dropdown)
  ========================================================= */
  const moreMenuModule = (() => {
    const nav = document.querySelector('nav[aria-label="Navegação principal"]');
    if (!nav) return null;

    const ul = nav.querySelector("ul");
    const moreItem = ul?.querySelector("[data-more-item]");
    const moreBtn = ul?.querySelector("[data-more-button]");
    const moreMenu = ul?.querySelector("[data-more-menu]");
    if (!ul || !moreItem || !moreBtn || !moreMenu) return null;

    const navVisible = () => getComputedStyle(nav).display !== "none";
    const isOverflowing = () => ul.scrollWidth > ul.clientWidth + 1;

    const close = () => {
      moreMenu.hidden = true;
      moreBtn.setAttribute("aria-expanded", "false");
    };

    const open = () => {
      if (isFn(window.__mpfCloseAllDropdowns)) window.__mpfCloseAllDropdowns();
      moreMenu.hidden = false;
      moreBtn.setAttribute("aria-expanded", "true");
    };

    window.__mpfCloseMoreMenu = close;

    moreBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      const expanded = moreBtn.getAttribute("aria-expanded") === "true";
      expanded ? close() : open();
    });

    addDocClick((e) => {
      if (!moreItem.contains(e.target)) close();
    });

    addDocKeydown((e) => {
      if (e.key === "Escape") close();
    });

    const putBackOverflowLinks = () => {
      const links = Array.from(moreMenu.querySelectorAll("a"));
      links.forEach((a) => {
        a.removeAttribute("role");
        const li = document.createElement("li");
        li.appendChild(a);
        ul.insertBefore(li, moreItem);
      });
      moreMenu.innerHTML = "";
    };

    const getRealItems = () => Array.from(ul.children).filter((li) => li !== moreItem);

    const moveLastToMore = () => {
      const items = getRealItems();
      if (items.length <= 2) return false;

      const li = items[items.length - 1];
      if (!li) return false;

      const link = li.querySelector("a");
      li.remove();

      if (!link) return true;

      const menuLi = document.createElement("li");
      menuLi.setAttribute("role", "none");
      link.setAttribute("role", "menuitem");
      menuLi.appendChild(link);
      moreMenu.prepend(menuLi);

      return true;
    };

    const rebuild = () => {
      close();
      putBackOverflowLinks();

      moreItem.hidden = true;
      moreMenu.hidden = true;

      if (!navVisible()) return;
      if (!isOverflowing()) return;

      moreItem.hidden = false;

      while (isOverflowing()) {
        const moved = moveLastToMore();
        if (!moved) break;
      }

      if (moreMenu.children.length === 0) {
        moreItem.hidden = true;
        close();
      }
    };

    const ro = new ResizeObserver(rebuild);
    ro.observe(ul);

    window.addEventListener("load", rebuild);
    if (document.fonts && isFn(document.fonts.ready?.then)) {
      document.fonts.ready.then(rebuild).catch(() => {});
    }

    return { close, open, rebuild };
  })();

  /* =========================================================
     6) Dropdowns genéricos ([data-dd-root]) com hierarquia
  ========================================================= */
  (() => {
    const roots = $$("[data-dd-root]");
    if (!roots.length) return;

    const getParts = (root) => ({
      btn: root.querySelector(":scope > [data-dd-button]"),
      menu: root.querySelector(":scope > [data-dd-menu]"),
    });

    const closeRoot = (root) => {
      const { btn, menu } = getParts(root);
      if (!btn || !menu) return;
      menu.hidden = true;
      btn.setAttribute("aria-expanded", "false");
    };

    const openRoot = (root) => {
      const { btn, menu } = getParts(root);
      if (!btn || !menu) return;
      menu.hidden = false;
      btn.setAttribute("aria-expanded", "true");
    };

    const isOpen = (root) => {
      const { btn } = getParts(root);
      return btn?.getAttribute("aria-expanded") === "true";
    };

    const getKeepSet = (root) => {
      const keep = new Set();
      let el = root;
      while (el) {
        if (el.matches?.("[data-dd-root]")) keep.add(el);
        el = el.parentElement;
      }
      return keep;
    };

    const closeAllExcept = (keepSet = null) => {
      roots.forEach((r) => {
        if (keepSet && keepSet.has(r)) return;
        closeRoot(r);
      });
    };

    window.__mpfCloseAllDropdowns = () => closeAllExcept(null);

    roots.forEach((root) => {
      const { btn, menu } = getParts(root);
      if (!btn || !menu) return;

      btn.addEventListener("click", (e) => {
        e.stopPropagation();

        if (isFn(window.__mpfCloseMoreMenu)) window.__mpfCloseMoreMenu();

        const willOpen = !isOpen(root);
        const keepSet = getKeepSet(root);

        closeAllExcept(keepSet);

        if (willOpen) openRoot(root);
        else closeRoot(root);
      });
    });

    // impedir clique interno de fechar dropdown (sem bloquear links)
    roots.forEach((root) => {
      const menu = root.querySelector(":scope > [data-dd-menu]");
      if (!menu) return;

      menu.addEventListener("click", (e) => {
        if (e.target.closest("a[href]")) return;
        if (e.target.closest("[data-acc-button]")) return;
        e.stopPropagation();
      });
    });

    addDocClick(() => closeAllExcept(null));

    addDocKeydown((e) => {
      if (e.key === "Escape") closeAllExcept(null);
    });
  })();

  /* =========================================================
     7) STICKY HEADER — entrada suave / saída rápida (UX-first)
  ========================================================= */
  (() => {
    const header = document.querySelector("#site-header[data-sticky]");
    if (!header) return;

    const topbar = header.querySelector(".mpf-topbar");

    // cria spacer para evitar “buraco”
    let spacer = document.querySelector("#header-spacer");
    if (!spacer) {
      spacer = document.createElement("div");
      spacer.id = "header-spacer";
      header.insertAdjacentElement("afterend", spacer);
    }

    let isSticky = false;
    let stickyTimer = null;
    let lastScrollY = window.scrollY || 0;

    const STICKY_DELAY = 500;
    const EXIT_BUFFER_MULTIPLIER = 2;

    const getHeights = () => {
      const full = header.offsetHeight;
      const topbarH = topbar ? topbar.offsetHeight : 0;
      const stickyH = Math.max(0, full - topbarH);
      return { full, stickyH };
    };

    const enableSticky = () => {
      if (isSticky) return;
      isSticky = true;

      const { stickyH } = getHeights();
      spacer.style.height = `${stickyH}px`;

      header.classList.remove("is-leaving");
      header.classList.add("is-sticky");

      header.offsetHeight;
      header.classList.add("is-sticky--shown");
    };

    const disableSticky = () => {
      if (!isSticky) return;
      isSticky = false;

      header.classList.add("is-leaving");
      header.classList.remove("is-sticky--shown");

      const onEnd = () => {
        header.classList.remove("is-sticky");
        header.classList.remove("is-leaving");
        spacer.style.height = "0px";
        header.removeEventListener("transitionend", onEnd);
      };

      header.addEventListener("transitionend", onEnd);
    };

    const scheduleSticky = () => {
      if (stickyTimer || isSticky) return;
      stickyTimer = setTimeout(() => {
        enableSticky();
        stickyTimer = null;
      }, STICKY_DELAY);
    };

    const cancelStickyTimer = () => {
      if (!stickyTimer) return;
      clearTimeout(stickyTimer);
      stickyTimer = null;
    };

    const onScroll = () => {
      const y = window.scrollY || 0;
      const goingUp = y < lastScrollY;
      lastScrollY = y;

      const { full } = getHeights();

      if (y > 2) document.documentElement.classList.add("is-scrolling");
      else document.documentElement.classList.remove("is-scrolling");

      if (y > full && !goingUp) scheduleSticky();
      else cancelStickyTimer();

      if (isSticky && goingUp && y < full * EXIT_BUFFER_MULTIPLIER) {
        cancelStickyTimer();
        disableSticky();
      }
    };

    window.addEventListener("scroll", onScroll, { passive: true });

    window.addEventListener("resize", () => {
      if (!isSticky) return;
      const { stickyH } = getHeights();
      spacer.style.height = `${stickyH}px`;
    });

    onScroll();
  })();
})();
