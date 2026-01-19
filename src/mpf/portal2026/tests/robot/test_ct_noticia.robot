# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s mpf.portal2026 -t test_noticia.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src mpf.portal2026.testing.MPF_PORTAL2026_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/mpf/portal2026/tests/robot/test_noticia.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a site administrator I can add a Noticia
  Given a logged-in site administrator
    and an add Noticia form
   When I type 'My Noticia' into the title field
    and I submit the form
   Then a Noticia with the title 'My Noticia' has been created

Scenario: As a site administrator I can view a Noticia
  Given a logged-in site administrator
    and a Noticia 'My Noticia'
   When I go to the Noticia view
   Then I can see the Noticia title 'My Noticia'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Noticia form
  Go To  ${PLONE_URL}/++add++Noticia

a Noticia 'My Noticia'
  Create content  type=Noticia  id=my-noticia  title=My Noticia

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Noticia view
  Go To  ${PLONE_URL}/my-noticia
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Noticia with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Noticia title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
