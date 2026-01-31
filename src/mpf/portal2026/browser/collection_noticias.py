from Products.Five import BrowserView
from plone import api
from plone.app.contenttypes.behaviors.collection import ICollection

class CollectionSummaryView(BrowserView):

    def get_results(self):
        # Tentativa 1: Via Behavior (A forma correta do Plone 5.2)
        collection = ICollection(self.context, None)
        if collection is not None:
            return collection.results(batch=True, b_size=10)

        # Tentativa 2: Fallback manual (Caso o behavior falhe por algum motivo de estado)
        catalog = api.portal.get_tool(name='portal_catalog')
        # No Dexterity, usamos getQuery() para pegar o dicionário pronto para o catálogo
        query = self.context.getQuery()
        if query:
            return catalog(query)

        return []
