# Unit tests for US16 Update company profile.
# conftest.py creates a fresh database for every test.
# Designer tests add designer13 / Design@123 (Tengku Uda Designer, profile 2).

import sqlite3

import pytest

from app import app
from database.db import getConnection
from entity.userAccount import UserAccount
from entity.companyProfile import CompanyProfile
from control.updateCompanyProfileController import UpdateCompanyProfileController
from boundary.updateCompanyProfilePage import UpdateCompanyProfilePage


def companyData():
    return {"companyName": "Uda Interiors", "description": "Interior design for homes.",
            "services": "Space planning, renovation", "email": "hello@udainteriors.com",
            "phone": "+65 6123 4567", "address": "10 Design Street"}


def updatedData():
    return {"companyName": "Uda Interiors Studio", "description": "Modern homes and offices.",
            "services": "Renovation, office design", "email": "studio@udainteriors.com",
            "phone": "+65 6987 6543", "address": "20 Studio Street"}


def makeCompany(designerId, data):
    # create/update take a CompanyProfile object now, not a dict
    return CompanyProfile(designerId=designerId, **data)


def createDesigner13():
    UserAccount().createUserAccount(
        UserAccount(username="designer13", password="Design@123", fullName="Tengku Uda Designer", email="designer13@archss.com", phone="", profileId=2))
    return UserAccount().verifyCredentials("designer13", "Design@123").userId


def createCompanyForDesigner13():
    userId = createDesigner13()
    CompanyProfile().createCompanyProfile(makeCompany(userId, companyData()))
    return userId


def loginAsDesigner13(client):
    return client.post("/designer/login", data={"username": "designer13", "password": "Design@123"})


def companyRows():
    conn = getConnection()
    rows = conn.execute("SELECT * FROM company_profile ORDER BY companyId").fetchall()
    conn.close()
    return [tuple(row) for row in rows]


# ---------- UpdateCompanyProfileController.updateCompanyProfile() ----------

def test_ut16_1_updateCompanyProfile_valid():
    userId = createCompanyForDesigner13()
    assert UpdateCompanyProfileController().updateCompanyProfile(makeCompany(userId, updatedData())) is True
    profile = CompanyProfile().getCompanyProfile(userId)
    for field, value in updatedData().items():
        assert getattr(profile, field) == value


def test_ut16_2_updateCompanyProfile_keepsIdentity():
    userId = createCompanyForDesigner13()
    before = CompanyProfile().getCompanyProfile(userId)
    UpdateCompanyProfileController().updateCompanyProfile(makeCompany(userId, updatedData()))
    after = CompanyProfile().getCompanyProfile(userId)
    assert after.companyId == before.companyId
    assert after.designerId == before.designerId
    assert after.createdDate == before.createdDate
    assert len(companyRows()) == 1


def test_ut16_3_updateCompanyProfile_noProfile():
    userId = createDesigner13()
    assert UpdateCompanyProfileController().updateCompanyProfile(makeCompany(userId, updatedData())) is False
    assert companyRows() == []


def test_ut16_5_updateCompanyProfile_unknownUser():
    assert UpdateCompanyProfileController().updateCompanyProfile(makeCompany(9999, updatedData())) is False


def test_ut16_6_updateCompanyProfile_missingRequired():
    # the page checks the input now, so this goes through the browser
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = updatedData()
    data["services"] = "   "
    before = companyRows()
    response = client.post("/designer/company/update", data=data)
    assert b"Please fix the highlighted fields" in response.data
    assert companyRows() == before


def test_ut16_7_updateCompanyProfile_invalidEmail():
    userId = createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = updatedData()
    data["email"] = "not-an-email"
    response = client.post("/designer/company/update", data=data)
    assert b"Enter a valid email address" in response.data
    assert CompanyProfile().getCompanyProfile(userId).email == "hello@udainteriors.com"


def test_ut16_8_updateCompanyProfile_clearOptionalFields():
    userId = createCompanyForDesigner13()
    data = updatedData()
    data.update(email="", phone="", address="")
    assert UpdateCompanyProfileController().updateCompanyProfile(makeCompany(userId, data)) is True
    profile = CompanyProfile().getCompanyProfile(userId)
    assert profile.email == ""
    assert profile.phone == ""
    assert profile.address == ""


def test_ut16_9_updateCompanyProfile_trimsInput():
    # the page trims now (not the entity), so this goes through the browser
    userId = createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = updatedData()
    data["companyName"] = "  Uda Interiors Studio  "
    client.post("/designer/company/update", data=data)
    assert CompanyProfile().getCompanyProfile(userId).companyName == "Uda Interiors Studio"


# ---------- CompanyProfile.updateCompanyProfile() ----------

def test_ut16_11_entity_updatesOnlyOwner():
    userId = createCompanyForDesigner13()
    UserAccount().createUserAccount(UserAccount(username="designer16", password="Design@123", fullName="Daniel Tan", email="", phone="", profileId=2))
    otherId = UserAccount().verifyCredentials("designer16", "Design@123").userId
    CompanyProfile().createCompanyProfile(makeCompany(otherId, companyData()))
    assert CompanyProfile().updateCompanyProfile(makeCompany(userId, updatedData())) is True
    assert CompanyProfile().getCompanyProfile(otherId).companyName == "Uda Interiors"


