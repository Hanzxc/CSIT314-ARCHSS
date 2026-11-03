# Unit tests for US17 Delete company profile.
# conftest.py creates a fresh database for every test.
# Designer tests add designer13 / Design@123 (Tengku Uda Designer, profile 2).

from app import app
from database.db import getConnection
from entity.userAccount import UserAccount
from entity.companyProfile import CompanyProfile
from control.deleteCompanyProfileController import DeleteCompanyProfileController
from control.interiorDesignerLoginController import InteriorDesignerLoginController


def companyData():
    return {"companyName": "Uda Interiors", "description": "Interior design for homes.",
            "services": "Space planning, renovation", "email": "hello@udainteriors.com",
            "phone": "+65 6123 4567", "address": "10 Design Street"}


def makeCompany(designerId, data):
    # the entity takes a CompanyProfile object now, not a dict
    return CompanyProfile(designerId=designerId, **data)


def createDesigner13():
    UserAccount().createUserAccount(
        "designer13", "Design@123", "Tengku Uda Designer", "designer13@archss.com", "", 2)
    return UserAccount().verifyCredentials("designer13", "Design@123").userId


def createCompanyForDesigner13():
    userId = createDesigner13()
    CompanyProfile().createCompanyProfile(makeCompany(userId, companyData()))
    return userId


def countCompanies():
    conn = getConnection()
    total = conn.execute("SELECT COUNT(*) FROM company_profile").fetchone()[0]
    conn.close()
    return total


def loginAsDesigner13(client):
    return client.post("/designer/login", data={"username": "designer13", "password": "Design@123"})


def openDeleteConfirmation(client):
    client.get("/designer/company/delete")
    with client.session_transaction() as session:
        confirmation = dict(session["companyDeleteConfirmation"])
    return {"choice": "delete", "companyId": str(confirmation["companyId"]),
            "confirmationToken": confirmation["token"]}


# ---------- DeleteCompanyProfileController.deleteCompanyProfile() ----------

def test_ut17_1_deleteCompanyProfile_valid():
    userId = createCompanyForDesigner13()
    companyId = CompanyProfile().getCompanyProfile(userId).companyId
    assert DeleteCompanyProfileController().deleteCompanyProfile(userId, companyId) is True
    assert CompanyProfile().getCompanyProfile(userId) is None
    assert countCompanies() == 1


def test_ut17_2_deleteCompanyProfile_missing():
    userId = createDesigner13()
    assert DeleteCompanyProfileController().deleteCompanyProfile(userId, 9999) is False


def test_ut17_4_deleteCompanyProfile_wrongCompanyId():
    userId = createCompanyForDesigner13()
    assert DeleteCompanyProfileController().deleteCompanyProfile(userId, 9999) is False
    assert countCompanies() == 1


def test_ut17_6_deleteCompanyProfile_keepsAccount():
    userId = createCompanyForDesigner13()
    companyId = CompanyProfile().getCompanyProfile(userId).companyId
    DeleteCompanyProfileController().deleteCompanyProfile(userId, companyId)
    account = UserAccount().getUserAccount(userId)
    assert account.username == "designer13"
    assert account.status == "Active"
    assert InteriorDesignerLoginController().login("designer13", "Design@123") is not None


# ---------- CompanyProfile.suspendCompanyProfile() ----------

def test_ut17_7_entity_suspendsOnlyMatchingOwner():
    userId = createCompanyForDesigner13()
    UserAccount().createUserAccount("designer17", "Design@123", "Daniel Tan", "", "", 2)
    otherId = UserAccount().verifyCredentials("designer17", "Design@123").userId
    CompanyProfile().createCompanyProfile(makeCompany(otherId, companyData()))
    companyId = CompanyProfile().getCompanyProfile(userId).companyId
    assert CompanyProfile().suspendCompanyProfile(otherId, companyId) is False
    assert CompanyProfile().suspendCompanyProfile(userId, companyId) is True
    assert CompanyProfile().getCompanyProfile(otherId) is not None
    assert countCompanies() == 2


