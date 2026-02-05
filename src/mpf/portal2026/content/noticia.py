# -*- coding: utf-8 -*-
from plone.autoform import directives
from plone.dexterity.content import Container
from plone.supermodel import model
from plone.supermodel.directives import fieldset
from zope import schema
from zope.interface import implementer



class INoticia(model.Schema):
    """Marker interface and Dexterity Python Schema for Noticia"""

    tituloAlternativo = schema.TextLine(
        title=u"Título alternativo",
        description=u"Título que será usado quando a notícia aparecer na capa do portal",
        required=False,
    )

    descricaoAlternativa = schema.Text(
        title=u"Descrição alternativa",
        description=u"Descrição de apoio que será exibida junto ao título alternativo na capa do portal",
        required=False,
    )

    tema = schema.Choice(
        title=u"Tema da notícia",
        required=True,
        missing_value=u"",
        vocabulary="mpf.portal2026.noticiatemas",
    )

    unidadeOrigem = schema.Choice(
        title=u"Unidade de origem",
        required=True,
        missing_value=u"",
        vocabulary="mpf.portal2026.unidades_origem",
    )

    # ------------------------------------------------------------------
    # IMAGEM
    # ------------------------------------------------------------------

    directives.order_after(creditoImagem="ILeadImageBehavior.image_caption")
    creditoImagem = schema.TextLine(
        title=u"Crédito da imagem",
        description=u"Autor, fotógrafo ou fonte da imagem",
        required=False,
    )
    directives.order_after(descricaoImagem="creditoImagem")
    descricaoImagem = schema.Text(
        title=u"Descrição da imagem",
        description=u"Descrição textual para acessibilidade (texto alternativo)",
        required=False,
    )



@implementer(INoticia)
class Noticia(Container):
    """Content-type class for INoticia"""
