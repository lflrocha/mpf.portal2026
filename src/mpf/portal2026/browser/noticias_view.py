# -*- coding: utf-8 -*-
import re
import logging
from DateTime import DateTime

from Products.Five.browser import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_unicode
from plone import api

from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

from plone.dexterity.utils import iterSchemata
from zope.schema import getFieldsInOrder
from zope.schema.vocabulary import getVocabularyRegistry

try:
    from urllib.parse import urlencode
except ImportError:
    from urllib import urlencode


UNIDADES_ORIGEM_MAP = {
    "pgr":  u"Procuradoria-Geral da República",
    "prr1": u"Procuradoria Regional da República da 1ª Região",
    "prr2": u"Procuradoria Regional da República da 2ª Região",
    "prr3": u"Procuradoria Regional da República da 3ª Região",
    "prr4": u"Procuradoria Regional da República da 4ª Região",
    "prr5": u"Procuradoria Regional da República da 5ª Região",
    "prr6": u"Procuradoria Regional da República da 6ª Região",
    "prac": u"Procuradoria da República no Acre",
    "pral": u"Procuradoria da República em Alagoas",
    "prap": u"Procuradoria da República no Amapá",
    "pram": u"Procuradoria da República no Amazonas",
    "prba": u"Procuradoria da República na Bahia",
    "prce": u"Procuradoria da República no Ceará",
    "prdf": u"Procuradoria da República no Distrito Federal",
    "pres": u"Procuradoria da República no Espírito Santo",
    "prgo": u"Procuradoria da República em Goiás",
    "prma": u"Procuradoria da República no Maranhão",
    "prmt": u"Procuradoria da República em Mato Grosso",
    "prms": u"Procuradoria da República em Mato Grosso do Sul",
    "prmg": u"Procuradoria da República em Minas Gerais",
    "prpa": u"Procuradoria da República no Pará",
    "prpb": u"Procuradoria da República na Paraíba",
    "prpr": u"Procuradoria da República no Paraná",
    "prpe": u"Procuradoria da República em Pernambuco",
    "prpi": u"Procuradoria da República no Piauí",
    "prrj": u"Procuradoria da República no Rio de Janeiro",
    "prrn": u"Procuradoria da República no Rio Grande do Norte",
    "prrs": u"Procuradoria da República no Rio Grande do Sul",
    "prro": u"Procuradoria da República em Rondônia",
    "prrr": u"Procuradoria da República em Roraima",
    "prsc": u"Procuradoria da República em Santa Catarina",
    "prsp": u"Procuradoria da República em São Paulo",
    "prse": u"Procuradoria da República em Sergipe",
    "prto": u"Procuradoria da República no Tocantins",
    "pfdc": u"Procuradoria Federal dos Direitos do Cidadão",
}

