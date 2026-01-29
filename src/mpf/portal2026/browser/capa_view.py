# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from plone.namedfile.interfaces import INamedBlobImageField
from plone.scale.scale import scaleImage
from zope.component import queryUtility
from zope.schema.interfaces import IField
from plone.scale.scale import scaleImage
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName


class CapaView(BrowserView):


    # -------------------------
    # Helpers
    # -------------------------
    def _relation_to_obj(self, rel):
        try:
            return rel.to_object if rel else None
        except Exception:
            return None

    def _first_text(self, value):
        """Converte lista/tupla/set ou string em texto simples."""
        if not value:
            return ""
        if isinstance(value, (list, tuple, set)):
            return str(next(iter(value), "")) or ""
        return str(value)

    def _get_chapeu_from_noticia(self, obj):
        """
        Tenta achar um 'chapéu' em campos comuns.
        Ajuste depois para o campo definitivo do seu tipo Noticia.
        """
        # 1) campo explícito
        for fname in ("chapeu", "chapéu", "hat", "kicker"):
            if hasattr(obj, fname):
                v = getattr(obj, fname, None)
                v = self._first_text(v)
                if v:
                    return v

        # 2) temas / theme / categoria
        for fname in ("temas", "tema", "themes", "categories"):
            if hasattr(obj, fname):
                v = getattr(obj, fname, None)
                v = self._first_text(v)
                if v:
                    return v

        # 3) Subject (assuntos)
        try:
            subj = obj.Subject()
            v = self._first_text(subj)
            if v:
                return v
        except Exception:
            pass

        return ""

    def _get_date_from_noticia(self, obj):
        """
        Tenta pegar a data mais adequada da notícia.
        Preferência: effective (publicação). Fallback: created.
        Retorna DateTime do Zope.
        """
        # effective()
        for attr in ("effective", "effective_date", "effectiveDate"):
            if hasattr(obj, attr):
                try:
                    v = getattr(obj, attr)
                    v = v() if callable(v) else v
                    if v:
                        return v
                except Exception:
                    pass

        # created()
        for attr in ("created", "creation_date", "creationDate"):
            if hasattr(obj, attr):
                try:
                    v = getattr(obj, attr)
                    v = v() if callable(v) else v
                    if v:
                        return v
                except Exception:
                    pass

        # EffectiveDate string do AT
        try:
            s = obj.EffectiveDate()  # string
            if s and s != "None":
                return DateTime(s)
        except Exception:
            pass

        return None

    def _format_date_ptbr(self, dt):
        """Formata: DD/MM/AAAA | HH:MM"""
        if not dt:
            return ""
        try:
            # dt pode ser DateTime do Zope
            return dt.strftime("%d/%m/%Y | %H:%M")
        except Exception:
            try:
                # DateTime do Zope tem strftime também, mas fica aqui como fallback
                return dt.ISO()[:16].replace("-", "/").replace("T", " | ")
            except Exception:
                return ""

    def _get_image_url_from_noticia(self, obj, scale="large"):
        """
        Tenta obter imagem via @@images (Plone 5.2) em campos comuns.
        Fallback: @@download/<campo>
        """
        # lista de candidatos comuns
        candidates = (
            "image", "imagem", "leadImage", "lead_image",
            "preview_image", "thumbnail", "foto", "capa", "banner"
        )

        base = obj.absolute_url()

        # tenta @@images/<field>/<scale>
        for fieldname in candidates:
            if hasattr(obj, fieldname):
                # não valida o conteúdo agora (custa caro); tenta URL direto
                return f"{base}/@@images/{fieldname}/{scale}"

        # fallback: @@download do campo mais provável
        for fieldname in candidates:
            if hasattr(obj, fieldname):
                return f"{base}/@@download/{fieldname}"

        return ""


    def _image_url_from_namedblob(self, fieldname, width=1200, height=800):
        """URL da imagem (NamedBlobImage) salva no próprio objeto Capa."""
        value = getattr(self.context, fieldname, None)
        if not value:
            return ""

        # tenta scale (melhor)
        try:
            result = scaleImage(value, width=width, height=height, direction="down")
            if result and getattr(result, "url", None):
                return result.url
        except Exception:
            pass

        # fallback: original
        return "{0}/@@download/{1}".format(self.context.absolute_url(), fieldname)

    # -------------------------
    # Bloco: Em destaque (relations)
    # -------------------------
    def destaques(self):
        out = []
        for fname in ("noticia_1", "noticia_2", "noticia_3"):
            obj = self._relation_to_obj(getattr(self.context, fname, None))
            if not obj:
                continue

            title = ""
            desc = ""
            try:
                title = obj.Title()
            except Exception:
                title = getattr(obj, "title", "") or ""

            try:
                desc = obj.Description()
            except Exception:
                desc = getattr(obj, "description", "") or ""

            dt = self._get_date_from_noticia(obj)

            out.append({
                "obj": obj,
                "title": title,
                "url": obj.absolute_url(),
                "description": desc,
                "chapeu": self._get_chapeu_from_noticia(obj),
                "date_str": self._format_date_ptbr(dt),
                "image_url": self._get_image_url_from_noticia(obj, scale="large"),
            })

        return out






    # -------------------------
    # Blocos
    # -------------------------


    def destaques_ultimas(self):
        """3 itens editáveis na Capa: du1..du3 (chapeu, titulo, imagem, link)"""
        items = []
        for i in (1, 2, 3):
            prefix = f"du{i}_"
            items.append({
                "chapeu": getattr(self.context, prefix + "chapeu", ""),
                "titulo": getattr(self.context, prefix + "titulo", ""),
                "link": getattr(self.context, prefix + "link", ""),
                "imagem_url": self._image_url_from_namedblob(prefix + "imagem", width=1200, height=800),
            })
        return items

    def em_foco(self):
        """3 itens editáveis na Capa: ef1..ef3 (chapeu, titulo, imagem, link)"""
        items = []
        for i in (1, 2, 3):
            prefix = f"ef{i}_"
            items.append({
                "chapeu": getattr(self.context, prefix + "chapeu", ""),
                "titulo": getattr(self.context, prefix + "titulo", ""),
                "link": getattr(self.context, prefix + "link", ""),
                "imagem_url": self._image_url_from_namedblob(prefix + "imagem", width=1200, height=800),
            })
        return items

    # -------------------------
    # Últimas notícias (catálogo)
    # -------------------------
    def ultimas_noticias(self, limit=3, tipos=None, path=None, review_state="published"):
        """
        Retorna as últimas notícias (limit), usando portal_catalog.

        - tipos: lista/tupla de portal_type (default tenta Noticia e variações comuns)
        - path: se None, busca no site todo. Se quiser restringir, passe um path físico
                tipo '/mpf2026/comunicacao/noticias'
        - review_state: 'published' por padrão (ajuste se necessário)
        """
        catalog = getToolByName(self.context, "portal_catalog")
        portal = getToolByName(self.context, "portal_url").getPortalObject()

        if tipos is None:
            # ajuste para o(s) tipo(s) real(is) do seu produto
            tipos = ("Noticia", "noticia", "News Item", "NewsItem")

        query = {
            "portal_type": tipos,
            "sort_on": "effective",
            "sort_order": "reverse",
        }

        if review_state:
            query["review_state"] = review_state

        if path:
            # aceita path físico começando com / (relativo ao portal)
            base = "/".join(portal.getPhysicalPath())
            if path.startswith("/"):
                path_query = base + path
            else:
                path_query = base + "/" + path
            query["path"] = {"query": path_query, "depth": -1}

        brains = catalog(**query)

        out = []
        for b in brains[:limit]:
            try:
                obj = b.getObject()
            except Exception:
                continue

            title = ""
            desc = ""
            try:
                title = obj.Title()
            except Exception:
                title = getattr(obj, "title", "") or ""

            try:
                desc = obj.Description()
            except Exception:
                desc = getattr(obj, "description", "") or ""

            dt = self._get_date_from_noticia(obj)

            out.append({
                "obj": obj,
                "title": title,
                "url": obj.absolute_url(),
                "description": desc,
                "chapeu": self._get_chapeu_from_noticia(obj),
                "date_str": self._format_date_ptbr(dt),
                "image_url": self._get_image_url_from_noticia(obj, scale="large"),
            })

        return out
