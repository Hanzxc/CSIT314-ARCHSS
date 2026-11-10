# Unit tests for US38 View IDP save statistics.
# conftest.py gives each test a fresh database with the default users (cust001 is the customer).
# Designer tests add designer37 / Design@123 (profile 2) - helpers come from the US37 tests.

from app import app
from entity.userAccount import UserAccount
from entity.idpAnalytics import IDPAnalytics
from control.viewIDPSaveStatisticsController import ViewIDPSaveStatisticsController
from boundary.viewIDPSaveStatisticsPage import MSG_NO_IDPS
from control.customerLoginController import REQUIRED_CUSTOMER_PERMISSIONS
from test_us37_viewIDPViewStatistics import (createDesigner, loginAsDesigner, customerId,
                                             createCategory, addIDP, addSave, addView)


def createCustomer(username):
    UserAccount().createUserAccount(UserAccount(username=username, password="Cust@123", fullName="Another Customer",
                                    email=username + "@archss.com", phone="", profileId=3))
    return UserAccount().verifyCredentials(username, "Cust@123", REQUIRED_CUSTOMER_PERMISSIONS).userId


# ---------- IDPAnalytics.getSaveStatistics() ----------

def test_ut38_1_getSaveStatistics_noIDPs():
    assert IDPAnalytics().getSaveStatistics(createDesigner()) == []


def test_ut38_2_getSaveStatistics_countsCustomersIncludingZero():
    designer = createDesigner()
    kitchen = createCategory("Kitchen")
    popular = addIDP(designer, kitchen, "Modern Kitchen")
    unsaved = addIDP(designer, kitchen, "Old Kitchen", "Past")
    addSave(customerId(), popular)
    addSave(createCustomer("cust038"), popular)
    counts = {row.idpId: row.saves for row in IDPAnalytics().getSaveStatistics(designer)}
    assert counts == {popular: 2, unsaved: 0}


def test_ut38_3_getSaveStatistics_onlyOwnIDPs():
    designer = createDesigner()
    other = createDesigner("designer37b")
    kitchen = createCategory("Kitchen")
    own = addIDP(designer, kitchen, "Own Kitchen")
    addSave(customerId(), addIDP(other, kitchen, "Someone Else's Kitchen"))
    assert [row.idpId for row in IDPAnalytics().getSaveStatistics(designer)] == [own]


def test_ut38_4_getSaveStatistics_skipsDeletedIDPs():
    designer = createDesigner()
    addIDP(designer, createCategory("Kitchen"), "Deleted Kitchen", status="Suspended")
    assert IDPAnalytics().getSaveStatistics(designer) == []


def test_ut38_5_getSaveStatistics_mostSavedFirst_viewsDontCount():
    designer = createDesigner()
    kitchen = createCategory("Kitchen")
    viewedOnly = addIDP(designer, kitchen, "A Kitchen")
    saved = addIDP(designer, kitchen, "B Kitchen")
    for _ in range(5):
        addView(viewedOnly)
    addSave(customerId(), saved)
    rows = IDPAnalytics().getSaveStatistics(designer)
    assert [(row.idpId, row.saves) for row in rows] == [(saved, 1), (viewedOnly, 0)]


def test_ut38_6_customerSavingThroughUS33_isCounted():
    designer = createDesigner()
    idpId = addIDP(designer, createCategory("Kitchen"), "Modern Kitchen")
    from entity.savedIDP import SavedIDP
    SavedIDP().createSavedRecord(customerId(), idpId)             # US33 save
    SavedIDP().createSavedRecord(customerId(), idpId)             # saving twice doesn't count twice
    assert IDPAnalytics().getSaveStatistics(designer)[0].saves == 1


# ---------- ViewIDPSaveStatisticsController.getSaveStatistics() ----------

def test_ut38_7_controller_passesDesignerThrough():
    designer = createDesigner()
    idpId = addIDP(designer, createCategory("Kitchen"), "Modern Kitchen")
    addSave(customerId(), idpId)
    fromController = ViewIDPSaveStatisticsController().getSaveStatistics(designer)
    fromEntity = IDPAnalytics().getSaveStatistics(designer)
    assert [(row.idpId, row.saves) for row in fromController] == \
        [(row.idpId, row.saves) for row in fromEntity] == [(idpId, 1)]


# ---------- ViewIDPSaveStatisticsPage (through the Flask route) ----------

def test_ut38_8_page_showsTableOfOwnIDPs():
    designer = createDesigner()
    addSave(customerId(), addIDP(designer, createCategory("Kitchen"), "Modern Kitchen"))
    client = app.test_client()
    loginAsDesigner(client)
    response = client.get("/designer/idps/statistics/saves")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Modern Kitchen" in html and "Customers who saved it" in html
    assert "<strong>1</strong>" in html


def test_ut38_9_page_noIDPs_showsMessage():
    createDesigner()
    client = app.test_client()
    loginAsDesigner(client)
    html = client.get("/designer/idps/statistics/saves").get_data(as_text=True)
    assert MSG_NO_IDPS.replace("'", "&#39;") in html
    assert "<table" not in html


def test_ut38_10_page_notLoggedIn_redirectsToDesignerLogin():
    response = app.test_client().get("/designer/idps/statistics/saves")
    assert response.status_code == 302
    assert "/designer/login" in response.headers["Location"]


def test_ut38_11_page_viewsAndSavesTabsLinkToEachOther():
    createDesigner()
    client = app.test_client()
    loginAsDesigner(client)
    html = client.get("/designer/idps/statistics/saves").get_data(as_text=True)
    assert 'href="/designer/idps/statistics/views"' in html
    assert 'href="/designer/idps/statistics/saves"' in html


def test_ut38_12_page_hintUnderTable_eachCustomerCountedOnce():
    designer = createDesigner()
    addSave(customerId(), addIDP(designer, createCategory("Kitchen"), "Modern Kitchen"))
    client = app.test_client()
    loginAsDesigner(client)
    html = client.get("/designer/idps/statistics/saves").get_data(as_text=True)
    assert html.index("</table>") < html.index("Each customer who saved the IDP is counted once.")
