# Unit tests for US17 Delete company profile.
# conftest.py creates a fresh database for every test.
# Designer tests add designer13 / Design@123 (Tengku Uda Designer, profile 2).
# the confirmation box posts hidden companyId + revision - no token, nothing kept in the session

import re

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
        UserAccount(username="designer13", password="Design@123", fullName="Tengku Uda Designer", email="designer13@archss.com", phone="", profileId=2))
    return UserAccount().verifyCredentials("designer13", "Design@123").userId


def createDesigner17():
    UserAccount().createUserAccount(UserAccount(username="designer17", password="Design@123", fullName="Daniel Tan", email="", phone="", profileId=2))
    return UserAccount().verifyCredentials("designer17", "Design@123").userId


def createCompanyForDesigner13():
    userId = createDesigner13()
    CompanyProfile().createCompanyProfile(makeCompany(userId, companyData()))
    return userId


def countCompanies():
    conn = getConnection()
    total = conn.execute("SELECT COUNT(*) FROM company_profile").fetchone()[0]
    conn.close()
    return total


def readCompanyRow(userId):
    conn = getConnection()
    row = conn.execute("SELECT * FROM company_profile WHERE designerId=?", (userId,)).fetchone()
    conn.close()
    return dict(row) if row else None


def loginAsDesigner13(client):
    return client.post("/designer/login", data={"username": "designer13", "password": "Design@123"})


def openDeleteConfirmation(client):
    # opens the box and reads its hidden fields, like the browser would send them
    response = client.get("/designer/company/delete")
    companyId = re.search(rb'name="companyId" value="([^"]*)"', response.data).group(1).decode()
    revision = re.search(rb'name="revision" value="([^"]*)"', response.data).group(1).decode()
    return {"choice": "delete", "companyId": companyId, "revision": revision}


# ---------- DeleteCompanyProfileController.deleteCompanyProfile() ----------

def test_ut17_1_deleteCompanyProfile_valid():
    userId = createCompanyForDesigner13()
    profile = CompanyProfile().getCompanyProfile(userId)
    assert DeleteCompanyProfileController().deleteCompanyProfile(userId, profile.companyId, profile.revision) is True
    assert CompanyProfile().getCompanyProfile(userId) is None
    assert readCompanyRow(userId)["status"] == "Suspended"
    assert countCompanies() == 1


def test_ut17_2_deleteCompanyProfile_missing():
    userId = createDesigner13()
    assert DeleteCompanyProfileController().deleteCompanyProfile(userId, 9999, 1) is False


def test_ut17_4_deleteCompanyProfile_wrongCompanyId():
    userId = createCompanyForDesigner13()
    assert DeleteCompanyProfileController().deleteCompanyProfile(userId, 9999, 1) is False
    assert CompanyProfile().getCompanyProfile(userId) is not None
    assert countCompanies() == 1


def test_ut17_6_deleteCompanyProfile_keepsAccount():
    userId = createCompanyForDesigner13()
    profile = CompanyProfile().getCompanyProfile(userId)
    DeleteCompanyProfileController().deleteCompanyProfile(userId, profile.companyId, profile.revision)
    account = UserAccount().getUserAccount(userId)
    assert account.username == "designer13"
    assert account.status == "Active"
    assert InteriorDesignerLoginController().login("designer13", "Design@123") is not None


# ---------- CompanyProfile.suspendCompanyProfile() ----------

def test_ut17_7_entity_suspendsOnlyMatchingOwner():
    userId = createCompanyForDesigner13()
    otherId = createDesigner17()
    CompanyProfile().createCompanyProfile(makeCompany(otherId, companyData()))
    profile = CompanyProfile().getCompanyProfile(userId)
    assert CompanyProfile().suspendCompanyProfile(otherId, profile.companyId, profile.revision) is False
    assert CompanyProfile().suspendCompanyProfile(userId, profile.companyId, profile.revision) is True
    assert CompanyProfile().getCompanyProfile(otherId) is not None
    assert countCompanies() == 2


def test_ut17_8_entity_repeatedDeleteReturnsFalse():
    userId = createCompanyForDesigner13()
    profile = CompanyProfile().getCompanyProfile(userId)
    assert CompanyProfile().suspendCompanyProfile(userId, profile.companyId, profile.revision) is True
    assert CompanyProfile().suspendCompanyProfile(userId, profile.companyId, profile.revision) is False


def test_ut17_9_entity_oldRevisionCannotSuspendRestoredProfile():
    # create doesn't bring a deleted one back (it's a duplicate), restore does - and the revision goes up
    userId = createCompanyForDesigner13()
    original = CompanyProfile().getCompanyProfile(userId)
    assert CompanyProfile().suspendCompanyProfile(userId, original.companyId, original.revision) is True
    assert CompanyProfile().createCompanyProfile(makeCompany(userId, companyData())) is False
    assert CompanyProfile().restoreCompanyProfile(userId, original.companyId, original.revision) is True
    restored = CompanyProfile().getCompanyProfile(userId)
    assert restored.companyId == original.companyId
    assert restored.revision == original.revision + 1
    assert CompanyProfile().suspendCompanyProfile(userId, original.companyId, original.revision) is False
    assert CompanyProfile().getCompanyProfile(userId).status == "Active"


# ---------- whole page, through the browser (test client) ----------

def test_ut17_10_viewPage_showsDeleteLink():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    assert b'href="/designer/company/delete"' in client.get("/designer/company").data


def test_ut17_11_deletePage_confirmationDoesNotDelete():
    userId = createCompanyForDesigner13()
    profile = CompanyProfile().getCompanyProfile(userId)
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company/delete")
    assert response.status_code == 200
    assert b"Are you sure" in response.data
    assert b"Uda Interiors" in response.data
    assert ('name="companyId" value="' + str(profile.companyId) + '"').encode() in response.data
    assert ('name="revision" value="' + str(profile.revision) + '"').encode() in response.data
    assert b"confirmationToken" not in response.data
    assert countCompanies() == 1
    assert CompanyProfile().getCompanyProfile(userId) is not None


def test_ut17_12_deletePage_success():
    userId = createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = openDeleteConfirmation(client)
    response = client.post("/designer/company/delete", data=data, follow_redirects=True)
    assert b"Company profile deleted successfully" in response.data
    assert b'action="/designer/company/restore"' in response.data
    assert CompanyProfile().getCompanyProfile(userId) is None
    assert readCompanyRow(userId)["status"] == "Suspended"


def test_ut17_13_deletePage_cancel():
    userId = createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = openDeleteConfirmation(client)
    data["choice"] = "cancel"
    response = client.post("/designer/company/delete", data=data)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/designer/company")
    assert CompanyProfile().getCompanyProfile(userId) is not None
    with client.session_transaction() as session:
        assert set(session.keys()) == {"userId", "profileId", "username"}


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


def test_ut17_17_deletePage_noRevisionRejected():
    userId = createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    companyId = CompanyProfile().getCompanyProfile(userId).companyId
    response = client.post("/designer/company/delete", data={"choice": "delete", "companyId": str(companyId)})
    assert response.status_code == 400
    assert b"Company profile could not be deleted. Please reopen the confirmation" in response.data
    assert CompanyProfile().getCompanyProfile(userId) is not None


def test_ut17_18_deletePage_wrongRevisionRejected():
    userId = createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = openDeleteConfirmation(client)
    data["revision"] = str(int(data["revision"]) + 1)
    assert client.post("/designer/company/delete", data=data).status_code == 400
    assert CompanyProfile().getCompanyProfile(userId) is not None


def test_ut17_19_deletePage_changedCompanyIdRejected():
    userId = createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = openDeleteConfirmation(client)
    data["companyId"] = "9999"
    assert client.post("/designer/company/delete", data=data).status_code == 400
    assert CompanyProfile().getCompanyProfile(userId) is not None
    assert countCompanies() == 1


