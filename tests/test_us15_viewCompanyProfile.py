# Unit tests for US15 View company profile.
# conftest.py creates a fresh database for every test.
# Designer tests add designer13 / Design@123 (Tengku Uda Designer, profile 2).

from app import app
from database.db import getConnection
from entity.userAccount import UserAccount
from entity.companyProfile import CompanyProfile
from control.viewCompanyProfileController import ViewCompanyProfileController


def createDesigner13():
    UserAccount().createUserAccount(
        "designer13", "Design@123", "Tengku Uda Designer", "designer13@archss.com", "", 2)
    return UserAccount().verifyCredentials("designer13", "Design@123").userId


def companyData():
    return {"companyName": "Uda Interiors", "description": "Interior design for homes.",
            "services": "Space planning, renovation", "email": "hello@udainteriors.com",
            "phone": "+65 6123 4567", "address": "10 Design Street"}


def makeCompany(designerId, data):
    # create takes a CompanyProfile object now, not a dict
    return CompanyProfile(designerId=designerId, **data)


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


# ---------- ViewCompanyProfileController.viewCompanyProfile() ----------

def test_ut15_1_viewCompanyProfile_valid():
    userId = createCompanyForDesigner13()
    profile = ViewCompanyProfileController().viewCompanyProfile(userId)
    assert profile is not None
    assert profile.companyName == "Uda Interiors"
    assert profile.designerId == userId


def test_ut15_2_viewCompanyProfile_noProfile():
    userId = createDesigner13()
    assert ViewCompanyProfileController().viewCompanyProfile(userId) is None


def test_ut15_3_viewCompanyProfile_unknownUser():
    assert ViewCompanyProfileController().viewCompanyProfile(9999) is None


def test_ut15_7_viewCompanyProfile_doesNotChangeData():
    userId = createCompanyForDesigner13()
    before = companyRows()
    ViewCompanyProfileController().viewCompanyProfile(userId)
    assert companyRows() == before


# ---------- CompanyProfile.getCompanyProfile() (shared US14 entity) ----------

def test_ut15_8_getCompanyProfile_allFields():
    userId = createCompanyForDesigner13()
    profile = CompanyProfile().getCompanyProfile(userId)
    assert profile.description == "Interior design for homes."
    assert profile.services == "Space planning, renovation"
    assert profile.email == "hello@udainteriors.com"
    assert profile.phone == "+65 6123 4567"
    assert profile.address == "10 Design Street"


def test_ut15_9_getCompanyProfile_differentOwner():
    createCompanyForDesigner13()
    UserAccount().createUserAccount("designer15", "Design@123", "Daniel Tan", "", "", 2)
    otherId = UserAccount().verifyCredentials("designer15", "Design@123").userId
    assert CompanyProfile().getCompanyProfile(otherId) is None


# ---------- whole page, through the browser (test client) ----------

def test_ut15_10_viewPage_showsCompanyDetails():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company")
    assert response.status_code == 200
    for text in companyData().values():
        assert text.encode() in response.data


def test_ut15_11_viewPage_notLoggedIn():
    client = app.test_client()
    response = client.get("/designer/company")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/designer/login")


def test_ut15_13_viewPage_noProfile():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company")
    assert response.status_code == 404
    assert b"You have not created a company profile yet" in response.data
    assert b'href="/designer/company/create"' in response.data
    assert companyRows() == []


def test_ut15_14_viewPage_optionalFieldsEmpty():
    userId = createDesigner13()
    data = companyData()
    data.update(email="", phone="", address="")
    CompanyProfile().createCompanyProfile(makeCompany(userId, data))
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company")
    assert response.status_code == 200
    assert response.data.count(b"Not provided") == 3


def test_ut15_15_viewPage_ignoresForgedOwner():
    createCompanyForDesigner13()
    UserAccount().createUserAccount("designer15", "Design@123", "Daniel Tan", "", "", 2)
    otherId = UserAccount().verifyCredentials("designer15", "Design@123").userId
    data = companyData()
    data["companyName"] = "Other Designer Private Company"
    CompanyProfile().createCompanyProfile(makeCompany(otherId, data))
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company?designerId=" + str(otherId) + "&companyId=2")
    assert b"Uda Interiors" in response.data
    assert b"Other Designer Private Company" not in response.data


def test_ut15_16_viewPage_otherAccountWithoutProfile():
    createCompanyForDesigner13()
    UserAccount().createUserAccount("designer15", "Design@123", "Daniel Tan", "", "", 2)
    client = app.test_client()
    client.post("/designer/login", data={"username": "designer15", "password": "Design@123"})
    response = client.get("/designer/company?designerId=4")
    assert response.status_code == 404
    assert b"Uda Interiors" not in response.data


def test_ut15_17_viewPage_escapeCompanyText():
    userId = createDesigner13()
    data = companyData()
    data["description"] = "<script>alert(1)</script>"
    CompanyProfile().createCompanyProfile(makeCompany(userId, data))
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company")
    assert b"<script>alert(1)</script>" not in response.data
    assert b"&lt;script&gt;alert(1)&lt;/script&gt;" in response.data


def test_ut15_18_viewPage_noLoginCredentialsInCompanyCard():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company")
    assert b"Design@123" not in response.data
    assert b"Tengku Uda Designer" not in response.data
    assert b"designer13@archss.com" not in response.data
    assert b'name="password"' not in response.data


def test_ut15_19_viewPage_doesNotChangeData():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    before = companyRows()
    client.get("/designer/company")
    client.get("/designer/company")
    assert companyRows() == before


def test_ut15_20_viewPage_isReadOnly():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company")
    # US19 adds a Log out submit button to the header; company content stays read-only.
    companyContent = response.data.split(b'<main class="content">', 1)[1]
    assert b"<textarea" not in companyContent
    assert b'type="submit"' not in companyContent
    assert b'href="/designer/dashboard"' in response.data
    assert client.post("/designer/company", data=companyData()).status_code == 405


def test_ut15_21_dashboard_showsViewLinkAfterCreation():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/dashboard")
    assert b'href="/designer/company"' in response.data
    assert b"View company profile" in response.data


def test_ut15_22_dashboard_noViewLinkBeforeCreation():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/dashboard")
    assert b'href="/designer/company"' not in response.data
    assert b'href="/designer/company/create"' in response.data


def test_ut15_24_createThenView_endToEnd():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.post("/designer/company/create", data=companyData(), follow_redirects=True)
    assert b"Company profile created successfully" in response.data
    assert b'href="/designer/company"' in response.data
    response = client.get("/designer/company")
    assert response.status_code == 200
    assert b"Uda Interiors" in response.data
    assert b"Space planning, renovation" in response.data


def test_ut15_suspendedProfile_isUnavailable():
    userId = createDesigner13()
    CompanyProfile().createCompanyProfile(makeCompany(userId, companyData()))
    profile = CompanyProfile().getCompanyProfile(userId)
    assert CompanyProfile().suspendCompanyProfile(userId, profile.companyId) is True
    client = app.test_client()
    loginAsDesigner13(client)
    assert client.get("/designer/company").status_code == 404
    assert b"Uda Interiors" not in client.get("/designer/company").data
