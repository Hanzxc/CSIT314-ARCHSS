# Unit tests for US28 Delete past IDP.
# conftest.py gives each test a fresh database. Helpers come from the US25 and US37 tests.

from app import app
from entity.idp import IDP
from control.deletePastIDPController import DeletePastIDPController
from boundary.pastIDPListPage import MSG_DELETED, MSG_NOT_FOUND
from test_us37_viewIDPViewStatistics import createDesigner, createCategory, addIDP
from test_us25_addPastIDP import loggedInDesigner, addPast, pastIDPRow


# ---------- IDP.markPastIDPUnavailable() ----------

def test_ut28_1_delete_marksSuspendedButKeepsTheRow():
    designer = createDesigner()
    idpId = addPast(designer, createCategory("Kitchen"))
    assert IDP().markPastIDPUnavailable(designer, idpId) is True
    assert pastIDPRow("Completed Kitchen")["status"] == "Suspended"
    assert IDP().findPastIDPsByDesignerId(designer) == []


def test_ut28_2_delete_otherDesignerOrTwiceOrCurrent_refused():
    designer = createDesigner()
    other = createDesigner("designer28b")
    kitchen = createCategory("Kitchen")
    idpId = addPast(designer, kitchen)
    current = addIDP(designer, kitchen, "Current One")
    assert IDP().markPastIDPUnavailable(other, idpId) is False
    assert IDP().markPastIDPUnavailable(designer, current) is False
    assert IDP().markPastIDPUnavailable(designer, idpId) is True
    assert IDP().markPastIDPUnavailable(designer, idpId) is False          # already deleted


# ---------- DeletePastIDPController ----------

def test_ut28_3_controller_passesThrough():
    designer = createDesigner()
    idpId = addPast(designer, createCategory("Kitchen"))
    controller = DeletePastIDPController()
    assert controller.getPastIDP(designer, idpId).idpId == idpId
    assert controller.deletePastIDP(designer, idpId) is True
    assert controller.getPastIDP(designer, idpId) is None


# ---------- PastIDPListPage (delete part) through the Flask route ----------

def test_ut28_4_page_clickDelete_showsConfirmationBox():
    client, designer = loggedInDesigner()
    idpId = addPast(designer, createCategory("Kitchen"))
    html = client.get(f"/designer/past-idps/{idpId}/delete").get_data(as_text=True)
    assert "Delete past IDP?" in html and "Completed Kitchen" in html
    assert pastIDPRow("Completed Kitchen")["status"] == "Active"          # nothing deleted yet


def test_ut28_5_page_confirm_deletesAndRefreshesList():
    client, designer = loggedInDesigner()
    idpId = addPast(designer, createCategory("Kitchen"))
    response = client.post(f"/designer/past-idps/{idpId}/delete", data={"choice": "delete"},
                           follow_redirects=True)
    html = response.get_data(as_text=True)
    assert MSG_DELETED in html and "My past IDPs" in html
    assert pastIDPRow("Completed Kitchen")["status"] == "Suspended"


def test_ut28_6_page_cancel_keepsTheIDP():
    client, designer = loggedInDesigner()
    idpId = addPast(designer, createCategory("Kitchen"))
    response = client.post(f"/designer/past-idps/{idpId}/delete", data={"choice": "cancel"})
    assert response.status_code == 302 and response.headers["Location"].endswith(f"/designer/past-idps/{idpId}")
    assert pastIDPRow("Completed Kitchen")["status"] == "Active"


def test_ut28_7_page_otherDesignersIDP_notFound():
    client, _ = loggedInDesigner()
    other = createDesigner("designer28b")
    idpId = addPast(other, createCategory("Kitchen"))
    assert client.get(f"/designer/past-idps/{idpId}/delete").status_code == 404
    response = client.post(f"/designer/past-idps/{idpId}/delete", data={"choice": "delete"})
    assert response.status_code == 404 and MSG_NOT_FOUND in response.get_data(as_text=True)
    assert pastIDPRow("Completed Kitchen")["status"] == "Active"


def test_ut28_8_page_notLoggedIn_redirectsToDesignerLogin():
    response = app.test_client().post("/designer/past-idps/1/delete", data={"choice": "delete"})
    assert response.status_code == 302 and "/designer/login" in response.headers["Location"]
