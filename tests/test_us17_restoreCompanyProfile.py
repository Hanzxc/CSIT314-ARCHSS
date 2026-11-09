# Unit tests for US17 Restore company profile (UC17-R).
# Existing conftest.py supplies a fresh database for each test.
# designer13 / Design@123; the dashboard's Restore button posts hidden companyId + revision.

import re

from app import app
from database.db import getConnection
from entity.userAccount import UserAccount
from entity.companyProfile import CompanyProfile
from control.restoreCompanyProfileController import RestoreCompanyProfileController


def companyData():
    return {"companyName": "Modena", "description": "Interior design for homes.",
            "services": "Space planning, renovation", "email": "hello@modena.com",
            "phone": "+65 6123 4567", "address": "10 Design Street"}


def createSuspendedCompany():
    UserAccount().createUserAccount(UserAccount(username="designer13", password="Design@123", fullName="Tengku Uda Designer", email="", phone="", profileId=2))
    userId = UserAccount().verifyCredentials("designer13", "Design@123").userId
    assert CompanyProfile().createCompanyProfile(CompanyProfile(designerId=userId, **companyData())) is True
    profile = CompanyProfile().getCompanyProfile(userId)
    assert CompanyProfile().suspendCompanyProfile(userId, profile.companyId, profile.revision) is True
    return userId


def readCompanyRow(userId):
    conn = getConnection()
    row = conn.execute("SELECT * FROM company_profile WHERE designerId=?", (userId,)).fetchone()
    conn.close()
    return dict(row) if row else None


def loginAsDesigner13(client):
    return client.post("/designer/login", data={"username": "designer13", "password": "Design@123"})


def restoreData(client):
    # reads the hidden fields of the dashboard's Restore form, like the browser would send them
    response = client.get("/designer/dashboard")
    companyId = re.search(rb'name="companyId" value="([^"]*)"', response.data).group(1).decode()
    revision = re.search(rb'name="revision" value="([^"]*)"', response.data).group(1).decode()
    return {"companyId": companyId, "revision": revision}


def deleteData(client):
    # same for the delete confirmation box (US17)
    response = client.get("/designer/company/delete")
    companyId = re.search(rb'name="companyId" value="([^"]*)"', response.data).group(1).decode()
    revision = re.search(rb'name="revision" value="([^"]*)"', response.data).group(1).decode()
    return {"choice": "delete", "companyId": companyId, "revision": revision}


# ---------- CompanyProfile.restoreCompanyProfile() ----------

def test_ut17r_1_entity_restoresAllSavedDetails():
    userId = createSuspendedCompany()
    before = readCompanyRow(userId)
    assert CompanyProfile().restoreCompanyProfile(userId, before["companyId"], before["revision"]) is True
    after = readCompanyRow(userId)
    expected = dict(before, status="Active", revision=before["revision"] + 1)
    assert after == expected


def test_ut17r_2_entity_repeatedRestoreReturnsFalse():
    userId = createSuspendedCompany()
    profile = CompanyProfile().getSuspendedCompanyProfile(userId)
    assert CompanyProfile().restoreCompanyProfile(userId, profile.companyId, profile.revision) is True
    assert CompanyProfile().restoreCompanyProfile(userId, profile.companyId, profile.revision) is False
    conn = getConnection()
    assert conn.execute("SELECT COUNT(*) FROM company_profile").fetchone()[0] == 1
    conn.close()


def test_ut17r_3_entity_wrongOwnerRejected():
    userId = createSuspendedCompany()
    profile = CompanyProfile().getSuspendedCompanyProfile(userId)
    assert CompanyProfile().restoreCompanyProfile(1, profile.companyId, profile.revision) is False
    assert readCompanyRow(userId)["status"] == "Suspended"


def test_ut17r_4_entity_wrongCompanyRejected():
    userId = createSuspendedCompany()
    assert CompanyProfile().restoreCompanyProfile(userId, 9999, 1) is False


def test_ut17r_5_entity_wrongRevisionRejected():
    userId = createSuspendedCompany()
    profile = CompanyProfile().getSuspendedCompanyProfile(userId)
    assert CompanyProfile().restoreCompanyProfile(userId, profile.companyId, profile.revision + 1) is False


# ---------- RestoreCompanyProfileController ----------

def test_ut17r_6_controller_restoreValid():
    userId = createSuspendedCompany()
    control = RestoreCompanyProfileController()
    profile = control.getSuspendedCompanyProfile(userId)
    assert control.restoreCompanyProfile(userId, profile.companyId, profile.revision) is True
    assert control.getSuspendedCompanyProfile(userId) is None


