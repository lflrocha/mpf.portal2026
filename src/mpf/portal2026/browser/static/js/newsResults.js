/* mpf-noticias.js
   ✅ UF + Órgão (SEM Região)
   ✅ Lista completa de Órgãos (igual ao select do MPF)
   ✅ Lista do aside (sticky) + dropdown mobile
   ✅ Busca por palavra-chave (título + resumo do card)
   ✅ Categoria
   ✅ Ordenação por data (data-date="YYYY-MM-DD")
   ✅ Toggle Cards/Lista (desktop) com localStorage
*/

(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  // ====== LISTA DE ÓRGÃOS (igual ao select do MPF atual) ======
  const ORGAOS_MPF_ATUAL = [
    { id: "/portal/rs", label: "Procuradoria da República no Rio Grande do Sul" },
    { id: "/portal/regiao1", label: "Procuradoria Regional da República da 1ª Região" },
    { id: "/portal/presp", label: "Procuradoria Regional Eleitoral em São Paulo" },
    { id: "/portal/al", label: "Procuradoria da República em Alagoas" },
    { id: "/portal/ac", label: "Procuradoria da República no Acre" },
    { id: "/portal/rj", label: "Procuradoria da República no Rio de Janeiro" },
    { id: "/portal/regiao6", label: "MPF-MG de 2º Grau" },
    { id: "/portal/preal", label: "Procuradoria Regional Eleitoral em Alagoas" },
    { id: "/portal/pgr", label: "Procuradoria-Geral da República" },
    { id: "/portal/preap", label: "Procuradoria Regional Eleitoral no Amapá" },
    { id: "/portal/predf", label: "Procuradoria Regional Eleitoral no Distrito Federal" },
    { id: "/portal/prems", label: "Procuradoria Regional Eleitoral no Mato Grosso do Sul" },
    { id: "/portal/ap", label: "Procuradoria da República no Amapá" },
    { id: "/portal/prepa", label: "Procuradoria Regional Eleitoral no Pará" },
    { id: "/portal/regiao3", label: "Procuradoria Regional da República da 3ª Região" },
    { id: "/portal/mt", label: "Ministério Público Federal em Mato Grosso" },
    { id: "/portal/premt", label: "Procuradoria Regional Eleitoral em Mato Grosso" },
    { id: "/portal/prego", label: "Procuradoria Regional Eleitoral em Goiás" },
    { id: "/portal/prero", label: "Procuradoria Regional Eleitoral em Rondônia" },
    { id: "/portal/pge", label: "Procuradoria-Geral Eleitoral" },
    { id: "/portal/ba", label: "Procuradoria da República na Bahia" },
    { id: "/portal/rr", label: "Procuradoria da República em Roraima" },
    { id: "/portal/prerj", label: "Procuradoria Regional Eleitoral no Rio de Janeiro" },
    { id: "/portal/regiao5", label: "Procuradoria Regional da República da 5ª Região" },
    { id: "/portal/prepr", label: "Procuradoria Regional Eleitoral no Paraná" },
    { id: "/portal/sc", label: "Procuradoria da República em Santa Catarina" },
    { id: "/portal/prese", label: "Procuradoria Regional Eleitoral em Sergipe" },
    { id: "/portal/pi", label: "Procuradoria da República no Piauí" },
    { id: "/portal/preac", label: "Procuradoria Regional Eleitoral no Acre" },
    { id: "/portal/se", label: "Procuradoria da República em Sergipe" },
    { id: "/portal/ms", label: "Procuradoria da República em Mato Grosso do Sul" },
    { id: "/portal/es", label: "Procuradoria da República no Espírito Santo" },
    { id: "/portal/prern", label: "Procuradoria Regional Eleitoral no Rio Grande do Norte" },
    { id: "/portal/sp", label: "Procuradoria da República em São Paulo" },
    { id: "/portal/prepb", label: "Procuradoria Regional Eleitoral na Paraíba" },
    { id: "/portal/ce", label: "Procuradoria da República no Ceará" },
    { id: "/portal/preto", label: "Procuradoria Regional Eleitoral no Tocantins" },
    { id: "/portal/rn", label: "Procuradoria da República no Rio Grande do Norte" },
    { id: "/portal/pa", label: "Procuradoria da República no Pará" },
    { id: "/portal/prees", label: "Procuradoria Regional Eleitoral no Espírito Santo" },
    { id: "/portal/prece", label: "Procuradoria Regional Eleitoral no Ceará" },
    { id: "/portal/preba", label: "Procuradoria Regional Eleitoral na Bahia" },
    { id: "/portal/regiao4", label: "Procuradoria Regional da República da 4ª Região" },
    { id: "/portal/premg", label: "Procuradoria Regional Eleitoral em Minas Gerais" },
    { id: "/portal/pe", label: "Procuradoria da República em Pernambuco" },
    { id: "/portal/presc", label: "Procuradoria Regional Eleitoral em Santa Catarina" },
    { id: "/portal/pream", label: "Procuradoria Regional Eleitoral no Amazonas" },
    { id: "/portal/am", label: "Procuradoria da República no Amazonas" },
    { id: "/portal/ro", label: "Procuradoria da República em Rondônia" },
    { id: "/portal/mg", label: "MPF-MG de 1º grau" },
    { id: "/portal/prema", label: "Procuradoria Regional Eleitoral no Maranhão" },
    { id: "/portal/regiao2", label: "Procuradoria Regional da República da 2ª Região" },
    { id: "/portal/prers", label: "Procuradoria Regional Eleitoral no Rio Grande do Sul" },
    { id: "/portal/prepe", label: "Procuradoria Regional Eleitoral em Pernambuco" },
    { id: "/portal/pb", label: "Procuradoria da República na Paraíba" },
    { id: "/portal/go", label: "Procuradoria da República em Goiás" },
    { id: "/portal/to", label: "Procuradoria da República no Tocantins" },
    { id: "/portal/df", label: "Procuradoria da República no Distrito Federal" },
    { id: "/portal/ma", label: "Procuradoria da República no Maranhão" },
    { id: "/portal/pr", label: "Procuradoria da República no Paraná" },
    { id: "/portal/prepi", label: "Procuradoria Regional Eleitoral no Piauí" },
  ];

  // Aliases opcionais (se algum card vier com valor curto no futuro)
  const ORIGIN_ALIASES = new Map([
    ["pgr", "/portal/pgr"],
    ["pge", "/portal/pge"],
    ["presp", "/portal/presp"],
  ]);

  function normalizeOriginId(raw) {
    const v = String(raw || "").trim();
    if (!v) return "";
    if (v.startsWith("/portal/")) return v;
    return ORIGIN_ALIASES.get(v) || v;
  }

  // ====== UFs (pra renderizar botão/lista por UF) ======
  // Se o Plone mandar data-uf="df", a filtragem por UF usa isso.
  // Se NÃO mandar, a gente deriva a UF de data-origin="/portal/xx" quando fizer sentido.
  const UF_ITEMS = [
    { id: "ac", label: "Acre (AC)" },
    { id: "al", label: "Alagoas (AL)" },
    { id: "ap", label: "Amapá (AP)" },
    { id: "am", label: "Amazonas (AM)" },
    { id: "ba", label: "Bahia (BA)" },
    { id: "ce", label: "Ceará (CE)" },
    { id: "df", label: "Distrito Federal (DF)" },
    { id: "es", label: "Espírito Santo (ES)" },
    { id: "go", label: "Goiás (GO)" },
    { id: "ma", label: "Maranhão (MA)" },
    { id: "mt", label: "Mato Grosso (MT)" },
    { id: "ms", label: "Mato Grosso do Sul (MS)" },
    { id: "mg", label: "Minas Gerais (MG)" },
    { id: "pa", label: "Pará (PA)" },
    { id: "pb", label: "Paraíba (PB)" },
    { id: "pr", label: "Paraná (PR)" },
    { id: "pe", label: "Pernambuco (PE)" },
    { id: "pi", label: "Piauí (PI)" },
    { id: "rj", label: "Rio de Janeiro (RJ)" },
    { id: "rn", label: "Rio Grande do Norte (RN)" },
    { id: "rs", label: "Rio Grande do Sul (RS)" },
    { id: "ro", label: "Rondônia (RO)" },
    { id: "rr", label: "Roraima (RR)" },
    { id: "sc", label: "Santa Catarina (SC)" },
    { id: "sp", label: "São Paulo (SP)" },
    { id: "se", label: "Sergipe (SE)" },
    { id: "to", label: "Tocantins (TO)" },
  ];
  const UF_LABEL = new Map(UF_ITEMS.map((x) => [x.id, x.label]));
  const ORGAO_LABEL = new Map(ORGAOS_MPF_ATUAL.map((x) => [x.id, x.label]));

  // ====== ELEMENTS ======
  const results = $("#news-results");
  if (!results) return;

  const items = () => $$(".news-item", results);

  const countEl = $("#news-count");
  const statusEl = $("#filter-status");

  const searchInput = $("#news-search");
  const catSelect = $("#news-category");
  const sortSelect = $("#news-sort");

  // View (Cards/Lista)
  const viewBtns = $$(".news-view-btn");
  function setView(view) {
    // só faz sentido no desktop
    if (!window.matchMedia("(min-width: 1024px)").matches) {
      results.classList.remove("is-cards");
      results.classList.add("is-list");
      return;
    }

    results.classList.toggle("is-list", view === "list");
    results.classList.toggle("is-cards", view === "cards");

    viewBtns.forEach((b) => {
      const active = b.dataset.view === view;
      b.setAttribute("aria-pressed", active ? "true" : "false");
      b.classList.toggle("bg-gray-900", active);
      b.classList.toggle("text-white", active);
      b.classList.toggle("bg-white", !active);
      b.classList.toggle("text-gray-900", !active);
    });

    try {
      localStorage.setItem("mpf_news_view", view);
    } catch (e) {}
  }

  // Aside (UF/Órgão)
  const asideSearch = $("#asideSearch");
  const asideList = $("#asideList");
  const clearAside = $("#clearFiltersAside");
  const clearDesktop = $("#clearFiltersDesktop");
  const groupBtns = $$(".groupby-btn");

  // Mobile filtros
  const groupByMobile = $("#groupByMobile");
  const itemMobile = $("#itemMobile");
  const clearMobile = $("#clearFiltersMobile");

  // ====== STATE ======
  const state = {
    groupBy: "uf", // "uf" | "orgao"
    selected: "", // ufId OU orgaoId
    q: "",
    category: "",
    sort: "recentes",
    view: "cards",
  };

  // ====== HELPERS ======
  function normalizeText(s) {
    return String(s || "")
      .toLowerCase()
      .normalize("NFD")
      .replace(/\p{Diacritic}/gu, "");
  }

  function buildGroupItems(groupBy) {
    if (groupBy === "uf") return UF_ITEMS;
    return ORGAOS_MPF_ATUAL;
  }

  function getSelectedLabel() {
    if (!state.selected) return "";
    if (state.groupBy === "uf") return UF_LABEL.get(state.selected) || state.selected;
    return ORGAO_LABEL.get(state.selected) || state.selected;
  }

  function inferUfFromOrigin(originId) {
    // tenta derivar uf quando o origin é "/portal/xx"
    // não cobre todos (ex: /portal/preac, /portal/regiao1 etc.), por isso é só fallback.
    const v = String(originId || "");
    const m = v.match(/^\/portal\/([a-z]{2})$/i);
    return m ? m[1].toLowerCase() : "";
  }

  // ====== RENDER LISTS ======
  function renderAsideList() {
    if (!asideList) return;
    const q = (asideSearch?.value || "").trim().toLowerCase();
    const list = buildGroupItems(state.groupBy).filter((x) => !q || x.label.toLowerCase().includes(q));

    asideList.innerHTML = list
      .map((x) => {
        const active = x.id === state.selected;
        return `
          <li>
            <button type="button"
              class="w-full text-left rounded-md px-3 py-2 text-sm font-semibold
                     border ${active ? "border-gray-900 bg-gray-900 text-white" : "border-gray-200 bg-white text-gray-900"}
                     hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-[color:var(--brand)]/30"
              data-select="${x.id}">
              ${x.label}
            </button>
          </li>
        `;
      })
      .join("");

    $$("#asideList [data-select]").forEach((btn) => {
      btn.addEventListener("click", () => {
        state.selected = btn.dataset.select || "";
        applyAll();
        renderAsideList();
        syncMobile();
      });
    });
  }

  function renderMobileOptions() {
    if (!itemMobile) return;
    const list = buildGroupItems(state.groupBy);
    itemMobile.innerHTML = [
      `<option value="">Todas</option>`,
      ...list.map((x) => `<option value="${x.id}">${x.label}</option>`),
    ].join("");
  }

  function syncMobile() {
    if (groupByMobile) groupByMobile.value = state.groupBy;
    if (itemMobile) itemMobile.value = state.selected || "";
  }

  // ====== FILTER LOGIC ======
  function matchOrigin(el) {
    if (!state.selected) return true;

    const origin = normalizeOriginId(el.dataset.origin || "");
    const ufFromDataset = String(el.dataset.uf || "").toLowerCase().trim();
    const ufFromOrigin = inferUfFromOrigin(origin);

    if (state.groupBy === "orgao") {
      return origin === state.selected;
    }

    // groupBy === "uf"
    const uf = ufFromDataset || ufFromOrigin;
    if (!uf) return true; // se não veio info, não bloqueia
    return uf === state.selected;
  }

  function matchCategory(el) {
    if (!state.category) return true;
    return (el.dataset.category || "") === state.category;
  }

  function matchSearch(el) {
    const q = normalizeText(state.q);
    if (!q) return true;

    // tenta achar texto no elemento (título + primeiro parágrafo como resumo)
    const title =
      el.querySelector("h1,h2,h3,h4,a")?.textContent ||
      "";
    const summary =
      el.querySelector("p")?.textContent ||
      "";

    const hay = normalizeText(`${title} ${summary}`);
    return hay.includes(q);
  }

  function applyFilters() {
    items().forEach((el) => {
      const ok = matchOrigin(el) && matchCategory(el) && matchSearch(el);
      el.hidden = !ok;
    });
  }

  function applySorting() {
    const list = items();
    const visible = list.filter((el) => !el.hidden);

    visible.sort((a, b) => {
      const da = new Date(a.dataset.date || "1970-01-01").getTime();
      const db = new Date(b.dataset.date || "1970-01-01").getTime();
      return state.sort === "antigas" ? da - db : db - da;
    });

    visible.forEach((el) => results.appendChild(el));
  }

  function updateCount() {
    if (!countEl) return;
    const visible = items().filter((el) => !el.hidden).length;
    countEl.textContent = String(visible);
  }

  function updateStatus() {
    if (!statusEl) return;

    const parts = [];
    if (state.selected) parts.push(`${state.groupBy.toUpperCase()}: ${getSelectedLabel()}`);
    if (state.category) parts.push(`Categoria: ${state.category}`);
    if (state.q) parts.push(`Busca: “${state.q}”`);

    statusEl.textContent = parts.length ? `Filtrado por ${parts.join(" • ")}.` : "Exibindo todas as notícias.";
  }

  function applyAll() {
    applyFilters();
    applySorting();
    updateCount();
    updateStatus();
  }

  // ====== GROUP BY ======
  function setGroupBy(next) {
    const gb = next === "orgao" ? "orgao" : "uf";
    state.groupBy = gb;
    state.selected = ""; // troca de modo zera seleção
    if (asideSearch) asideSearch.value = "";

    groupBtns.forEach((b) => {
      const active = b.dataset.groupby === gb;
      b.setAttribute("aria-pressed", active ? "true" : "false");
      b.classList.toggle("bg-gray-900", active);
      b.classList.toggle("text-white", active);
      b.classList.toggle("bg-white", !active);
      b.classList.toggle("text-gray-900", !active);
    });

    renderMobileOptions();
    renderAsideList();
    syncMobile();
    applyAll();
  }

  function clearAll() {
    state.selected = "";
    state.q = "";
    state.category = "";
    state.sort = sortSelect?.value || "recentes";

    if (searchInput) searchInput.value = "";
    if (catSelect) catSelect.value = "";
    if (asideSearch) asideSearch.value = "";
    if (itemMobile) itemMobile.value = "";

    applyAll();
    renderAsideList();
    syncMobile();
  }

  // ====== EVENTS ======
  groupBtns.forEach((btn) =>
    btn.addEventListener("click", () => setGroupBy(btn.dataset.groupby))
  );

  if (asideSearch) asideSearch.addEventListener("input", renderAsideList);

  if (groupByMobile) groupByMobile.addEventListener("change", (e) => setGroupBy(e.target.value));

  if (itemMobile) {
    itemMobile.addEventListener("change", (e) => {
      state.selected = e.target.value || "";
      applyAll();
      renderAsideList();
    });
  }

  if (clearAside) clearAside.addEventListener("click", clearAll);
  if (clearMobile) clearMobile.addEventListener("click", clearAll);
  if (clearDesktop) clearDesktop.addEventListener("click", clearAll);

  // Busca / categoria / ordenação
  if (searchInput) {
    searchInput.addEventListener("input", () => {
      state.q = searchInput.value.trim();
      applyAll();
    });
  }

  if (catSelect) {
    catSelect.addEventListener("change", () => {
      state.category = catSelect.value || "";
      applyAll();
    });
  }

  if (sortSelect) {
    sortSelect.addEventListener("change", () => {
      state.sort = sortSelect.value || "recentes";
      applyAll();
    });
  }

  // View toggle
  viewBtns.forEach((b) => {
    b.addEventListener("click", () => {
      const v = b.dataset.view || "cards";
      state.view = v;
      setView(v);
    });
  });

  // ====== INIT ======
  // count inicial (quantos existem, antes de filtrar)
  if (countEl) countEl.textContent = String(items().length);

  // view inicial (salva)
  let saved = "cards";
  try {
    saved = localStorage.getItem("mpf_news_view") || "cards";
  } catch (e) {}
  state.view = saved;

  setView(state.view);

  // se redimensionar: força lista no mobile
  window.addEventListener("resize", () => setView(state.view));

  // listas/inputs
  renderMobileOptions();
  renderAsideList();
  syncMobile();

  // default group
  setGroupBy(state.groupBy);

  // aplica filtros iniciais
  applyAll();
})();
