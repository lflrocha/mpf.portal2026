from Products.Five import BrowserView
from plone import api


class NoticiasView(BrowserView):
    """View da página de Notícias (JS-driven)"""

    def results(self):
        """Brains de notícias publicadas (ordenadas)"""
        catalog = api.portal.get_tool("portal_catalog")
        return catalog(
            portal_type="News Item",
            review_state="published",
            sort_on="effective",
            sort_order="reverse",
        )

    def categories(self):
        """Categorias (Subjects) únicas"""
        catalog = api.portal.get_tool("portal_catalog")
        subjects = catalog.uniqueValuesFor("Subject")
        return sorted(subjects)

    def image_url(self, brain):
        """Imagem principal em escala large (se existir)"""
        try:
            obj = brain.getObject()
        except Exception:
            return ""

        image = getattr(obj, "image", None)
        if not image:
            return ""

        scale = image.scale("large")
        return scale.url if scale else ""

    def unit(self, brain):
        """Unidade publicadora (campo customizado ou fallback)"""
        return getattr(brain, "unidade", "") or ""