def test_ut17_8_entity_repeatedDeleteReturnsFalse():
    userId = createCompanyForDesigner13()
    companyId = CompanyProfile().getCompanyProfile(userId).companyId
    assert CompanyProfile().suspendCompanyProfile(userId, companyId) is True
    assert CompanyProfile().suspendCompanyProfile(userId, companyId) is False


def test_ut17_9_entity_oldRevisionCannotSuspendRestoredProfile():
    # create doesn't bring a deleted one back any more (it's a duplicate), restore does
    userId = createCompanyForDesigner13()
    original = CompanyProfile().getCompanyProfile(userId)
    assert CompanyProfile().suspendCompanyProfile(userId, original.companyId, original.revision) is True
    assert CompanyProfile().createCompanyProfile(makeCompany(userId, companyData())) is False
    assert CompanyProfile().restoreCompanyProfile(userId, original.companyId, original.revision) is True
    replacement = CompanyProfile().getCompanyProfile(userId)
    assert replacement.companyId == original.companyId
    assert replacement.revision == original.revision + 1
    assert CompanyProfile().suspendCompanyProfile(userId, original.companyId, original.revision) is False
    assert CompanyProfile().getCompanyProfile(userId).status == "Active"


# ---------- whole page, through the browser (test client) ----------

def test_ut17_10_viewPage_showsDeleteLink():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    assert b'href="/designer/company/delete"' in client.get("/designer/company").data


def test_ut17_11_deletePage_confirmationDoesNotDelete():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company/delete")
    assert response.status_code == 200
    assert b"Are you sure" in response.data
    assert b"Uda Interiors" in response.data
    assert b'name="confirmationToken"' in response.data
    assert countCompanies() == 1


def test_ut17_12_deletePage_success():
    userId = createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = openDeleteConfirmation(client)
    response = client.post("/designer/company/delete", data=data, follow_redirects=True)
    assert b"Company profile deleted successfully" in response.data
    assert b'action="/designer/company/restore"' in response.data
    assert CompanyProfile().getCompanyProfile(userId) is None


def test_ut17_13_deletePage_cancel():
    userId = createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    openDeleteConfirmation(client)
    response = client.post("/designer/company/delete", data={"choice": "cancel"})
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/designer/company")
    assert CompanyProfile().getCompanyProfile(userId) is not None
    with client.session_transaction() as session:
        assert "companyDeleteConfirmation" not in session


def test_ut17_14_deletePage_notLoggedIn():
    client = app.test_client()
    response = client.get("/designer/company/delete")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/designer/login")
    assert client.post("/designer/company/delete", data={"choice": "delete"}).status_code == 302


def test_ut17_16_deletePage_noProfile():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company/delete")
    assert response.status_code == 404
    assert b"You have not created a company profile yet" in response.data


def test_ut17_17_deletePage_directPostWithoutConfirmationRejected():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.post("/designer/company/delete", data={"choice": "delete", "companyId": "1"})
    assert response.status_code == 400
    assert countCompanies() == 1


def test_ut17_18_deletePage_wrongTokenRejected():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = openDeleteConfirmation(client)
    data["confirmationToken"] = "wrong-token"
    assert client.post("/designer/company/delete", data=data).status_code == 400
    assert countCompanies() == 1


def test_ut17_19_deletePage_forgedCompanyIdRejected():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = openDeleteConfirmation(client)
    data["companyId"] = "9999"
    assert client.post("/designer/company/delete", data=data).status_code == 400
    assert countCompanies() == 1


def test_ut17_20_deletePage_ignoresForgedOwner():
    userId = createCompanyForDesigner13()
    UserAccount().createUserAccount("designer17", "Design@123", "Daniel Tan", "", "", 2)
    otherId = UserAccount().verifyCredentials("designer17", "Design@123").userId
    CompanyProfile().createCompanyProfile(makeCompany(otherId, companyData()))
    client = app.test_client()
    loginAsDesigner13(client)
    data = openDeleteConfirmation(client)
    data["designerId"] = str(otherId)
    client.post("/designer/company/delete?designerId=" + str(otherId), data=data)
    assert CompanyProfile().getCompanyProfile(userId) is None
    assert CompanyProfile().getCompanyProfile(otherId) is not None


