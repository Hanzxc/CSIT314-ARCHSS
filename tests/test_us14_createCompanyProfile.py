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
        UserAccount(username="designer13", password="Design@123", fullName="Tengku Uda Designer", email="designer13@archss.com", phone="", profileId=2))
    return UserAccount().verifyCredentials("designer13", "Design@123").userId


def companyData():
    return {"companyName": "Uda Interiors", "description": "Interior design for homes.",
            "services": "Space planning, renovation", "email": "hello@udainteriors.com",
            "phone": "+65 6123 4567", "address": "10 Design Street"}


def makeCompany(designerId, data):
    # create/update take a CompanyProfile object now, not a dict
    return CompanyProfile(designerId=designerId, **data)


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
    assert CreateCompanyProfileController().createCompanyProfile(makeCompany(userId, companyData())) is True
    profile = CompanyProfile().getCompanyProfile(userId)
    assert profile.companyName == "Uda Interiors"
    assert profile.designerId == userId
    assert profile.services == "Space planning, renovation"


def test_ut14_2_createCompanyProfile_alreadyExists():
    userId = createDesigner13()
    control = CreateCompanyProfileController()
    assert control.createCompanyProfile(makeCompany(userId, companyData())) is True
    before = countCompanies()
    data = companyData()
    data["companyName"] = "Another Company"
    assert control.createCompanyProfile(makeCompany(userId, data)) is False
    assert countCompanies() == before
    assert CompanyProfile().getCompanyProfile(userId).companyName == "Uda Interiors"










def test_ut14_7_createCompanyProfile_optionalFieldsEmpty():
    userId = createDesigner13()
    data = companyData()
    data.update(email="", phone="", address="")
    assert CreateCompanyProfileController().createCompanyProfile(makeCompany(userId, data)) is True


def test_ut14_8_createCompanyProfile_trimsInput():
    # the page trims now (not the entity), so this goes through the browser
    userId = createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    data = companyData()
    data["companyName"] = "  Uda Interiors  "
    client.post("/designer/company/create", data=data)
    assert CompanyProfile().getCompanyProfile(userId).companyName == "Uda Interiors"


# ---------- CompanyProfile (new entity) ----------

def test_ut14_9_getCompanyProfile_notFound():
    assert CompanyProfile().getCompanyProfile(9999) is None


def test_ut14_11_entity_duplicateOwnerRejected():
    userId = createDesigner13()
    assert CompanyProfile().createCompanyProfile(makeCompany(userId, companyData())) is True
    assert CompanyProfile().createCompanyProfile(makeCompany(userId, companyData())) is False
    assert countCompanies() == 1


def test_ut14_12_profilesKeptSeparate():
    first = createDesigner13()
    UserAccount().createUserAccount(UserAccount(username="designer14", password="Design@123", fullName="Daniel Tan", email="", phone="", profileId=2))
    second = UserAccount().verifyCredentials("designer14", "Design@123").userId
    assert CreateCompanyProfileController().createCompanyProfile(makeCompany(first, companyData())) is True
    assert CompanyProfile().getCompanyProfile(second) is None
    assert CreateCompanyProfileController().createCompanyProfile(makeCompany(second, companyData())) is True
    assert countCompanies() == 2


# ---------- CreateCompanyProfilePage.validateInput() ----------

def test_ut14_13_validateInput_valid():
    assert CreateCompanyProfilePage().validateInput(makeCompany(None, companyData())) is True


def test_ut14_14_validateInput_missingName():
    page = CreateCompanyProfilePage()
    data = companyData()
    data["companyName"] = ""
    assert page.validateInput(makeCompany(None, data)) is False
    assert "companyName" in page.fieldErrors


def test_ut14_15_validateInput_missingDescription():
    data = companyData()
    data["description"] = ""
    assert CreateCompanyProfilePage().validateInput(makeCompany(None, data)) is False


def test_ut14_16_validateInput_missingServices():
    data = companyData()
    data["services"] = ""
    assert CreateCompanyProfilePage().validateInput(makeCompany(None, data)) is False


