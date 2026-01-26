from Products.Five.browser import BrowserView
from plone.dexterity.utils import iterSchemata
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