def test_ut17r_9_controller_missingAccountRejected():
    assert RestoreCompanyProfileController().getSuspendedCompanyProfile(9999) is None
    assert RestoreCompanyProfileController().restoreCompanyProfile(9999, 1, 1) is False


# ---------- whole page, through Flask's test client ----------

def test_ut17r_10_dashboard_showsOwnRestoreButton():
    userId = createSuspendedCompany()
    profile = CompanyProfile().getSuspendedCompanyProfile(userId)
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/dashboard")
    assert b"Suspended" in response.data
    assert b"Restore company profile" in response.data
    assert b'action="/designer/company/restore"' in response.data
    assert ('name="companyId" value="' + str(profile.companyId) + '"').encode() in response.data
    assert ('name="revision" value="' + str(profile.revision) + '"').encode() in response.data
    assert b"Modena" not in response.data
    assert b"hello@modena.com" not in response.data
    assert readCompanyRow(userId)["status"] == "Suspended"


def test_ut17r_11_restorePage_success():
    userId = createSuspendedCompany()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.post("/designer/company/restore", data=restoreData(client), follow_redirects=True)
    assert response.status_code == 200
    assert b"Company profile restored successfully" in response.data
    assert b"Modena" in response.data
    assert b"hello@modena.com" in response.data
    assert b"Active" in response.data
    assert readCompanyRow(userId)["status"] == "Active"
    assert b"Restore company profile" not in client.get("/designer/dashboard").data
    assert b'href="/designer/company"' in client.get("/designer/dashboard").data


def test_ut17r_12_restorePage_notLoggedIn():
    userId = createSuspendedCompany()
    profile = CompanyProfile().getSuspendedCompanyProfile(userId)
    response = app.test_client().post("/designer/company/restore",
                                      data={"companyId": profile.companyId, "revision": profile.revision})
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/designer/login")
    assert readCompanyRow(userId)["status"] == "Suspended"


def test_ut17r_13_restorePage_getNotAllowed():
    userId = createSuspendedCompany()
    client = app.test_client()
    loginAsDesigner13(client)
    assert client.get("/designer/company/restore").status_code == 405
    assert readCompanyRow(userId)["status"] == "Suspended"


def test_ut17r_15_restorePage_missingFieldsRejected():
    # no companyId or revision -> the entity matches no row
    userId = createSuspendedCompany()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.post("/designer/company/restore", follow_redirects=True)
    assert b"Company profile could not be restored. Please reopen the dashboard and try again" in response.data
    assert b"Restore company profile" in response.data
    assert readCompanyRow(userId)["status"] == "Suspended"


def test_ut17r_16_restorePage_wrongRevisionRejected():
    userId = createSuspendedCompany()
    client = app.test_client()
    loginAsDesigner13(client)
    data = restoreData(client)
    data["revision"] = str(int(data["revision"]) + 1)
    response = client.post("/designer/company/restore", data=data, follow_redirects=True)
    assert b"Company profile could not be restored" in response.data
    assert readCompanyRow(userId)["status"] == "Suspended"


def test_ut17r_17_restorePage_sameFormTwiceDoesNotChangeData():
    userId = createSuspendedCompany()
    client = app.test_client()
    loginAsDesigner13(client)
    data = restoreData(client)
    client.post("/designer/company/restore", data=data)
    before = readCompanyRow(userId)
    response = client.post("/designer/company/restore", data=data, follow_redirects=True)
    assert b"Company profile could not be restored" in response.data
    assert readCompanyRow(userId) == before


def test_ut17r_18_restorePage_ignoresForgedOwnerAndBusinessDetails():
    userId = createSuspendedCompany()
    client = app.test_client()
    loginAsDesigner13(client)
    data = restoreData(client)
    data.update({"designerId": "1", "companyName": "Forged", "status": "Suspended"})
    response = client.post("/designer/company/restore?designerId=1", data=data, follow_redirects=True)
    assert b"Company profile restored successfully" in response.data
    assert readCompanyRow(userId)["companyName"] == "Modena"
    assert readCompanyRow(userId)["status"] == "Active"