def test_ut17_22_deletePage_keepsLoginSession():
    userId = createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = openDeleteConfirmation(client)
    client.post("/designer/company/delete", data=data)
    with client.session_transaction() as session:
        assert session["userId"] == userId
        assert "companyDeleteConfirmation" not in session
    assert client.get("/designer/dashboard").status_code == 200


def test_ut17_23_deletedProfile_cannotBeViewedOrUpdated():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    client.post("/designer/company/delete", data=openDeleteConfirmation(client))
    assert client.get("/designer/company").status_code == 404
    assert client.get("/designer/company/update").status_code == 404


def test_ut17_24_deletePage_confirmationCannotBeReused():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = openDeleteConfirmation(client)
    client.post("/designer/company/delete", data=data)
    assert client.post("/designer/company/delete", data=data).status_code == 400


def test_ut17_25_deletePage_staleConfirmationKeepsRestoredProfile():
    # deleted + restored in between -> revision went up, so the old confirmation is useless
    userId = createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = openDeleteConfirmation(client)
    CompanyProfile().suspendCompanyProfile(userId, int(data["companyId"]))
    suspended = CompanyProfile().getSuspendedCompanyProfile(userId)
    CompanyProfile().restoreCompanyProfile(userId, suspended.companyId, suspended.revision)
    replacementId = CompanyProfile().getCompanyProfile(userId).companyId
    response = client.post("/designer/company/delete", data=data)
    assert response.status_code == 400
    assert CompanyProfile().getCompanyProfile(userId).companyId == replacementId


def test_ut17_26_deletePage_unknownChoiceDoesNotDelete():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = openDeleteConfirmation(client)
    data["choice"] = "unknown"
    assert client.post("/designer/company/delete", data=data).status_code == 400
    assert countCompanies() == 1


def test_ut17_27_deletePage_escapesCompanyName():
    userId = createDesigner13()
    data = companyData()
    data["companyName"] = "<script>alert(1)</script>"
    CompanyProfile().createCompanyProfile(makeCompany(userId, data))
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company/delete")
    assert b"<script>alert(1)</script>" not in response.data
    assert b"&lt;script&gt;" in response.data


def test_ut17_28_createViewUpdateDelete_endToEnd():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    client.post("/designer/company/create", data=companyData())
    data = companyData()
    data["companyName"] = "Uda Interiors Studio"
    client.post("/designer/company/update", data=data)
    assert b"Uda Interiors Studio" in client.get("/designer/company").data
    client.post("/designer/company/delete", data=openDeleteConfirmation(client))
    assert countCompanies() == 1
    assert client.get("/designer/company").status_code == 404
    assert b'action="/designer/company/restore"' in client.get("/designer/dashboard").data


def test_ut17_29_suspend_keepsAllBusinessData():
    userId = createCompanyForDesigner13()
    conn = getConnection()
    before = dict(conn.execute("SELECT * FROM company_profile WHERE designerId=?", (userId,)).fetchone())
    conn.close()
    assert DeleteCompanyProfileController().deleteCompanyProfile(userId, before["companyId"]) is True
    conn = getConnection()
    after = dict(conn.execute("SELECT * FROM company_profile WHERE designerId=?", (userId,)).fetchone())
    conn.close()
    assert after["status"] == "Suspended"
    before["status"] = "Suspended"
    assert after == before


def test_ut17_30_suspend_filtersViewUpdateSearchAndOffersCreate():
    userId = createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    client.post("/designer/company/delete", data=openDeleteConfirmation(client))
    assert client.get("/designer/company").status_code == 404
    assert client.get("/designer/company/update").status_code == 404
    assert client.post("/designer/company/update", data=companyData()).status_code == 404
    assert client.get("/designer/company/search?keyword=Uda").status_code == 404
    assert CompanyProfile().updateCompanyProfile(makeCompany(userId, companyData())) is False
    assert CompanyProfile().searchCompanyInformation(userId, "") == []
    assert b'action="/designer/company/restore"' in client.get("/designer/dashboard").data
    assert client.get("/designer/company/create").status_code == 200
    # but saving the form doesn't make a second one - the deleted row still counts as a duplicate
    assert b"You already have a company profile" in client.post("/designer/company/create", data=companyData()).data
    assert countCompanies() == 1
