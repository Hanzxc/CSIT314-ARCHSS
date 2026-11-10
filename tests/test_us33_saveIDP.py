# Unit tests for US33 Save IDP.
# conftest.py gives each test a fresh database (cust001 / Cust@123 is the customer).
# Helpers come from the US37 tests and are shared with the US34 / US35 tests.

from app import app
from database.db import getConnection
from entity.savedIDP import SavedIDP
from control.saveIDPController import SaveIDPController
import boundary.idpDetailsPage as idpDetailsPage
from boundary.idpDetailsPage import MSG_SAVED, MSG_NOT_SAVED
from test_us37_viewIDPViewStatistics import (createDesigner, customerId, createCategory, addIDP, execute,
                                             countViews, loginAsDesigner)


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


def spyCreateSavedRecord(monkeypatch):
    # records each createSavedRecord call and what it returned
    calls = []
    original = SavedIDP.createSavedRecord
    def spy(self, customer, idpId):
        added = original(self, customer, idpId)
        calls.append(((customer, idpId), added))
        return added
    monkeypatch.setattr(SavedIDP, "createSavedRecord", spy)
    return calls


def flashes(client):
    with client.session_transaction() as state:
        return state.get("_flashes", [])


# ---------- SavedIDP.createSavedRecord() ----------

def test_ut33_1_createSavedRecord_addsOneRow():
    idpId = addIDP(createDesigner(), createCategory("Kitchen"), "Modern Kitchen")
    assert countSaved(customerId(), idpId) == 0
    assert SavedIDP().createSavedRecord(customerId(), idpId) is True
    assert countSaved(customerId(), idpId) == 1


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

def test_ut33_5_controller_returnsEntityResult(monkeypatch):
    idpId = addIDP(createDesigner(), createCategory("Kitchen"), "Modern Kitchen")
    calls = spyCreateSavedRecord(monkeypatch)
    assert SaveIDPController().saveIDP(customerId(), idpId) is True
    assert calls == [((customerId(), idpId), True)]          # one entity call, nothing else


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
    # US32 always shows the Save IDP button now (no "Saved" badge) - the saved record is what counts
    assert MSG_SAVED in html and ">Save IDP</button>" in html
    assert countSaved(customerId(), idpId) == 1


def test_ut33_8_page_alreadySaved_showsNotSavedNoDuplicate():
    idpId = addIDP(createDesigner(), createCategory("Kitchen"), "Modern Kitchen")
    client = loggedInCustomer()
    client.post(f"/customer/idps/{idpId}/save", follow_redirects=True)     # first save, message shown
    client.post(f"/customer/idps/{idpId}/save")
    assert flashes(client) == [("error", MSG_NOT_SAVED)]
    assert countSaved(customerId(), idpId) == 1


def test_ut33_9_page_unavailableIDP_showsNotSaved():
    idpId = addIDP(createDesigner(), createCategory("Kitchen"), "Deleted", status="Suspended")
    client = loggedInCustomer()
    response = client.post(f"/customer/idps/{idpId}/save")
    assert response.status_code == 302
    assert flashes(client) == [("error", MSG_NOT_SAVED)]
    assert countSaved(customerId(), idpId) == 0


def test_ut33_10_page_notLoggedIn_redirectsToCustomerLogin():
    response = app.test_client().post("/customer/idps/1/save")
    assert response.status_code == 302 and response.headers["Location"].endswith("/customer/login")


def test_ut33_11_controller_duplicate_falseStraightFromEntity(monkeypatch):
    idpId = addIDP(createDesigner(), createCategory("Kitchen"), "Modern Kitchen")
    calls = spyCreateSavedRecord(monkeypatch)
    controller = SaveIDPController()
    assert controller.saveIDP(customerId(), idpId) is True
    assert controller.saveIDP(customerId(), idpId) is False
    assert calls == [((customerId(), idpId), True), ((customerId(), idpId), False)]
    html = loggedInCustomer().post(f"/customer/idps/{idpId}/save", follow_redirects=True).get_data(as_text=True)
    assert MSG_NOT_SAVED in html


