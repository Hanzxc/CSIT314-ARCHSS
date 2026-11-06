# Unit tests for US27 Update past IDP.
# conftest.py gives each test a fresh database. Helpers come from the US25 and US37 tests.

from app import app
from entity.idp import IDP
from control.updatePastIDPController import UpdatePastIDPController
from boundary.editPastIDPPage import MSG_UPDATED, MSG_FIX_FIELDS, MSG_NOT_FOUND
from test_us37_viewIDPViewStatistics import createDesigner, createCategory, addIDP
from test_us25_addPastIDP import loggedInDesigner, addPast, form, pastIDPRow


def changed(idpId, designerId, categoryId, title="Renamed Kitchen"):
    return IDP(idpId=idpId, designerId=designerId, categoryId=categoryId, title=title,
               description="New description", location="Bishan")


# ---------- IDP.updatePastIDPDetails() ----------

def test_ut27_1_update_ownPastIDP():
    designer = createDesigner()
    kitchen = createCategory("Kitchen")
    bedroom = createCategory("Bedroom")
    idpId = addPast(designer, kitchen)
    assert IDP().updatePastIDPDetails(changed(idpId, designer, bedroom)) is True
    row = pastIDPRow("Renamed Kitchen")
    assert row["categoryId"] == bedroom and row["location"] == "Bishan" and row["projectType"] == "Past"


def test_ut27_2_update_otherDesignersIDP_refused():
    designer = createDesigner()
    other = createDesigner("designer27b")
    kitchen = createCategory("Kitchen")
    idpId = addPast(designer, kitchen)
    assert IDP().updatePastIDPDetails(changed(idpId, other, kitchen)) is False
    assert pastIDPRow("Completed Kitchen") is not None


def test_ut27_3_update_suspendedCategoryOrDeletedOrCurrent_refused():
    designer = createDesigner()
    kitchen = createCategory("Kitchen")
    hidden = createCategory("Old Style", "Suspended")
    idpId = addPast(designer, kitchen)
    deleted = addPast(designer, kitchen, "Deleted", status="Suspended")
    current = addIDP(designer, kitchen, "Current One")
    assert IDP().updatePastIDPDetails(changed(idpId, designer, hidden)) is False
    assert IDP().updatePastIDPDetails(changed(deleted, designer, kitchen, "Deleted 2")) is False
    assert IDP().updatePastIDPDetails(changed(current, designer, kitchen, "Current 2")) is False


# ---------- UpdatePastIDPController ----------

def test_ut27_4_controller_passesThrough():
    designer = createDesigner()
    kitchen = createCategory("Kitchen")
    idpId = addPast(designer, kitchen)
    controller = UpdatePastIDPController()
    assert controller.getPastIDP(designer, idpId).title == "Completed Kitchen"
    assert controller.updatePastIDP(changed(idpId, designer, kitchen)) is True


# ---------- EditPastIDPPage through the Flask route ----------

def test_ut27_5_page_openForm_filledInWithCurrentDetails():
    client, designer = loggedInDesigner()
    idpId = addPast(designer, createCategory("Kitchen"))
    html = client.get(f"/designer/past-idps/{idpId}/edit").get_data(as_text=True)
    assert "Update past IDP" in html and 'value="Completed Kitchen"' in html and "Test project" in html


def test_ut27_6_page_submitValid_savesAndShowsSuccess():
    client, designer = loggedInDesigner()
    idpId = addPast(designer, createCategory("Kitchen"))
    kitchen = pastIDPRow("Completed Kitchen")["categoryId"]
    response = client.post(f"/designer/past-idps/{idpId}/edit", data=form(kitchen, title="Renamed Kitchen"),
                           follow_redirects=True)
    html = response.get_data(as_text=True)
    assert MSG_UPDATED in html and "Renamed Kitchen" in html


def test_ut27_7_page_missingTitle_nothingChanged():
    client, designer = loggedInDesigner()
    kitchen = createCategory("Kitchen")
    idpId = addPast(designer, kitchen)
    html = client.post(f"/designer/past-idps/{idpId}/edit", data=form(kitchen, title="")).get_data(as_text=True)
    assert MSG_FIX_FIELDS in html
    assert pastIDPRow("Completed Kitchen") is not None


def test_ut27_8_page_otherDesignersIDP_notFound():
    client, _ = loggedInDesigner()
    other = createDesigner("designer27b")
    kitchen = createCategory("Kitchen")
    idpId = addPast(other, kitchen)
    assert client.get(f"/designer/past-idps/{idpId}/edit").status_code == 404
    response = client.post(f"/designer/past-idps/{idpId}/edit", data=form(kitchen, title="Hijacked"))
    assert response.status_code == 404 and MSG_NOT_FOUND in response.get_data(as_text=True)
    assert pastIDPRow("Hijacked") is None


def test_ut27_9_page_notLoggedIn_redirectsToDesignerLogin():
    response = app.test_client().get("/designer/past-idps/1/edit")
    assert response.status_code == 302 and "/designer/login" in response.headers["Location"]
