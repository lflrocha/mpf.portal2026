# -*- coding: utf-8 -*-
from plone.app.layout.viewlets.common import ViewletBase
from zope.component import queryMultiAdapter
from Products.CMFCore.utils import getToolByName

from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.layout.navigation.root import getNavigationRootObject


class HeaderMPFViewlet(ViewletBase):
    """Header MPF - viewlet estático global."""

    def menu_tree(self, depth=3):
        request = self.request
        context = self.context

        root = getNavigationRootObject(context, request)
        root_path = '/'.join(root.getPhysicalPath())

        strategy = queryMultiAdapter((context, request), INavtreeStrategy)
        if strategy is None:
            # Sem strategy registrada: não dá para usar o navtree padrão
            return self._menu_tree_fallback(root_path, depth=3)

        query = {
            'path': {'query': root_path, 'depth': 3},
            'sort_on': 'getObjPositionInParent',
        }

        tree = buildFolderTree(context, obj=root, query=query, strategy=strategy)
        return tree.get('children', [])

    def _menu_tree_fallback(self, root_path, depth=3):
        catalog = getToolByName(self.context, 'portal_catalog')

        brains = catalog(
            path={'query': root_path, 'depth': depth},
            sort_on='getObjPositionInParent',
            review_state='published',   # importante se você testa como Anonymous
            # portal_type=['Folder', 'Document'],  # se quiser limitar
        )

        # debug rápido (opcional):
        # import logging; logging.getLogger('mpf.portal2026').warning("MENU root=%s brains=%s", root_path, len(brains))

        nodes = {}
        for b in brains:
            path = b.getPath()
            nodes[path] = {
                'title': b.Title,
                'url': b.getURL(),
                'path': path,
                'children': [],
            }

        root_node = {'path': root_path, 'children': []}

        for path, node in nodes.items():
            if path == root_path:
                continue

            parent_path = path.rsplit('/', 1)[0]

            if parent_path == root_path:
                # <-- aqui está o pulo do gato: top-level entra direto no root
                root_node['children'].append(node)
                continue

            parent = nodes.get(parent_path)
            if parent:
                parent['children'].append(node)

        return root_node['children']



class FooterMPFViewlet(ViewletBase):
    """Footer MPF - viewlet estático global."""
    pass
