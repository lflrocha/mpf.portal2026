# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from DateTime import DateTime

from zope.schema.vocabulary import getVocabularyRegistry
from zope.component import getUtility
from zope.schema.interfaces import IVocabularyFactory

try:
    from plone.batching import Batch
except ImportError:
    Batch = None


class NoticiasView(BrowserView):
    """Página de busca de notícias (keyword + tema + unidade/origem)."""

    DEFAULT_PAGE_SIZE = 10

    def _catalog(self):
        return getToolByName(self.context, "portal_catalog")

    def _portal(self):
        return getToolByName(self.context, "portal_url").getPortalObject()

    # -----------------------
    # Leitura de parâmetros
    # -----------------------
    def q(self):
        return (self.request.get("q") or "").strip()

    def tema(self):
        return (self.request.get("tema") or "").strip()

    def unidade(self):
        # unidade = caminho, ex: "/portal/pgr" (igual seu data-origin)
        u = (self.request.get("unidade") or "").strip()
        if not u:
            return ""
        # normaliza: sempre começar com "/" e sem "/" no fim
        if not u.startswith("/"):
            u = "/" + u
        u = u.rstrip("/")
        return u

    def sort(self):
        s = (self.request.get("sort") or "recentes").strip()
        return s if s in ("recentes", "antigas") else "recentes"

    def page(self):
        try:
            p = int(self.request.get("page") or 1)
        except Exception:
            p = 1
        return max(1, p)

    def page_size(self):
        try:
            ps = int(self.request.get("ps") or self.DEFAULT_PAGE_SIZE)
        except Exception:
            ps = self.DEFAULT_PAGE_SIZE
        return max(1, min(ps, 50))

    # -----------------------
    # Vocabulários/Opções
    # -----------------------
    def temas_options(self):
        """Opções para o select de temas"""
        registry = getVocabularyRegistry()
        vocab = registry.get(self.context, "mpf.portal2026.noticiatemas")

        options = [("", "Todas")]
        for term in vocab:
            options.append((term.token, term.title))

        return options

    def unidades_options(self, max_items=200):
        """
        Fallback simples para montar uma lista de origens a partir das notícias existentes.
        Se você tiver uma taxonomia oficial de unidades, troque isso por ela.
        """
        cat = self._catalog()
        brains = cat(portal_type="Noticia", sort_on="created", sort_order="reverse")[:5000]
        seen = set()
        opts = [("", u"Todas")]
        for b in brains:
            # origem = primeiro ou primeiros níveis do path
            # ex: /mpf2026/portal/pgr/noticia-x  -> queremos /portal/pgr
            path = b.getPath()
            parts = path.split("/")
            # ajuste se sua estrutura for diferente
            # aqui eu pego os 2 níveis após a raiz do site: /portal/UF
            if len(parts) >= 4:
                origin = "/" + "/".join(parts[2:4])  # exemplo: /portal/pgr
                if origin not in seen:
                    seen.add(origin)
                    opts.append((origin, origin))
            if len(opts) >= max_items:
                break
        return opts

    # -----------------------
    # Busca no catálogo
    # -----------------------
    def build_query(self):
        q = {
            "portal_type": "Noticia",
            "review_state": "published",
        }

        # palavra-chave (SearchableText)
        if self.q():
            q["SearchableText"] = self.q()

        # tema
        if self.tema():
            # se o seu campo chama 'temas' e indexa, isso funciona
            q["temas"] = self.tema()

        # unidade/origem por path
        if self.unidade():
            portal = self._portal()
            base = portal.getPhysicalPath()
            # transforma "/portal/pgr" em path físico do portal + "/portal/pgr"
            origin_path = "/".join(base) + self.unidade()
            q["path"] = {"query": origin_path, "depth": -1}

        # ordenação (ajuste o index de data conforme o seu)
        # normalmente: effective / Date / created
        if self.sort() == "antigas":
            q["sort_on"] = "effective"
            q["sort_order"] = "ascending"
        else:
            q["sort_on"] = "effective"
            q["sort_order"] = "descending"

        return q

    def results(self):
        cat = self._catalog()
        brains = cat(**self.build_query())

        # paginação
        page = self.page()
        ps = self.page_size()
        start = (page - 1) * ps
        end = start + ps

        sliced = brains[start:end]

        items = []
        for b in sliced:
            items.append(self.brain_to_item(b))

        total = len(brains)
        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": ps,
            "pages": int((total + ps - 1) / ps) if ps else 1,
        }

    def brain_to_item(self, b):
        obj = None
        try:
            obj = b.getObject()
        except Exception:
            obj = None

        title = getattr(b, "Title", "") or getattr(b, "title", "") or ""
        desc = getattr(b, "Description", "") or getattr(b, "description", "") or ""

        # data
        dt = getattr(b, "effective", None) or getattr(b, "created", None)
        iso = ""
        human = ""
        if dt:
            try:
                if isinstance(dt, DateTime):
                    iso = dt.ISO()
                    human = dt.strftime("%d/%m/%Y • %H:%M")
                else:
                    # fallback
                    iso = str(dt)
                    human = str(dt)
            except Exception:
                iso = str(dt)
                human = str(dt)

        # chapéu/tema (se você usa 'temas' como lista)
        tema_label = ""
        try:
            if obj is not None and hasattr(obj, "temas") and obj.temas:
                # se for lista de ids, tenta traduzir via vocabulário
                tema_id = obj.temas[0] if isinstance(obj.temas, (list, tuple)) else obj.temas
                tema_label = self.tema_title(tema_id)
        except Exception:
            pass

        # origem (path "curto" tipo /portal/pgr)
        origin = self.origin_from_path(b.getPath())

        # imagem (NamedBlobImage no seu tipo Noticia)
        image_url = ""
        if obj is not None:
            image_url = self.image_url(obj)

        return {
            "title": title,
            "description": desc,
            "url": b.getURL(),
            "tema": tema_label,
            "tema_id": (obj.temas[0] if obj is not None and getattr(obj, "temas", None) else ""),
            "origin": origin,
            "datetime_iso": iso,
            "datetime_human": human,
            "image_url": image_url,
        }

    def origin_from_path(self, path):
        # Ajuste conforme sua IA real.
        # Ex: /mpf2026/portal/pgr/xyz -> /portal/pgr
        parts = path.split("/")
        if len(parts) >= 4:
            return "/" + "/".join(parts[2:4])
        return ""

    def tema_title(self, tema_id):
        if not tema_id:
            return ""
        try:
            from zope.schema.vocabulary import getVocabularyRegistry
            reg = getVocabularyRegistry()
            vocab = reg.get(self.context, "mpf.portal2026.noticiatemas")
            term = vocab.getTerm(tema_id)
            return term.title
        except Exception:
            return tema_id

    def image_url(self, obj):
        """
        Tenta obter a URL da imagem principal da notícia.
        Ajuste o nome do campo conforme seu schema (ex: image / imagem).
        """
        field_name_candidates = ("image", "imagem", "imagePrincipal", "imagemPrincipal")
        for fname in field_name_candidates:
            if hasattr(obj, fname):
                try:
                    img = getattr(obj, fname)
                    if img:
                        # @@images é o padrão em Dexterity (plone.namedfile)
                        return obj.absolute_url() + "/@@images/{}/large".format(fname)
                except Exception:
                    pass
        return ""

    # helpers pro template
    def build_url(self, **overrides):
        """
        Monta URL mantendo parâmetros atuais e sobrescrevendo os que vierem.
        """
        base = self.context.absolute_url() + "/noticias"
        params = {
            "q": self.q(),
            "tema": self.tema(),
            "unidade": self.unidade(),
            "sort": self.sort(),
            "page": self.page(),
            "ps": self.page_size(),
        }
        params.update(overrides)
        # remove vazios pra URL ficar limpa
        clean = {k: v for k, v in params.items() if v not in ("", None)}
        from urllib import urlencode  # python2 compat? no py3 é urllib.parse
        try:
            qs = urlencode(clean)
        except Exception:
            from urllib.parse import urlencode as _urlencode
            qs = _urlencode(clean)
        return base + ("?" + qs if qs else "")
