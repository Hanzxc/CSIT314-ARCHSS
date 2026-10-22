# Unit tests for US14 Create company profile.
# conftest.py gives each test a fresh database with the existing default users.
# Designer tests add designer13 / Design@123 (Tengku Uda Designer, profile 2).

from app import app
from database.db import getConnection
from entity.userAccount import UserAccount
from entity.companyProfile import CompanyProfile
from control.createCompanyProfileController import CreateCompanyProfileController
from boundary.createCompanyProfilePage import CreateCompanyProfilePage


def createDesigner13():
    UserAccount().createUserAccount(
        "designer13", "Design@123", "Tengku Uda Designer", "designer13@archss.com", "", 2)
    return UserAccount().verifyCredentials("designer13", "Design@123").userId


def companyData():
    return {"companyName": "Uda Interiors", "description": "Interior design for homes.",
            "services": "Space planning, renovation", "email": "hello@udainteriors.com",
            "phone": "+65 6123 4567", "address": "10 Design Street"}


def countCompanies():
    conn = getConnection()
    total = conn.execute("SELECT COUNT(*) FROM company_profile").fetchone()[0]
    conn.close()
    return total


def loginAsDesigner13(client):
    return client.post("/designer/login", data={"username": "designer13", "password": "Design@123"})


# ---------- CreateCompanyProfileController.createCompanyProfile() ----------

def test_ut14_1_createCompanyProfile_valid():
    userId = createDesigner13()
    assert CreateCompanyProfileController().createCompanyProfile(userId, companyData()) is True
    profile = CompanyProfile().getCompanyProfile(userId)
    assert profile.companyName == "Uda Interiors"
    assert profile.designerId == userId
    assert profile.services == "Space planning, renovation"


def test_ut14_2_createCompanyProfile_alreadyExists():
    userId = createDesigner13()
    control = CreateCompanyProfileController()
    assert control.createCompanyProfile(userId, companyData()) is True
    before = countCompanies()
    data = companyData()
    data["companyName"] = "Another Company"
    assert control.createCompanyProfile(userId, data) is False
    assert countCompanies() == before
    assert CompanyProfile().getCompanyProfile(userId).companyName == "Uda Interiors"


def test_ut14_3_createCompanyProfile_adminRejected():
    assert CreateCompanyProfileController().createCompanyProfile(1, companyData()) is False
    assert countCompanies() == 0


def test_ut14_4_createCompanyProfile_unknownAccount():
    assert CreateCompanyProfileController().createCompanyProfile(9999, companyData()) is False


def test_ut14_5_createCompanyProfile_suspendedAccount():
    userId = createDesigner13()
    conn = getConnection()
    conn.execute("UPDATE user_account SET status='Suspended' WHERE userId=?", (userId,))
    conn.commit()
    conn.close()
    assert CreateCompanyProfileController().createCompanyProfile(userId, companyData()) is False


def test_ut14_6_createCompanyProfile_missingRequiredField():
    userId = createDesigner13()
    data = companyData()
    data["services"] = "   "
    assert CreateCompanyProfileController().createCompanyProfile(userId, data) is False
    assert countCompanies() == 0


def test_ut14_7_createCompanyProfile_optionalFieldsEmpty():
    userId = createDesigner13()
    data = companyData()
    data.update(email="", phone="", address="")
    assert CreateCompanyProfileController().createCompanyProfile(userId, data) is True


def test_ut14_8_createCompanyProfile_trimsInput():
    userId = createDesigner13()
    data = companyData()
    data["companyName"] = "  Uda Interiors  "
    assert CreateCompanyProfileController().createCompanyProfile(userId, data) is True
    assert CompanyProfile().getCompanyProfile(userId).companyName == "Uda Interiors"


# ---------- CompanyProfile (new entity) ----------

def test_ut14_9_getCompanyProfile_notFound():
    assert CompanyProfile().getCompanyProfile(9999) is None


def test_ut14_10_hasCompanyProfile():
    userId = createDesigner13()
    assert CreateCompanyProfileController().hasCompanyProfile(userId) is False
    assert CompanyProfile().createCompanyProfile(userId, companyData()) is True
    assert CreateCompanyProfileController().hasCompanyProfile(userId) is True


def test_ut14_11_entity_duplicateOwnerRejected():
    userId = createDesigner13()
    assert CompanyProfile().createCompanyProfile(userId, companyData()) is True
    assert CompanyProfile().createCompanyProfile(userId, companyData()) is False
    assert countCompanies() == 1


def test_ut14_12_profilesKeptSeparate():
    first = createDesigner13()
    UserAccount().createUserAccount("designer14", "Design@123", "Daniel Tan", "", "", 2)
    second = UserAccount().verifyCredentials("designer14", "Design@123").userId
    assert CreateCompanyProfileController().createCompanyProfile(first, companyData()) is True
    assert CompanyProfile().getCompanyProfile(second) is None
    assert CreateCompanyProfileController().createCompanyProfile(second, companyData()) is True
    assert countCompanies() == 2