def test_ut17r_20_dashboard_otherDesignerCannotSeeOrRestoreCompany():
    userId = createSuspendedCompany()
    profile = CompanyProfile().getSuspendedCompanyProfile(userId)
    UserAccount().createUserAccount(UserAccount(username="other17", password="Design@123", fullName="Other Designer", email="", phone="", profileId=2))
    client = app.test_client()
    client.post("/designer/login", data={"username": "other17", "password": "Design@123"})
    response = client.get("/designer/dashboard")
    assert b"Restore company profile" not in response.data
    assert b"Modena" not in response.data
    # the owner comes from other17's session, so designer13's row doesn't match
    response = client.post("/designer/company/restore",
                           data={"companyId": profile.companyId, "revision": profile.revision, "designerId": userId},
                           follow_redirects=True)
    assert b"Company profile could not be restored" in response.data
    assert readCompanyRow(userId)["status"] == "Suspended"


def test_ut17r_21_dashboard_newDesignerGetsCreate():
    UserAccount().createUserAccount(UserAccount(username="designer13", password="Design@123", fullName="Tengku Uda Designer", email="", phone="", profileId=2))
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/dashboard")
    assert b'href="/designer/company/create"' in response.data
    assert b"Restore company profile" not in response.data


def test_ut17r_22_restore_afterLogoutAndLoginStillAvailable():
    userId = createSuspendedCompany()
    client = app.test_client()
    loginAsDesigner13(client)
    client.get("/designer/dashboard")
    client.post("/designer/logout")
    loginAsDesigner13(client)
    assert b"Restore company profile" in client.get("/designer/dashboard").data
    client.post("/designer/company/restore", data=restoreData(client))
    assert readCompanyRow(userId)["status"] == "Active"


def test_ut17r_23_restore_oldDashboardFormRejected():
    # restored + deleted again in between -> revision went up, so the old form matches no row
    userId = createSuspendedCompany()
    client = app.test_client()
    loginAsDesigner13(client)
    data = restoreData(client)
    profile = CompanyProfile().getSuspendedCompanyProfile(userId)
    CompanyProfile().restoreCompanyProfile(userId, profile.companyId, profile.revision)
    CompanyProfile().suspendCompanyProfile(userId, profile.companyId, profile.revision + 1)
    response = client.post("/designer/company/restore", data=data, follow_redirects=True)
    assert b"Company profile could not be restored" in response.data
    assert readCompanyRow(userId)["status"] == "Suspended"


def test_ut17r_24_deleteRestore_doesNotLoseDetails():
    userId = createSuspendedCompany()
    before = readCompanyRow(userId)
    client = app.test_client()
    loginAsDesigner13(client)
    client.post("/designer/company/restore", data=restoreData(client))
    assert b"Modena" in client.get("/designer/company/search?keyword=modena").data
    client.post("/designer/company/delete", data=deleteData(client))
    assert readCompanyRow(userId)["status"] == "Suspended"
    client.post("/designer/company/restore", data=restoreData(client))
    after = readCompanyRow(userId)
    assert after == dict(before, status="Active", revision=before["revision"] + 2)
    conn = getConnection()
    assert conn.execute("SELECT COUNT(*) FROM company_profile").fetchone()[0] == 1
    conn.close()


def test_ut17r_25_dashboard_openDoesNotRestore():
    userId = createSuspendedCompany()
    before = readCompanyRow(userId)
    client = app.test_client()
    loginAsDesigner13(client)
    client.get("/designer/dashboard")
    client.get("/designer/dashboard")
    assert readCompanyRow(userId) == before


# ---------- system tests (TC) ----------

def test_tc17_10_restoreOnlyWorksForOwner():
    # designer A = designer13 (Suspended profile), designer B = other17 with no profile
    userId = createSuspendedCompany()
    profile = CompanyProfile().getSuspendedCompanyProfile(userId)
    UserAccount().createUserAccount(UserAccount(username="other17", password="Design@123", fullName="Other Designer", email="", phone="", profileId=2))
    client = app.test_client()
    client.post("/designer/login", data={"username": "other17", "password": "Design@123"})
    response = client.get("/designer/dashboard")
    assert b"Restore company profile" not in response.data
    assert b"Modena" not in response.data
    client.post("/designer/company/restore", data={"companyId": profile.companyId, "revision": profile.revision})
    assert readCompanyRow(userId)["status"] == "Suspended"


def test_tc17_11_outOfDateRestoreForm():
    # two tabs: restore + delete again in the first, then Restore in the second (old revision)
    userId = createSuspendedCompany()
    client = app.test_client()
    loginAsDesigner13(client)
    secondTab = restoreData(client)
    client.post("/designer/company/restore", data=restoreData(client))
    client.post("/designer/company/delete", data=deleteData(client))
    before = readCompanyRow(userId)
    response = client.post("/designer/company/restore", data=secondTab, follow_redirects=True)
    assert b"Company profile could not be restored. Please reopen the dashboard and try again" in response.data
    assert readCompanyRow(userId) == before
