# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from plone import api
from Products.CMFPlone.utils import safe_unicode
from DateTime import DateTime
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory
import re
try:
    # Py3
    from urllib.parse import urlencode
except ImportError:
    # Py2 fallback (não deve ocorrer no teu ambiente)
    from urllib import urlencode


class NoticiasView(BrowserView):
    """Listagem de notícias com filtro por tema (único), unidade, busca e ordenação."""

    DEFAULT_PAGE_SIZE = 10
    temas_vocabulary_name = "mpf.portal2026.noticiatemas"

    # -------------------------
    # Params do request
    # -------------------------
    def q(self):
        return (self.request.get("q") or "").strip()

    def tema(self):
        return (self.request.get("tema") or "").strip()

    def unidade(self):
        # esperado: "/portal/pgr" (relativo ao site)
        return (self.request.get("unidade") or "").strip()

    def sort(self):
        v = (self.request.get("sort") or "recentes").strip().lower()
        return v if v in ("recentes", "antigas") else "recentes"

    def page(self):
        try:
            p = int(self.request.get("page") or 1)
        except Exception:
            p = 1
        return max(1, p)

    def page_size(self):
        try:
            s = int(self.request.get("pagesize") or self.DEFAULT_PAGE_SIZE)
        except Exception:
            s = self.DEFAULT_PAGE_SIZE
        return min(max(1, s), 50)

    # -------------------------
    # Vocabulário / opções
    # -------------------------

    def _get_vocab(self, name):
        try:
            factory = getUtility(IVocabularyFactory, name=name)
            return factory(self.context)
        except Exception:
            return None

    def temas_options(self):
        opts = [("", u"Todas")]
        vocab = self._get_vocab(self.temas_vocabulary_name)
        if vocab:
            for term in vocab:
                value = getattr(term, "value", "")
                title = getattr(term, "title", None) or getattr(term, "label", None) or value
                opts.append((safe_unicode(value), safe_unicode(title)))
        return opts

    def _tema_title(self, tema_id):
        if not tema_id:
            return u""
        vocab = self._get_vocab(self.temas_vocabulary_name)
        if not vocab:
            return safe_unicode(tema_id)
        try:
            term = vocab.getTerm(tema_id)
            return safe_unicode(getattr(term, "title", None) or getattr(term, "label", None) or tema_id)
        except Exception:
            return safe_unicode(tema_id)


    def unidades_options(self):
        """
        Opções do aside. Por enquanto simples.
        Se depois você tiver uma fonte real (estrutura do site, registry, etc),
        troca aqui mantendo o formato (value,label).
        """
        return [
            ("", u"Todas"),
            ("/portal/pgr", u"PGR"),
            ("/portal/prr", u"PRR"),
            ("/portal/prm", u"PRM"),
        ]

    # -------------------------
    # Query catálogo
    # -------------------------
    def _catalog(self):
        return getToolByName(self.context, "portal_catalog")

    def _site_path(self):
        portal = api.portal.get()
        return "/".join(portal.getPhysicalPath())

    def _resolve_unidade_path(self):
        """
        Converte "/portal/pgr" => "/mpf2026/portal/pgr"
        """
        u = self.unidade()
        if not u:
            return ""
        u = u.strip()
        # aceita com ou sem "/"
        u = u[1:] if u.startswith("/") else u
        base = self._site_path()
        return base + "/" + u if u else ""

    def _tema_index_name(self):
        """
        Você disse que o campo é `tema` e é único.
        Mas às vezes o índice pode estar como `temas`.
        Aqui detectamos automaticamente.
        """
        catalog = self._catalog()
        indexes = getattr(catalog, "indexes", lambda: {})()
        if "tema" in indexes:
            return "tema"
        if "temas" in indexes:
            return "temas"
        # fallback: tenta "tema" primeiro
        return "tema"

    def _query(self):
        catalog = self._catalog()

        sort_order = "reverse" if self.sort() == "recentes" else "ascending"

        query = {
            "portal_type": "Noticia",
            "sort_on": "effective",
            "sort_order": sort_order,
        }

        # escopo base: site todo
        path_query = {"query": self._site_path(), "depth": -1}

        # unidade (se vier)
        unidade_path = self._resolve_unidade_path()
        if unidade_path:
            path_query = {"query": unidade_path, "depth": -1}

        query["path"] = path_query

        # tema (único)
        tema = self.tema()
        if tema:
            idx = self._tema_index_name()
            query[idx] = tema

        # busca textual

        if self.q():
            query["SearchableText"] = self._searchabletext_query(self.q())

        return catalog(**query)

    # -------------------------
    # Montagem dos itens pro template
    # -------------------------
    def _image_url(self, obj):
        """
        Tenta extrair uma URL de imagem.
        Ajuste o nome do campo conforme seu schema:
        - image
        - imagem
        - capa
        etc.
        """
        for fieldname in ("image", "imagem", "capa", "leadImage", "lead_image"):
            img = getattr(obj, fieldname, None)
            if img:
                # @@images/<field>/<scale>
                return obj.absolute_url() + "/@@images/{}/preview".format(fieldname)
        return ""

    def _origin(self, brain):
        # caminho relativo dentro do site (ex: /portal/pgr/...)
        try:
            site = self._site_path()
            p = brain.getPath()
            if p.startswith(site):
                rel = p[len(site):]
                return rel or "/"
            return brain.getPath()
        except Exception:
            return ""

    def _human_date(self, dt):
        if not dt:
            return ""
        try:
            # DateTime -> string BR
            # dt é DateTime (Zope) normalmente
            return dt.strftime("%d/%m/%Y • %H:%M")
        except Exception:
            try:
                d = DateTime(dt)
                return d.strftime("%d/%m/%Y • %H:%M")
            except Exception:
                return ""

    def results(self):
        brains = self._query()

        p = self.page()
        s = self.page_size()
        start = (p - 1) * s
        end = start + s

        total = len(brains)
        pages = (total + s - 1) // s if total else 1

        items = []
        for b in brains[start:end]:
            obj = None
            try:
                obj = b.getObject()
            except Exception:
                obj = None

            # tema id: tenta brain primeiro; se não tiver, tenta no objeto
            tema_id = ""
            try:
                tema_id = getattr(b, "tema", "") or getattr(b, "temas", "") or ""
            except Exception:
                tema_id = ""

            if obj and not tema_id:
                tema_id = getattr(obj, "tema", "") or getattr(obj, "temas", "") or ""

            tema_id = safe_unicode(tema_id) if tema_id else ""

            dt = getattr(b, "effective", None) or getattr(b, "created", None) or None

            items.append({
                "title": safe_unicode(getattr(b, "Title", "") or ""),
                "description": safe_unicode(getattr(b, "Description", "") or ""),
                "url": b.getURL(),
                "origin": safe_unicode(self._origin(b)),
                "tema_id": tema_id,
                "tema": self._tema_title(tema_id) if tema_id else u"Geral",
                "image_url": self._image_url(obj) if obj else "",
                "datetime_iso": dt.ISO() if dt else "",
                "datetime_human": self._human_date(dt),
            })

        return {
            "items": items,
            "total": total,
            "page": p,
            "pages": pages,
        }

    # -------------------------
    # URL builder para paginação
    # -------------------------
    def build_url(self, page=1):
        params = {}
        if self.q():
            params["q"] = self.q()
        if self.tema():
            params["tema"] = self.tema()
        if self.unidade():
            params["unidade"] = self.unidade()
        if self.sort():
            params["sort"] = self.sort()
        if self.request.get("pagesize"):
            params["pagesize"] = str(self.page_size())

        params["page"] = str(page)

        base = self.context.absolute_url() + "/@@noticias-view"
        return base + "?" + urlencode(params)




    def _searchabletext_query(self, q):
        """
        Converte a busca do usuário em uma query mais permissiva.
        Ex:
          "teste"  -> "teste*"
          "teste 2" -> "teste* 2*"
        Mantém aspas quando o usuário já escreveu busca com frase.
        """
        q = (q or "").strip()
        if not q:
            return ""

        # Se o usuário já colocou wildcard ou fez busca avançada, respeita
        if "*" in q or ":" in q or '"' in q:
            return q

        parts = re.split(r"\s+", q)
        out = []
        for p in parts:
            p = p.strip()
            if not p:
                continue

            # só adiciona * em termos "normais"
            if re.match(r"^[\w\-]+$", p, flags=re.UNICODE):
                out.append(p + "*")
            else:
                out.append(p)

        return " ".join(out)