def test_ut16_12_entity_missingOwnerDoesNotInsert():
    assert CompanyProfile().updateCompanyProfile(makeCompany(9999, updatedData())) is False
    assert companyRows() == []


def test_ut16_13_entity_invalidWriteRollsBack():
    # the entity doesn't validate any more (the page does), but the table's CHECK
    # still stops a blank description getting in as a backup
    userId = createCompanyForDesigner13()
    data = updatedData()
    data["description"] = ""
    before = companyRows()
    with pytest.raises(sqlite3.IntegrityError):
        CompanyProfile().updateCompanyProfile(makeCompany(userId, data))
    assert companyRows() == before


# ---------- UpdateCompanyProfilePage.validateInput() ----------

def test_ut16_14_validateInput_valid():
    assert UpdateCompanyProfilePage().validateInput(makeCompany(None, updatedData())) is True


def test_ut16_15_validateInput_blankName():
    page = UpdateCompanyProfilePage()
    data = updatedData()
    data["companyName"] = ""
    assert page.validateInput(makeCompany(None, data)) is False
    assert "companyName" in page.fieldErrors


def test_ut16_16_validateInput_nameTooLong():
    data = updatedData()
    data["companyName"] = "A" * 101
    assert UpdateCompanyProfilePage().validateInput(makeCompany(None, data)) is False


# ---------- whole page, through the browser (test client) ----------

def test_ut16_17_updatePage_prefillsForm():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company/update")
    assert response.status_code == 200
    for text in companyData().values():
        assert text.encode() in response.data
    assert b"Save changes" in response.data


def test_ut16_18_updatePage_success():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.post("/designer/company/update", data=updatedData())
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/designer/company")
    response = client.get("/designer/company")
    assert b"Company profile updated successfully" in response.data
    assert b"Uda Interiors Studio" in response.data
    assert b"Modern homes and offices." in response.data


def test_ut16_19_updatePage_invalidInputKeepsStoredData():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = updatedData()
    data["companyName"] = ""
    before = companyRows()
    response = client.post("/designer/company/update", data=data)
    assert b"Please fix the highlighted fields" in response.data
    assert b"Modern homes and offices." in response.data
    assert companyRows() == before


def test_ut16_20_cancel_changesNothing():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    before = companyRows()
    response = client.get("/designer/company/update")
    assert b'href="/designer/company"' in response.data
    client.get("/designer/company")
    assert companyRows() == before


def test_ut16_21_updatePage_notLoggedIn():
    client = app.test_client()
    response = client.get("/designer/company/update")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/designer/login")
    assert client.post("/designer/company/update", data=updatedData()).status_code == 302
    assert companyRows() == []


def test_ut16_23_updatePage_noProfile():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company/update")
    assert response.status_code == 404
    assert b"You have not created a company profile yet" in response.data
    assert client.post("/designer/company/update", data=updatedData()).status_code == 404
    assert companyRows() == []


def test_ut16_24_updatePage_ignoresForgedOwner():
    userId = createCompanyForDesigner13()
    UserAccount().createUserAccount(UserAccount(username="designer16", password="Design@123", fullName="Daniel Tan", email="", phone="", profileId=2))
    otherId = UserAccount().verifyCredentials("designer16", "Design@123").userId
    CompanyProfile().createCompanyProfile(makeCompany(otherId, companyData()))
    client = app.test_client()
    loginAsDesigner13(client)
    data = updatedData()
    data.update(designerId=str(otherId), companyId="2")
    client.post("/designer/company/update?designerId=" + str(otherId), data=data)
    assert CompanyProfile().getCompanyProfile(userId).companyName == "Uda Interiors Studio"
    assert CompanyProfile().getCompanyProfile(otherId).companyName == "Uda Interiors"


def test_ut16_26_updatePage_escapesPrefilledText():
    userId = createDesigner13()
    data = companyData()
    data["description"] = "<script>alert(1)</script>"
    CompanyProfile().createCompanyProfile(makeCompany(userId, data))
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company/update")
    assert b"<script>alert(1)</script>" not in response.data
    assert b"&lt;script&gt;" in response.data


def test_ut16_27_viewPage_showsUpdateLink():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    assert b'href="/designer/company/update"' in client.get("/designer/company").data


def test_ut16_28_createUpdateView_endToEnd():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    client.post("/designer/company/create", data=companyData())
    client.post("/designer/company/update", data=updatedData())
    response = client.get("/designer/company")
    assert b"Uda Interiors Studio" in response.data
    assert b"Renovation, office design" in response.data
    assert b"Space planning, renovation" not in response.data
    assert len(companyRows()) == 1


def test_ut16_suspendedProfile_isUnavailable():
    userId = createDesigner13()
    CompanyProfile().createCompanyProfile(makeCompany(userId, companyData()))
    profile = CompanyProfile().getCompanyProfile(userId)
    assert CompanyProfile().suspendCompanyProfile(userId, profile.companyId) is True
    client = app.test_client()
    loginAsDesigner13(client)
    data = companyData()
    data["companyName"] = "Must not save"
    assert client.post("/designer/company/update", data=data).status_code == 404
    assert CompanyProfile().updateCompanyProfile(makeCompany(userId, data)) is False
