# -*- coding: utf-8 -*-
from mpf.portal2026.content.noticia import INoticia  # NOQA E501
from mpf.portal2026.testing import MPF_PORTAL2026_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest


class NoticiaIntegrationTest(unittest.TestCase):

    layer = MPF_PORTAL2026_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.parent = self.portal

    def test_ct_noticia_schema(self):
        fti = queryUtility(IDexterityFTI, name='Noticia')
        schema = fti.lookupSchema()
        self.assertEqual(INoticia, schema)

    def test_ct_noticia_fti(self):
        fti = queryUtility(IDexterityFTI, name='Noticia')
        self.assertTrue(fti)

    def test_ct_noticia_factory(self):
        fti = queryUtility(IDexterityFTI, name='Noticia')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            INoticia.providedBy(obj),
            u'INoticia not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_noticia_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='Noticia',
            id='noticia',
        )

        self.assertTrue(
            INoticia.providedBy(obj),
            u'INoticia not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('noticia', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('noticia', parent.objectIds())

    def test_ct_noticia_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Noticia')
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )

    def test_ct_noticia_filter_content_type_false(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Noticia')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'noticia_id',
            title='Noticia container',
        )
        self.parent = self.portal[parent_id]
        obj = api.content.create(
            container=self.parent,
            type='Document',
            title='My Content',
        )
        self.assertTrue(
            obj,
            u'Cannot add {0} to {1} container!'.format(obj.id, fti.id)
        )
