# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

import mpf.portal2026


class MpfPortal2026Layer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        import plone.restapi
        self.loadZCML(package=plone.restapi)
        self.loadZCML(package=mpf.portal2026)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'mpf.portal2026:default')


MPF_PORTAL2026_FIXTURE = MpfPortal2026Layer()


MPF_PORTAL2026_INTEGRATION_TESTING = IntegrationTesting(
    bases=(MPF_PORTAL2026_FIXTURE,),
    name='MpfPortal2026Layer:IntegrationTesting',
)


MPF_PORTAL2026_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(MPF_PORTAL2026_FIXTURE,),
    name='MpfPortal2026Layer:FunctionalTesting',
)


MPF_PORTAL2026_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        MPF_PORTAL2026_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='MpfPortal2026Layer:AcceptanceTesting',
)
