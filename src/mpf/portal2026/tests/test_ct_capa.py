# -*- coding: utf-8 -*-
from mpf.portal2026.content.capa import ICapa  # NOQA E501
from mpf.portal2026.testing import MPF_PORTAL2026_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest


class CapaIntegrationTest(unittest.TestCase):

    layer = MPF_PORTAL2026_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.parent = self.portal

    def test_ct_capa_schema(self):
        fti = queryUtility(IDexterityFTI, name='Capa')
        schema = fti.lookupSchema()
        self.assertEqual(ICapa, schema)

    def test_ct_capa_fti(self):
        fti = queryUtility(IDexterityFTI, name='Capa')
        self.assertTrue(fti)

    def test_ct_capa_factory(self):
        fti = queryUtility(IDexterityFTI, name='Capa')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            ICapa.providedBy(obj),
            u'ICapa not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_capa_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='Capa',
            id='capa',
        )

        self.assertTrue(
            ICapa.providedBy(obj),
            u'ICapa not provided by {0}!'.format(
                obj.id,
            ),
        )

        parent = obj.__parent__
        self.assertIn('capa', parent.objectIds())

        # check that deleting the object works too
        api.content.delete(obj=obj)
        self.assertNotIn('capa', parent.objectIds())

    def test_ct_capa_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='Capa')
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )
