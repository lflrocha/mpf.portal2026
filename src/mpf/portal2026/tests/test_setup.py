# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from mpf.portal2026.testing import MPF_PORTAL2026_INTEGRATION_TESTING  # noqa: E501
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID

import unittest


try:
    from Products.CMFPlone.utils import get_installer
except ImportError:
    get_installer = None


class TestSetup(unittest.TestCase):
    """Test that mpf.portal2026 is properly installed."""

    layer = MPF_PORTAL2026_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')

    def test_product_installed(self):
        """Test if mpf.portal2026 is installed."""
        self.assertTrue(self.installer.is_product_installed(
            'mpf.portal2026'))

    def test_browserlayer(self):
        """Test that IMpfPortal2026Layer is registered."""
        from mpf.portal2026.interfaces import IMpfPortal2026Layer
        from plone.browserlayer import utils
        self.assertIn(
            IMpfPortal2026Layer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = MPF_PORTAL2026_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        if get_installer:
            self.installer = get_installer(self.portal, self.layer['request'])
        else:
            self.installer = api.portal.get_tool('portal_quickinstaller')
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstall_product('mpf.portal2026')
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if mpf.portal2026 is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed(
            'mpf.portal2026'))

    def test_browserlayer_removed(self):
        """Test that IMpfPortal2026Layer is removed."""
        from mpf.portal2026.interfaces import IMpfPortal2026Layer
        from plone.browserlayer import utils
        self.assertNotIn(IMpfPortal2026Layer, utils.registered_layers())
