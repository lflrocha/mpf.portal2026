# -*- coding: utf-8 -*-
from plone.dexterity.content import Item
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from zope.interface import implementer
from zope import schema

from z3c.relationfield.schema import RelationChoice
from plone.app.vocabularies.catalog import CatalogSource
from plone.namedfile.field import NamedBlobImage

class ICapa(model.Schema):
    """Schema do tipo Capa"""

    noticia_1 = RelationChoice(
        title=u"Notícia 1",
        required=False,
        source=CatalogSource(portal_type="Noticia"),
    )

    noticia_2 = RelationChoice(
        title=u"Notícia 2",
        required=False,
        source=CatalogSource(portal_type="Noticia"),
    )

    noticia_3 = RelationChoice(
        title=u"Notícia 3",
        required=False,
        source=CatalogSource(portal_type="Noticia"),
    )

    # ==================== ABA: Destaques Últimas ====================
    fieldset(
        u"Destaques Últimas",
        fields=[
            "du1_chapeu", "du1_titulo", "du1_imagem", "du1_link",
            "du2_chapeu", "du2_titulo", "du2_imagem", "du2_link",
            "du3_chapeu", "du3_titulo", "du3_imagem", "du3_link",
        ],
    )

    du1_chapeu = schema.TextLine(title=u"Destaque 1: Chapéu", required=True)
    du1_titulo = schema.TextLine(title=u"Destaque 1: Título", required=True)
    du1_imagem = NamedBlobImage(title=u"Destaque 1: Imagem", required=True)
    du1_link = schema.URI(title=u"Destaque 1: Link", required=True)

    du2_chapeu = schema.TextLine(title=u"Destaque 2: Chapéu", required=True)
    du2_titulo = schema.TextLine(title=u"Destaque 2: Título", required=True)
    du2_imagem = NamedBlobImage(title=u"Destaque 2: Imagem", required=True)
    du2_link = schema.URI(title=u"Destaque 2: Link", required=True)

    du3_chapeu = schema.TextLine(title=u"Destaque 3: Chapéu", required=True)
    du3_titulo = schema.TextLine(title=u"Destaque 3: Título", required=True)
    du3_imagem = NamedBlobImage(title=u"Destaque 3: Imagem", required=True)
    du3_link = schema.URI(title=u"Destaque 3: Link", required=True)

    # ==================== ABA: Em foco ====================
    fieldset(
        u"Em foco",
        fields=[
            "ef1_chapeu", "ef1_titulo", "ef1_imagem", "ef1_link",
            "ef2_chapeu", "ef2_titulo", "ef2_imagem", "ef2_link",
            "ef3_chapeu", "ef3_titulo", "ef3_imagem", "ef3_link",
        ],
    )

    ef1_chapeu = schema.TextLine(title=u"Conteúdo 1: Chapéu", required=True)
    ef1_titulo = schema.TextLine(title=u"Conteúdo 1: Título", required=True)
    ef1_imagem = NamedBlobImage(title=u"Conteúdo 1: Imagem", required=True)
    ef1_link = schema.URI(title=u"Conteúdo 1: Link", required=True)

    ef2_chapeu = schema.TextLine(title=u"Conteúdo 2: Chapéu", required=True)
    ef2_titulo = schema.TextLine(title=u"Conteúdo 2: Título", required=True)
    ef2_imagem = NamedBlobImage(title=u"Conteúdo 2: Imagem", required=True)
    ef2_link = schema.URI(title=u"Conteúdo 2: Link", required=True)

    ef3_chapeu = schema.TextLine(title=u"Conteúdo 3: Chapéu", required=True)
    ef3_titulo = schema.TextLine(title=u"Conteúdo 3: Título", required=True)
    ef3_imagem = NamedBlobImage(title=u"Conteúdo 3: Imagem", required=True)
    ef3_link = schema.URI(title=u"Conteúdo 3: Link", required=True)




@implementer(ICapa)
class Capa(Item):
    pass
