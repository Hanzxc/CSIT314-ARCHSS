# Unit tests for US33 Save IDP.
# conftest.py gives each test a fresh database (cust001 / Cust@123 is the customer).
# Helpers come from the US37 tests and are shared with the US34 / US35 tests.

from app import app
from database.db import getConnection
from entity.savedIDP import SavedIDP
from control.saveIDPController import SaveIDPController
from boundary.idpDetailsPage import MSG_SAVED, MSG_ALREADY_SAVED, MSG_UNAVAILABLE
from test_us37_viewIDPViewStatistics import createDesigner, customerId, createCategory, addIDP


def loggedInCustomer():
    client = app.test_client()
    client.post("/customer/login", data={"username": "cust001", "password": "Cust@123"})
    return client


def countSaved(customer, idpId):
    conn = getConnection()
    total = conn.execute("SELECT COUNT(*) FROM saved_idp WHERE customerId = ? AND idpId = ?",
                         (customer, idpId)).fetchone()[0]
    conn.close()
    return total


# ---------- SavedIDP.exists() / createSavedRecord() ----------

def test_ut33_1_createSavedRecord_thenExists():
    idpId = addIDP(createDesigner(), createCategory("Kitchen"), "Modern Kitchen")
    assert SavedIDP().exists(customerId(), idpId) is False
    assert SavedIDP().createSavedRecord(customerId(), idpId) is True
    assert SavedIDP().exists(customerId(), idpId) is True


def test_ut33_2_createSavedRecord_noDuplicate():
    idpId = addIDP(createDesigner(), createCategory("Kitchen"), "Modern Kitchen")
    SavedIDP().createSavedRecord(customerId(), idpId)
    assert SavedIDP().createSavedRecord(customerId(), idpId) is False
    assert countSaved(customerId(), idpId) == 1


def test_ut33_3_createSavedRecord_hiddenOrMissingIDP_refused():
    designer = createDesigner()
    deleted = addIDP(designer, createCategory("Kitchen"), "Deleted", status="Suspended")
    hidden = addIDP(designer, createCategory("Old Style", "Suspended"), "Hidden")
    for idpId in (deleted, hidden, 999999):
        assert SavedIDP().createSavedRecord(customerId(), idpId) is False
        assert countSaved(customerId(), idpId) == 0


def test_ut33_4_pastIDPsCanBeSavedToo():
    idpId = addIDP(createDesigner(), createCategory("Kitchen"), "Completed Kitchen", "Past")
    assert SavedIDP().createSavedRecord(customerId(), idpId) is True


# ---------- SaveIDPController ----------

def test_ut33_5_controller_passesThrough():
    idpId = addIDP(createDesigner(), createCategory("Kitchen"), "Modern Kitchen")
    controller = SaveIDPController()
    assert controller.checkAlreadySaved(customerId(), idpId) is False
    assert controller.saveIDP(customerId(), idpId) is True
    assert controller.checkAlreadySaved(customerId(), idpId) is True


# ---------- IDPDetailsPage through the Flask route (the Save button on the US32 page) ----------

def test_ut33_6_page_detailsShowSaveButton():
    idpId = addIDP(createDesigner(), createCategory("Kitchen"), "Modern Kitchen")
    html = loggedInCustomer().get(f"/customer/idps/{idpId}").get_data(as_text=True)
    assert f'action="/customer/idps/{idpId}/save"' in html and ">Save IDP</button>" in html


def test_ut33_7_page_clickSave_savesAndShowsSavedState():
    idpId = addIDP(createDesigner(), createCategory("Kitchen"), "Modern Kitchen")
    client = loggedInCustomer()
    response = client.post(f"/customer/idps/{idpId}/save", follow_redirects=True)
    html = response.get_data(as_text=True)
    assert MSG_SAVED in html and "Saved</span>" in html and ">Save IDP</button>" not in html
    assert countSaved(customerId(), idpId) == 1


def test_ut33_8_page_alreadySaved_showsMessageNoDuplicate():
    idpId = addIDP(createDesigner(), createCategory("Kitchen"), "Modern Kitchen")
    client = loggedInCustomer()
    client.post(f"/customer/idps/{idpId}/save")
    html = client.post(f"/customer/idps/{idpId}/save", follow_redirects=True).get_data(as_text=True)
    assert MSG_ALREADY_SAVED in html
    assert countSaved(customerId(), idpId) == 1


def test_ut33_9_page_unavailableIDP_showsError():
    idpId = addIDP(createDesigner(), createCategory("Kitchen"), "Deleted", status="Suspended")
    response = loggedInCustomer().post(f"/customer/idps/{idpId}/save")
    assert response.status_code == 302
    with loggedInCustomer() as client:
        client.post(f"/customer/idps/{idpId}/save")
        with client.session_transaction() as state:
            assert (("error", MSG_UNAVAILABLE) in state.get("_flashes", []))


def test_ut33_10_page_notLoggedIn_redirectsToCustomerLogin():
    response = app.test_client().post("/customer/idps/1/save")
    assert response.status_code == 302 and response.headers["Location"].endswith("/customer/login")
