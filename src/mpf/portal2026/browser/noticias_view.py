# -*- coding: utf-8 -*-
from plone import api
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView


DEFAULT_PAGE_SIZE = 20

# Ajuste aqui para os tipos reais do seu portal:
NEWS_PORTAL_TYPES = (
    "Noticia",      # seu Dexterity clone
    "News Item",    # tipo padrão (se existir)
)

class NoticiasView(BrowserView):
    """Lista notícias em escopo local (default) ou global (?scope=global)."""

    def _catalog(self):
        return getToolByName(self.context, "portal_catalog")

    def _portal(self):
        return api.portal.get()

    def scope(self):
        req = self.request
        scope = (req.get("scope") or "local").strip().lower()
        return "global" if scope == "global" else "local"

    def base_path(self):
        # global: raiz do site
        if self.scope() == "global":
            portal = self._portal()
            return "/".join(portal.getPhysicalPath())

        # local: a partir do contexto atual (pasta/unidade) e descendo
        return "/".join(self.context.getPhysicalPath())

    def page(self):
        try:
            p = int(self.request.get("page", 1))
        except Exception:
            p = 1
        return max(1, p)

    def page_size(self):
        try:
            s = int(self.request.get("page_size", DEFAULT_PAGE_SIZE))
        except Exception:
            s = DEFAULT_PAGE_SIZE
        # evita abusos
        return min(max(5, s), 100)

    def results(self):
        catalog = self._catalog()

        path = {"query": self.base_path(), "depth": -1}

        # Ordena por effective desc; se seu portal usa "created" ou "modified", troque aqui.
        query = {
            "portal_type": NEWS_PORTAL_TYPES,
            "path": path,
            "sort_on": "effective",
            "sort_order": "descending",
        }

        # paginação via b_start
        page = self.page()
        page_size = self.page_size()
        b_start = (page - 1) * page_size

        # no Plone 5, dá pra usar b_start/b_size no catalog
        brains = catalog(query, b_start=b_start, b_size=page_size)

        # total vem do “sequence length”
        total = getattr(brains, "sequence_length", None)
        if callable(total):
            total = total()
        else:
            # fallback
            total = len(catalog(query))

        return {
            "brains": brains,
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": int((total + page_size - 1) / page_size) if total is not None else 1,
        }

    def url_for_page(self, page):
        base = self.context.absolute_url() + "/noticias_view"
        scope = self.scope()
        page_size = self.page_size()
        return f"{base}?scope={scope}&page_size={page_size}&page={page}"
