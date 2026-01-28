from plone.app.contenttypes.behaviors.leadimage import ILeadImageBehavior
from plone.app.relationfield.behavior import IRelatedItems
from plone.dexterity.utils import iterSchemata
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from zope.component import getMultiAdapter
from zope.schema import getFieldsInOrder
from zope.schema.vocabulary import getVocabularyRegistry


class NoticiaView(BrowserView):

    def _field(self, name):
        for schema in iterSchemata(self.context):
            for fname, field in getFieldsInOrder(schema):
                if fname == name:
                    return field
        return None

    def _get_vocab(self, field):
        """Resolve vocabulário tanto para Choice quanto para List/Tuple de Choice."""
        # Se for lista/tupla, o Choice geralmente está em value_type
        choice = getattr(field, "value_type", None) or field

        # 1) vocabulário já “embutido”
        vocab = getattr(choice, "vocabulary", None)
        if vocab is not None:
            return vocab

        # 2) vocabulário por nome (vocabularyName)
        vocab_name = getattr(choice, "vocabularyName", None)
        if vocab_name:
            registry = getVocabularyRegistry()
            return registry.get(self.context, vocab_name)

        return None

    def _labels(self, fieldname):
        field = self._field(fieldname)
        if field is None:
            return []

        value = getattr(self.context, fieldname, None)
        if not value:
            return []

        tokens = list(value) if isinstance(value, (list, tuple, set)) else [value]

        vocab = self._get_vocab(field)
        if vocab is None:
            # fallback: sem vocabulário, devolve o que tem
            return [str(t) for t in tokens]

        labels = []
        for token in tokens:
            try:
                term = vocab.getTerm(token)
                labels.append(getattr(term, "title", token))
            except Exception:
                labels.append(str(token))
        return labels

    def tipo_noticia(self):
        return ", ".join(self._labels("tema"))

    def unidade_origem(self):
        return ", ".join(self._labels("unidadeOrigem"))

    def titulo(self):
        return self.context.title

    def descricao(self):
        return getattr(self.context, "description", "")


    def corpo_html(self):
        """Retorna o corpo (RichText) como HTML."""
        # tenta nomes comuns
        rich = getattr(self.context, "text", None)

        if not rich:
            return ""

        # RichText em Plone tem .output (HTML renderizado) e .raw (original)
        try:
            return rich.output or ""
        except Exception:
            return ""




    def breadcrumbs(self):
        """
        Retorna a lista de breadcrumbs no formato do Plone:
        [{'Title': '...', 'absolute_url': '...'}, ...]
        """
        bc = getMultiAdapter((self.context, self.request), name="breadcrumbs_view")
        return bc.breadcrumbs()


    def data_modificacao_formatada(self):
        """
        Retorna a data de modificação no formato:
        DD/MM/AAAA • HH:MM
        """
        dt = self.context.modified()
        if not dt:
            return ""

        data = dt.strftime("%d/%m/%Y")
        hora = dt.strftime("%H:%M")
        return f"{data} • {hora}"


    def anexos(self):
        """
        Lista arquivos (File) dentro da Notícia.
        Retorna uma lista de dicts: title, url, size_bytes, size_human, filename
        """
        catalog = getToolByName(self.context, "portal_catalog")

        brains = catalog(
            portal_type="File",
            path={"query": "/".join(self.context.getPhysicalPath()), "depth": 1},
            sort_on="getObjPositionInParent",
        )

        items = []
        for b in brains:
            obj = b.getObject()

            # Em Plone/Dexterity File: arquivo costuma estar em obj.file
            f = getattr(obj, "file", None)

            size_bytes = 0
            filename = ""

            if f:
                # NamedBlobFile / NamedFile
                size_bytes = getattr(f, "size", 0) or 0
                filename = getattr(f, "filename", "") or ""

            items.append({
                "title": obj.title or b.Title or filename or "Arquivo",
                "url": obj.absolute_url(),
                "size_bytes": size_bytes,
                "size_human": self._human_size(size_bytes),
                "filename": filename,
            })

        return items

    def _human_size(self, num):
        # Formato simples: B, KB, MB, GB
        try:
            num = int(num or 0)
        except Exception:
            num = 0

        for unit in ["B", "KB", "MB", "GB", "TB"]:
            if num < 1024 or unit == "TB":
                if unit == "B":
                    return f"{num} {unit}"
                return f"{num/1024:.0f} {unit}" if unit == "KB" else f"{num/1024/1024:.1f} MB" if unit == "MB" else f"{num:.1f} {unit}"
            num = num / 1024
        return "0 B"


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


    def imagem_noticia(self):
        """
        Retorna dict com dados da imagem da notícia:
        {
          url: URL da imagem (escala large),
          alt: texto alternativo,
          exists: True/False
        }
        """
        ctx = self.context

        # 1) Lead Image behavior
        if ILeadImageBehavior is not None:
            lead = ILeadImageBehavior(ctx, None)
            if lead and lead.image:
                return {
                    "url": f"{ctx.absolute_url()}/@@images/image/large",
                    "alt": lead.image_caption or ctx.Title(),
                    "exists": True,
                }

        # 2) Campo image/imagem direto no schema
        for fieldname in ("image", "imagem"):
            img = getattr(ctx, fieldname, None)
            if img:
                return {
                    "url": f"{ctx.absolute_url()}/@@images/{fieldname}/large",
                    "alt": ctx.Title(),
                    "exists": True,
                }

        return {
            "exists": False,
        }
