# -*- coding: utf-8 -*-
from Products.Five import BrowserView
from zope.component import getMultiAdapter


class ContatoView(BrowserView):
    """View customizada para Document."""

    def breadcrumbs(self):
        """
        Retorna a lista de breadcrumbs no formato do Plone:
        [{'Title': '...', 'absolute_url': '...'}, ...]
        """
        bc = getMultiAdapter((self.context, self.request), name="breadcrumbs_view")
        return bc.breadcrumbs()

    def contato(self):
        text = getattr(self.context, "contato", None)
        if not text:
            return u""
        return text.output or u""

    def endereco(self):
        text = getattr(self.context, "endereco", None)
        if not text:
            return u""
        return text.output or u""

    def descricao(self):
        text = getattr(self.context, "como_chegar", None)
        return text
