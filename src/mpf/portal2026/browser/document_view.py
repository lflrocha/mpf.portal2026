# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from plone import api
from zope.component import getMultiAdapter


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