class NoticiasView(BrowserView):
    """Listagem de notícias com filtro por tema (único), unidade, busca e ordenação."""

    DEFAULT_PAGE_SIZE = 10

    # vocabulários (utility)
    temas_vocabulary_name = "mpf.portal2026.noticiatemas"

    # campo dexterity que será resolvido via vocabulário do próprio field
    unidade_origem_fieldname = "unidadeOrigem"

    # -------------------------
    # Lifecycle
    # -------------------------
    def __call__(self):
        self.request.set("disable_plone.leftcolumn", 1)
        self.request.set("disable_plone.rightcolumn", 1)
        return self.index()

    # -------------------------
    # Normalização / helpers
    # -------------------------
    def _normalize_single_value(self, value):
        """Pega 1 valor válido (string) e remove placeholders."""
        blacklist = ("", None, "__novalue__", "--- Selecione ---", "-- Selecione --")

        if isinstance(value, (list, tuple)):
            value = [v for v in value if v not in blacklist]
            return safe_unicode(value[0]).strip() if value else ""

        if isinstance(value, str):
            v = value.strip()
            return safe_unicode(v) if v not in blacklist else ""

        return ""

    def _catalog(self):
        return getToolByName(self.context, "portal_catalog")

    def _site_path(self):
        portal = api.portal.get()
        return "/".join(portal.getPhysicalPath())

    # -------------------------
    # Request params
    # -------------------------
    def q(self):
        return (self.request.get("q") or "").strip()

    def tema(self):
        return self._normalize_single_value(self.request.get("tema"))

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
    # Vocabulários e opções (UI)
    # -------------------------
    def _get_vocab_utility(self, name):
        """Resolve vocabulário registrado como IVocabularyFactory utility."""
        try:
            factory = getUtility(IVocabularyFactory, name=name)
            return factory(self.context)
        except Exception:
            return None

    def temas_options(self):
        opts = [("", u"Todas")]
        vocab = self._get_vocab_utility(self.temas_vocabulary_name)
        if vocab:
            for term in vocab:
                value = getattr(term, "value", "") or ""
                title = getattr(term, "title", None) or getattr(term, "label", None) or value
                opts.append((safe_unicode(value), safe_unicode(title)))
        return opts

    def _tema_title(self, tema_id):
        if not tema_id:
            return u""
        vocab = self._get_vocab_utility(self.temas_vocabulary_name)
        if not vocab:
            return safe_unicode(tema_id)

        # usa mapa por iteração (mais robusto que getTerm em alguns cenários)
        for term in vocab:
            if safe_unicode(getattr(term, "value", "")) == safe_unicode(tema_id):
                return safe_unicode(getattr(term, "title", None) or getattr(term, "label", None) or tema_id)

        return safe_unicode(tema_id)

    def unidades_options(self):
        # simples por enquanto
        return [
            ("", u"Todas"),
            ("/portal/pgr", u"PGR"),
            ("/portal/prr", u"PRR"),
            ("/portal/prm", u"PRM"),
        ]

    # -------------------------
    # Resolver label via vocabulário do field (Dexterity)
    # -------------------------
    def _field(self, name):
        for schema in iterSchemata(self.context):
            for fname, field in getFieldsInOrder(schema):
                if fname == name:
                    return field
        return None

    def _get_vocab_from_field(self, fieldname):
        field = self._field(fieldname)
        if field is None:
            return None

        choice = getattr(field, "value_type", None) or field

        vocab = getattr(choice, "vocabulary", None)
        if vocab is not None:
            return vocab

        vocab_name = getattr(choice, "vocabularyName", None)
        if vocab_name:
            try:
                registry = getVocabularyRegistry()
                return registry.get(self.context, vocab_name)
            except Exception:
                return None

        return None

    def _label_from_field_vocab(self, fieldname, token_or_value):
        """Resolve value/token -> title iterando o vocabulário do field (robusto)."""
        token_or_value = self._normalize_single_value(token_or_value)
        if not token_or_value:
            return u""

        vocab = self._get_vocab_from_field(fieldname)
        if not vocab:
            return safe_unicode(token_or_value)

        key = safe_unicode(token_or_value)

        # cria mapa simples por iteração (value e token)
        for term in vocab:
            v = safe_unicode(getattr(term, "value", "") or "")
            t = safe_unicode(getattr(term, "token", "") or "")
            title = safe_unicode(getattr(term, "title", None) or getattr(term, "label", None) or v or t)

            if key == v or key == t:
                return title

        return safe_unicode(token_or_value)

    # -------------------------
    # Query catálogo
    # -------------------------
    def _resolve_unidade_path(self):
        """Converte '/portal/pgr' => '<site>/portal/pgr'"""
        u = self.unidade()
        if not u:
            return ""
        u = u[1:] if u.startswith("/") else u
        base = self._site_path()
        return base + "/" + u if u else ""

    def _tema_index_name(self):
        """Detecta nome do índice tema/temas no catálogo."""
        catalog = self._catalog()
        indexes = getattr(catalog, "indexes", lambda: {})()
        if "tema" in indexes:
            return "tema"
        if "temas" in indexes:
            return "temas"
        return "tema"

    def _query(self):
        catalog = self._catalog()
        sort_order = "reverse" if self.sort() == "recentes" else "ascending"

        query = {
            "portal_type": "Noticia",
            "sort_on": "effective",
            "sort_order": sort_order,
            "path": {"query": self._site_path(), "depth": -1},
        }

        unidade_path = self._resolve_unidade_path()
        if unidade_path:
            query["path"] = {"query": unidade_path, "depth": -1}

        tema = self.tema()
        if tema:
            query[self._tema_index_name()] = tema

        if self.q():
            query["SearchableText"] = self._searchabletext_query(self.q())

        return catalog(**query)

    # -------------------------
    # Render helpers (itens)
    # -------------------------
    def _image_url(self, obj):
        for fieldname in ("image", "imagem", "capa", "leadImage", "lead_image"):
            img = getattr(obj, fieldname, None)
            if img:
                return obj.absolute_url() + "/@@images/{}/preview".format(fieldname)
        return ""

    def _origin(self, brain):
        try:
            site = self._site_path()
            p = brain.getPath()
            if p.startswith(site):
                rel = p[len(site):]
                return rel or "/"
            return p
        except Exception:
            return ""

    def _human_date(self, dt):
        if not dt:
            return ""
        try:
            return dt.strftime("%d/%m/%Y • %H:%M")
        except Exception:
            try:
                d = DateTime(dt)
                return d.strftime("%d/%m/%Y • %H:%M")
            except Exception:
                return ""

    def _unidade_origem_label(self, unidade_id):
        unidade_id = (unidade_id or "").strip()
        if not unidade_id or unidade_id == "__novalue__":
            return u""
        unidade_id = safe_unicode(unidade_id)
        return UNIDADES_ORIGEM_MAP.get(unidade_id, unidade_id)



    # -------------------------
    # Public: results + pagination
    # -------------------------
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
            try:
                obj = b.getObject()
            except Exception:
                obj = None

            tema_id = self._normalize_single_value(getattr(b, "tema", None) or getattr(b, "temas", None))
            if obj and not tema_id:
                tema_id = self._normalize_single_value(getattr(obj, "tema", None) or getattr(obj, "temas", None))

            unidade_id = self._normalize_single_value(getattr(b, "unidadeOrigem", None))
            if obj and not unidade_id:
                unidade_id = self._normalize_single_value(getattr(obj, "unidadeOrigem", None))

            unidade_label = self._unidade_origem_label(unidade_id)
            
            dt = getattr(b, "effective", None) or getattr(b, "created", None) or None

            items.append({
                "title": safe_unicode(getattr(b, "Title", "") or ""),
                "description": safe_unicode(getattr(b, "Description", "") or ""),
                "url": b.getURL(),
                "origin": safe_unicode(self._origin(b)),
                "tema_id": tema_id,
                "tema": self._tema_title(tema_id) if tema_id else u"Geral",
                "unidadeOrigem": unidade_label,
                "image_url": self._image_url(obj) if obj else "",
                "datetime_iso": dt.ISO() if dt else "",
                "datetime_human": self._human_date(dt),
            })

        return {"items": items, "total": total, "page": p, "pages": pages}

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

    # -------------------------
    # SearchableText helper
    # -------------------------
    def _searchabletext_query(self, q):
        q = (q or "").strip()
        if not q:
            return ""

        if "*" in q or ":" in q or '"' in q:
            return q

        parts = re.split(r"\s+", q)
        out = []
        for p in parts:
            p = p.strip()
            if not p:
                continue

            if re.match(r"^[\w\-]+$", p, flags=re.UNICODE):
                out.append(p + "*")
            else:
                out.append(p)

        return " ".join(out)
