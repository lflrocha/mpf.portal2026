# -*- coding: utf-8 -*-
# from plone.app.textfield import RichText
# from plone.autoform import directives
from plone.dexterity.content import Container

# from plone.namedfile import field as namedfile
from plone.supermodel import model

from plone.supermodel.directives import fieldset
# from z3c.form.browser.radio import RadioFieldWidget
# from zope import schema
from zope.interface import implementer
from zope import schema
from plone.autoform import directives
# from mpf.portal2026 import _


class INoticia(model.Schema):
    """ Marker interface and Dexterity Python Schema for Noticia
    """
    # If you want, you can load a xml model created TTW here
    # and customize it in Python:

    # model.load('noticia.xml')

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

    temas = schema.List(
        title=u"Temas da notícia",
        required=True,
        value_type=schema.Choice(vocabulary="mpf.portal2026.noticiatemas"),
    )

    unidadeOrigem = schema.Choice(
        title=u"Unidade de origem",
        required=True,
        missing_value=u"",
        vocabulary="mpf.portal2026.unidades_origem",
    )

    # directives.read_permission(notes='cmf.ManagePortal')
    # directives.write_permission(notes='cmf.ManagePortal')
    # notes = RichText(
    #     title=_(u'Secret Notes (only for site-admins)'),
    #     required=False
    # )


@implementer(INoticia)
class Noticia(Container):
    """ Content-type class for INoticia
    """
