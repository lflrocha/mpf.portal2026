# -*- coding: utf-8 -*-
from zope import schema
from zope.interface import Interface


class INoticiaTemasSettings(Interface):
    noticiaTemas = schema.List(
        title=u"Temas das notícias",
        required=False,
        value_type=schema.TextLine(title=u"Item"),
        default=[]
    )