# ---------- CreateCompanyProfilePage.validateInput() ----------

def test_ut14_13_validateInput_valid():
    assert CreateCompanyProfilePage().validateInput(companyData()) is True


def test_ut14_14_validateInput_missingName():
    page = CreateCompanyProfilePage()
    data = companyData()
    data["companyName"] = ""
    assert page.validateInput(data) is False
    assert "companyName" in page.fieldErrors


def test_ut14_15_validateInput_missingDescription():
    data = companyData()
    data["description"] = ""
    assert CreateCompanyProfilePage().validateInput(data) is False


def test_ut14_16_validateInput_missingServices():
    data = companyData()
    data["services"] = ""
    assert CreateCompanyProfilePage().validateInput(data) is False


def test_ut14_17_validateInput_invalidEmail():
    data = companyData()
    data["email"] = "not-an-email"
    assert CreateCompanyProfilePage().validateInput(data) is False


def test_ut14_18_validateInput_nameTooLong():
    data = companyData()
    data["companyName"] = "A" * 101
    assert CreateCompanyProfilePage().validateInput(data) is False


# ---------- whole page, through the browser (test client) ----------

def test_ut14_19_createPage_showsForm():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company/create")
    assert response.status_code == 200
    assert b"Create company profile" in response.data
    for name in [b"companyName", b"description", b"services", b"email", b"phone", b"address"]:
        assert name in response.data


def test_ut14_20_createPage_success():
    userId = createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.post("/designer/company/create", data=companyData(), follow_redirects=True)
    assert b"Company profile created successfully" in response.data
    assert CompanyProfile().getCompanyProfile(userId).companyName == "Uda Interiors"
    assert countCompanies() == 1


def test_ut14_21_createPage_missingRequiredField():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = companyData()
    data["companyName"] = ""
    response = client.post("/designer/company/create", data=data)
    assert b"Please fix the highlighted fields" in response.data
    assert b"Interior design for homes." in response.data
    assert countCompanies() == 0


def test_ut14_22_createPage_duplicate():
    userId = createDesigner13()
    CreateCompanyProfileController().createCompanyProfile(userId, companyData())
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.post("/designer/company/create", data=companyData())
    assert b"You already have a company profile" in response.data
    assert countCompanies() == 1


def test_ut14_23_createPage_notLoggedIn():
    client = app.test_client()
    response = client.get("/designer/company/create")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/designer/login")
    assert countCompanies() == 0


def test_ut14_24_createPage_adminForbidden():
    client = app.test_client()
    client.post("/login", data={"username": "admin01", "password": "Admin@123"})
    assert client.post("/designer/company/create", data=companyData()).status_code == 403
    assert countCompanies() == 0


def test_ut14_25_createPage_usesSessionOwner():
    userId = createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = companyData()
    data["designerId"] = "1"  # forged owner field must be ignored
    client.post("/designer/company/create", data=data)
    assert CompanyProfile().getCompanyProfile(userId) is not None
    assert CompanyProfile().getCompanyProfile(1) is None


def test_ut14_26_cancel_createsNothing():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company/create")
    assert b'href="/designer/dashboard"' in response.data
    assert client.get("/designer/dashboard").status_code == 200
    assert countCompanies() == 0


def test_ut14_27_dashboard_showsCreateLink():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    assert b'href="/designer/company/create"' in client.get("/designer/dashboard").data


def test_ut14_28_dashboard_hidesCreateAfterSuccess():
    userId = createDesigner13()
    CreateCompanyProfileController().createCompanyProfile(userId, companyData())
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/dashboard")
    assert b"Company profile created" in response.data
    assert b'href="/designer/company/create"' not in response.data


def test_ut14_29_createPage_profileSuspendedAfterLogin():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    conn = getConnection()
    conn.execute("UPDATE user_profile SET status='Suspended' WHERE profileId=2")
    conn.commit()
    conn.close()
    assert client.post("/designer/company/create", data=companyData()).status_code == 403
    assert countCompanies() == 0


def test_ut14_30_entityEscapesOnRedisplay():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = companyData()
    data.update(companyName="", description="<script>alert(1)</script>")
    response = client.post("/designer/company/create", data=data)
    assert b"<script>alert(1)</script>" not in response.data
    assert b"&lt;script&gt;" in response.data


# ---------- demo data ----------

def test_ut14_31_seedCompanyData_has100AndDoesNotDuplicate():
    from database.seedCompanyData import seedCompanyData
    assert seedCompanyData() == 100
    assert countCompanies() == 100
    assert seedCompanyData() == 0
    assert countCompanies() == 100
