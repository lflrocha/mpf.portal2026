# -*- coding: utf-8 -*-
import re
import unicodedata
from zope.interface import implementer
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm


DEFAULT_TEMAS = [
    u"Combate à Corrupção",
    u"Comunidades Tradicionais",
    u"Concursos",
    u"Constitucional",
    u"Consumidor e Ordem Econômica",
    u"Controle Externo da Atividade Policial",
    u"Cooperação Internacional",
    u"Criminal",
    u"Direitos do Cidadão",
    u"Eleitoral",
    u"Fiscalização de Atos Administrativos",
    u"Geral",
    u"Improbidade Administrativa",
    u"Indígenas",
    u"Meio Ambiente",
    u"Patrimônio Público",
    u"Patrimônio Cultural",
    u"Sistema Prisional",
    u"Transparência",
]

UNIDADES_ORIGEM = [
    ("pgr",  u"Procuradoria-Geral da República"),
    ("prr1", u"Procuradoria Regional da República da 1ª Região"),
    ("prr2", u"Procuradoria Regional da República da 2ª Região"),
    ("prr3", u"Procuradoria Regional da República da 3ª Região"),
    ("prr4", u"Procuradoria Regional da República da 4ª Região"),
    ("prr5", u"Procuradoria Regional da República da 5ª Região"),
    ("prr6", u"Procuradoria Regional da República da 6ª Região"),
    ("prac", u"Procuradoria da República no Acre"),
    ("pral", u"Procuradoria da República em Alagoas"),
    ("prap", u"Procuradoria da República no Amapá"),
    ("pram", u"Procuradoria da República no Amazonas"),
    ("prba", u"Procuradoria da República na Bahia"),
    ("prce", u"Procuradoria da República no Ceará"),
    ("prdf", u"Procuradoria da República no Distrito Federal"),
    ("pres", u"Procuradoria da República no Espírito Santo"),
    ("prgo", u"Procuradoria da República em Goiás"),
    ("prma", u"Procuradoria da República no Maranhão"),
    ("prmt", u"Procuradoria da República em Mato Grosso"),
    ("prms", u"Procuradoria da República em Mato Grosso do Sul"),
    ("prmg", u"Procuradoria da República em Minas Gerais"),
    ("prpa", u"Procuradoria da República no Pará"),
    ("prpb", u"Procuradoria da República na Paraíba"),
    ("prpr", u"Procuradoria da República no Paraná"),
    ("prpe", u"Procuradoria da República em Pernambuco"),
    ("prpi", u"Procuradoria da República no Piauí"),
    ("prrj", u"Procuradoria da República no Rio de Janeiro"),
    ("prrn", u"Procuradoria da República no Rio Grande do Norte"),
    ("prrs", u"Procuradoria da República no Rio Grande do Sul"),
    ("prro", u"Procuradoria da República em Rondônia"),
    ("prrr", u"Procuradoria da República em Roraima"),
    ("prsc", u"Procuradoria da República em Santa Catarina"),
    ("prsp", u"Procuradoria da República em São Paulo"),
    ("prse", u"Procuradoria da República em Sergipe"),
    ("prto", u"Procuradoria da República no Tocantins"),
    ("pfdc", u"Procuradoria Federal dos Direitos do Cidadão"),
]

def _tokenize(text):
    """Gera token ascii, lowercase e com hífens."""
    if text is None:
        return u""
    if not isinstance(text, str):
        text = str(text)

    # remove acentos
    text = unicodedata.normalize("NFKD", text)
    text = u"".join([c for c in text if not unicodedata.combining(c)])

    text = text.lower().strip()
    text = re.sub(r"\s+", "-", text)          # espaços -> hífen
    text = re.sub(r"[^a-z0-9\-]", "", text)   # remove resto
    text = re.sub(r"-{2,}", "-", text)        # evita hífen duplo
    return text


@implementer(IVocabularyFactory)
class NoticiaTemasVocabulary(object):
    def __call__(self, context):
        terms = []
        for title in DEFAULT_TEMAS:
            token = _tokenize(title)
            terms.append(SimpleTerm(value=title, token=token, title=title))
        return SimpleVocabulary(terms)


noticiatemas_vocab = NoticiaTemasVocabulary()


@implementer(IVocabularyFactory)
class UnidadesOrigemVocabulary(object):
    def __call__(self, context):
        terms = [
            SimpleTerm(value=u"", token="__novalue__", title=u"--- Selecione ---"),
        ]
        terms.extend([
            SimpleTerm(value=uid, token=uid, title=nome)
            for uid, nome in UNIDADES_ORIGEM
        ])
        return SimpleVocabulary(terms)

unidades_origem_vocab = UnidadesOrigemVocabulary()

