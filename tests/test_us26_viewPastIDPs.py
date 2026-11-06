# Unit tests for US26 View past IDPs.
# conftest.py gives each test a fresh database. Helpers come from the US25 and US37 tests.

from app import app
from entity.idp import IDP
from control.viewPastIDPController import ViewPastIDPController
from boundary.pastIDPListPage import MSG_NO_PAST_IDPS, MSG_NOT_FOUND
from test_us37_viewIDPViewStatistics import createDesigner, createCategory, addIDP
from test_us25_addPastIDP import loggedInDesigner, addPast


# ---------- IDP.findPastIDPsByDesignerId() / getPastIDPDetails() ----------

def test_ut26_1_findPastIDPs_onlyOwnActivePastNewestFirst():
    designer = createDesigner()
    other = createDesigner("designer26b")
    kitchen = createCategory("Kitchen")
    older = addPast(designer, kitchen, "Older Kitchen")
    newer = addPast(designer, kitchen, "Newer Kitchen")
    addPast(designer, kitchen, "Deleted Kitchen", status="Suspended")
    addIDP(designer, kitchen, "Current Kitchen")                  # Current, not Past
    addPast(other, kitchen, "Someone Else's Kitchen")
    assert [idp.idpId for idp in IDP().findPastIDPsByDesignerId(designer)] == [newer, older]


def test_ut26_2_findPastIDPs_includesCategoryName():
    designer = createDesigner()
    addPast(designer, createCategory("Kitchen"))
    assert IDP().findPastIDPsByDesignerId(designer)[0].categoryName == "Kitchen"


def test_ut26_3_getPastIDPDetails_ownVsOtherDesigner():
    designer = createDesigner()
    other = createDesigner("designer26b")
    idpId = addPast(designer, createCategory("Kitchen"))
    assert IDP().getPastIDPDetails(designer, idpId).title == "Completed Kitchen"
    assert IDP().getPastIDPDetails(other, idpId) is None
    assert IDP().getPastIDPDetails(designer, 999999) is None


# ---------- ViewPastIDPController ----------

def test_ut26_4_controller_passesThrough():
    designer = createDesigner()
    idpId = addPast(designer, createCategory("Kitchen"))
    controller = ViewPastIDPController()
    assert [idp.idpId for idp in controller.getPastIDPs(designer)] == [idpId]
    assert controller.getPastIDPDetails(designer, idpId).idpId == idpId


# ---------- PastIDPListPage through the Flask routes ----------

def test_ut26_5_page_listShowsOwnPastIDPs():
    client, designer = loggedInDesigner()
    addPast(designer, createCategory("Kitchen"), "Completed Kitchen")
    html = client.get("/designer/past-idps").get_data(as_text=True)
    assert "My past IDPs" in html and "Completed Kitchen" in html


def test_ut26_6_page_noPastIDPs_showsEmptyMessage():
    client, _ = loggedInDesigner()
    html = client.get("/designer/past-idps").get_data(as_text=True)
    assert MSG_NO_PAST_IDPS in html


def test_ut26_7_page_detailsShowEverything():
    client, designer = loggedInDesigner()
    idpId = addPast(designer, createCategory("Kitchen"))
    html = client.get(f"/designer/past-idps/{idpId}").get_data(as_text=True)
    assert "Completed Kitchen" in html and "Kitchen" in html and "Test project" in html
    assert f"/designer/past-idps/{idpId}/edit" in html and f"/designer/past-idps/{idpId}/delete" in html


def test_ut26_8_page_otherDesignersIDP_notFound():
    client, _ = loggedInDesigner()
    other = createDesigner("designer26b")
    idpId = addPast(other, createCategory("Kitchen"))
    response = client.get(f"/designer/past-idps/{idpId}")
    assert response.status_code == 404 and MSG_NOT_FOUND in response.get_data(as_text=True)


def test_ut26_9_page_notLoggedIn_redirectsToDesignerLogin():
    response = app.test_client().get("/designer/past-idps")
    assert response.status_code == 302 and "/designer/login" in response.headers["Location"]


def test_ut26_10_dashboardAndMenu_linkToPastIDPs():
    client, _ = loggedInDesigner()
    html = client.get("/designer/dashboard").get_data(as_text=True)
    assert html.count('href="/designer/past-idps"') == 2 and 'href="/designer/past-idps/add"' in html
