# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from plone import api
from zope.component import getMultiAdapter
from plone.app.relationfield.behavior import IRelatedItems

class DocumentView(BrowserView):
    """View customizada para Document."""

    def titulo(self):
        return self.context.Title()

    def descricao(self):
        return self.context.Description()

    def corpo_html(self):
        text = getattr(self.context, "text", None)
        if not text:
            return u""
        return text.output or u""

    def breadcrumbs(self):
        """
        Retorna a lista de breadcrumbs no formato do Plone:
        [{'Title': '...', 'absolute_url': '...'}, ...]
        """
        bc = getMultiAdapter((self.context, self.request), name="breadcrumbs_view")
        return bc.breadcrumbs()

    def relacionados(self, limit=6):
        """
        Retorna lista de itens relacionados (Related Items) do Plone.
        Cada item vira um dict com title, url, description, portal_type.
        """
        if IRelatedItems is None:
            return []

        # Pega os relatedItems via behavior
        rel = IRelatedItems(self.context, None)
        if not rel:
            return []

        values = getattr(rel, 'relatedItems', None) or []
        if not values:
            return []

        items = []
        for v in values:
            # RelationValue -> objeto
            obj = getattr(v, 'to_object', None)
            if obj is None:
                # fallback (alguns casos expõem toObject)
                obj = getattr(v, 'toObject', None)

            if obj is None:
                continue

            items.append({
                'title': obj.Title() if hasattr(obj, 'Title') else getattr(obj, 'title', u''),
                'url': obj.absolute_url(),
                'description': obj.Description() if hasattr(obj, 'Description') else getattr(obj, 'description', u''),
                'portal_type': getattr(obj, 'portal_type', ''),
            })

            if limit and len(items) >= limit:
                break

        return items