def test_ut33_12_page_bothOutcomes_redirectWithSaved1():
    idpId = addIDP(createDesigner(), createCategory("Kitchen"), "Modern Kitchen")
    client = loggedInCustomer()
    for _ in range(2):      # saved, then not saved
        response = client.post(f"/customer/idps/{idpId}/save")
        assert response.status_code == 302
        assert response.headers["Location"].endswith(f"/customer/idps/{idpId}?saved=1")


def test_ut33_13_page_redirectAfterSave_addsNoView():
    idpId = addIDP(createDesigner(), createCategory("Kitchen"), "Modern Kitchen")
    assert countViews(idpId) == 0
    response = loggedInCustomer().post(f"/customer/idps/{idpId}/save", follow_redirects=True)
    assert response.status_code == 200 and MSG_SAVED in response.get_data(as_text=True)
    assert countViews(idpId) == 0


def test_ut33_14_page_onlyCallsSaveIDP(monkeypatch):
    calls = []
    class StubController:       # only saveIDP - any other call would fail
        def saveIDP(self, customer, idpId):
            calls.append((customer, idpId))
            return True
    monkeypatch.setattr(idpDetailsPage, "SaveIDPController", StubController)
    assert loggedInCustomer().post("/customer/idps/7/save").status_code == 302
    assert calls == [(customerId(), 7)]
    assert not hasattr(SaveIDPController, "checkAlreadySaved")


# ---------- system tests (Flask test client) ----------

def test_tc33_3_saveSameIDPTwice_listedOnce():
    idpId = addIDP(createDesigner(), createCategory("Kitchen"), "Modern Kitchen")
    client = loggedInCustomer()
    client.post(f"/customer/idps/{idpId}/save", follow_redirects=True)
    html = client.post(f"/customer/idps/{idpId}/save", follow_redirects=True).get_data(as_text=True)
    assert "This IDP is already in your saved list or is no longer available" in html
    assert client.get("/customer/saved-list").get_data(as_text=True).count("<h2>Modern Kitchen</h2>") == 1


def test_tc33_4_idpNoLongerAvailable_nothingSaved():
    designer = createDesigner()
    deleted = addIDP(designer, createCategory("Kitchen"), "Deleted Kitchen")
    hidden = addIDP(designer, createCategory("Old Style"), "Hidden Loft")
    client = loggedInCustomer()
    for idpId in (deleted, hidden):
        assert client.get(f"/customer/idps/{idpId}").status_code == 200
    # meanwhile the designer deletes one (US23) and the other's category is suspended (US44)
    execute("UPDATE idp SET status = 'Suspended' WHERE idpId = ?", (deleted,))
    execute("UPDATE idp_category SET status = 'Suspended' WHERE categoryName = 'Old Style'")
    for idpId in (deleted, hidden):
        html = client.post(f"/customer/idps/{idpId}/save", follow_redirects=True).get_data(as_text=True)
        assert "This IDP is already in your saved list or is no longer available" in html
        assert countSaved(customerId(), idpId) == 0


def test_tc33_5_backOnIDPPage_saveButtonStillShown():
    idpId = addIDP(createDesigner(), createCategory("Kitchen"), "Modern Kitchen")
    response = loggedInCustomer().post(f"/customer/idps/{idpId}/save", follow_redirects=True)
    html = response.get_data(as_text=True)
    assert response.request.full_path == f"/customer/idps/{idpId}?saved=1"
    assert "IDP saved to your saved list" in html and ">Save IDP</button>" in html


def test_tc33_6_saveDoesNotCountAView():
    idpId = addIDP(createDesigner(), createCategory("Kitchen"), "Modern Kitchen")
    designer = app.test_client()
    loginAsDesigner(designer)
    customer = loggedInCustomer()
    customer.get(f"/customer/idps/{idpId}")
    assert "<strong>1</strong>" in designer.get("/designer/idps/statistics/views").get_data(as_text=True)
    customer.post(f"/customer/idps/{idpId}/save", follow_redirects=True)
    assert "<strong>1</strong>" in designer.get("/designer/idps/statistics/views").get_data(as_text=True)