def test_ut14_17_validateInput_invalidEmail():
    data = companyData()
    data["email"] = "not-an-email"
    assert CreateCompanyProfilePage().validateInput(makeCompany(None, data)) is False


def test_ut14_18_validateInput_nameTooLong():
    data = companyData()
    data["companyName"] = "A" * 101
    assert CreateCompanyProfilePage().validateInput(makeCompany(None, data)) is False


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
    CreateCompanyProfileController().createCompanyProfile(makeCompany(userId, companyData()))
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
    CreateCompanyProfileController().createCompanyProfile(makeCompany(userId, companyData()))
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/dashboard")
    assert b"Company profile created" in response.data
    assert b'href="/designer/company/create"' not in response.data




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


# ---------- Active / Suspended lifecycle ----------

def test_ut14_32_create_setsActiveAutomatically():
    userId = createDesigner13()
    data = companyData()
    data["status"] = "Suspended"    # the entity ignores this, new ones are always Active
    assert CreateCompanyProfileController().createCompanyProfile(makeCompany(userId, data)) is True
    assert CompanyProfile().getCompanyProfile(userId).status == "Active"


def test_ut14_33_create_suspendedRowCountsAsDuplicate():
    # a deleted (Suspended) profile still counts as "already exists" - the designer
    # uses the Restore button to get it back instead of creating it again
    userId = createDesigner13()
    control = CreateCompanyProfileController()
    assert control.createCompanyProfile(makeCompany(userId, companyData())) is True
    original = CompanyProfile().getCompanyProfile(userId)
    assert CompanyProfile().suspendCompanyProfile(userId, original.companyId, original.revision) is True
    data = companyData()
    data["companyName"] = "Uda Interiors Reopened"
    assert control.createCompanyProfile(makeCompany(userId, data)) is False
    conn = getConnection()
    row = conn.execute("SELECT * FROM company_profile WHERE designerId=?", (userId,)).fetchone()
    conn.close()
    assert row["status"] == "Suspended"
    assert row["companyName"] == "Uda Interiors"
    assert countCompanies() == 1


def test_ut14_34_createPage_existingProfile_stillShowsEmptyForm():
    # no "has a profile?" check before the form - the duplicate is only found when they save
    userId = createDesigner13()
    CompanyProfile().createCompanyProfile(makeCompany(userId, companyData()))
    before = CompanyProfile().getCompanyProfile(userId)
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company/create")
    assert response.status_code == 200
    assert b'name="companyName" value=""' in response.data
    assert b"You already have a company profile" not in response.data
    assert b"Uda Interiors" not in response.data
    assert vars(CompanyProfile().getCompanyProfile(userId)) == vars(before)
    assert countCompanies() == 1


def test_ut14_35_createPage_suspendedProfileShowsExists():
    userId = createDesigner13()
    CompanyProfile().createCompanyProfile(makeCompany(userId, companyData()))
    original = CompanyProfile().getCompanyProfile(userId)
    CompanyProfile().suspendCompanyProfile(userId, original.companyId, original.revision)
    client = app.test_client()
    loginAsDesigner13(client)
    data = companyData()
    data["companyName"] = "Reactivated Interiors"
    response = client.post("/designer/company/create", data=data)
    assert b"You already have a company profile" in response.data
    assert client.get("/designer/company").status_code == 404
    assert countCompanies() == 1


# ---------- system tests (TC) ----------

def test_tc14_8_alreadyHasProfile_formOpensThenSaveRefused():
    userId = createDesigner13()
    CompanyProfile().createCompanyProfile(makeCompany(userId, companyData()))
    before = vars(CompanyProfile().getCompanyProfile(userId))
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company/create")
    assert response.status_code == 200
    assert b'name="companyName" value=""' in response.data
    data = companyData()
    data["companyName"] = "Another Company"
    response = client.post("/designer/company/create", data=data)
    assert b"You already have a company profile" in response.data
    assert vars(CompanyProfile().getCompanyProfile(userId)) == before
    assert countCompanies() == 1