def test_ut17_20_deletePage_ignoresForgedOwner():
    userId = createCompanyForDesigner13()
    otherId = createDesigner17()
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
        assert set(session.keys()) <= {"userId", "profileId", "username", "_flashes"}
    assert client.get("/designer/dashboard").status_code == 200


def test_ut17_23_deletedProfile_cannotBeViewedOrUpdated():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    client.post("/designer/company/delete", data=openDeleteConfirmation(client))
    assert client.get("/designer/company").status_code == 404
    assert client.get("/designer/company/update").status_code == 404


def test_ut17_24_deletePage_sameFormTwice():
    userId = createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = openDeleteConfirmation(client)
    assert client.post("/designer/company/delete", data=data).status_code == 302
    # the row isn't Active any more, so the entity finds nothing to suspend
    assert client.post("/designer/company/delete", data=data).status_code == 400
    assert readCompanyRow(userId)["status"] == "Suspended"


def test_ut17_25_deletePage_oldFormKeepsRestoredProfile():
    # deleted + restored in between -> revision went up, so the old form matches no row
    userId = createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = openDeleteConfirmation(client)
    profile = CompanyProfile().getCompanyProfile(userId)
    CompanyProfile().suspendCompanyProfile(userId, profile.companyId, profile.revision)
    CompanyProfile().restoreCompanyProfile(userId, profile.companyId, profile.revision)
    response = client.post("/designer/company/delete", data=data)
    assert response.status_code == 400
    assert CompanyProfile().getCompanyProfile(userId).status == "Active"


def test_ut17_26_deletePage_unknownChoiceDoesNotDelete():
    userId = createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = openDeleteConfirmation(client)
    data["choice"] = "unknown"
    response = client.post("/designer/company/delete", data=data)
    assert response.status_code == 400
    assert b"Please open the delete confirmation and try again" in response.data
    assert CompanyProfile().getCompanyProfile(userId) is not None


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
    userId = createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    client.post("/designer/company/create", data=companyData())
    data = companyData()
    data["companyName"] = "Uda Interiors Studio"
    client.post("/designer/company/update", data=data)
    assert b"Uda Interiors Studio" in client.get("/designer/company").data
    client.post("/designer/company/delete", data=openDeleteConfirmation(client))
    assert countCompanies() == 1
    assert readCompanyRow(userId)["status"] == "Suspended"
    assert client.get("/designer/company").status_code == 404
    assert b'action="/designer/company/restore"' in client.get("/designer/dashboard").data


def test_ut17_29_suspend_keepsAllBusinessData():
    userId = createCompanyForDesigner13()
    before = readCompanyRow(userId)
    assert DeleteCompanyProfileController().deleteCompanyProfile(userId, before["companyId"], before["revision"]) is True
    after = readCompanyRow(userId)
    assert after["status"] == "Suspended"
    before["status"] = "Suspended"
    assert after == before


def test_ut17_30_suspend_hidesViewUpdateAndSearch():
    userId = createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    client.post("/designer/company/delete", data=openDeleteConfirmation(client))
    assert client.get("/designer/company").status_code == 404
    assert client.get("/designer/company/update").status_code == 404
    assert client.post("/designer/company/update", data=companyData()).status_code == 404
    assert client.get("/designer/company/search?keyword=Uda").status_code == 404
    assert CompanyProfile().updateCompanyProfile(makeCompany(userId, companyData())) is False
    assert CompanyProfile().searchCompanyInformation(userId, "") is None
    assert b'action="/designer/company/restore"' in client.get("/designer/dashboard").data


# ---------- system tests (TC) ----------

def test_tc17_6_oldDeleteFormSentAgain():
    userId = createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = openDeleteConfirmation(client)
    client.post("/designer/company/delete", data=data)
    before = readCompanyRow(userId)
    response = client.post("/designer/company/delete", data=data)
    assert response.status_code == 400
    assert b"Company profile could not be deleted. Please reopen the confirmation" in response.data
    assert readCompanyRow(userId) == before
