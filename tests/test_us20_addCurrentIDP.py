# Unit tests for US20 Add current IDP.
# conftest.py gives each test a fresh database with the existing default users.
# Designer tests add designer20 / Design@123 (Tengku Uda Designer, profile 2).
# Categories come from US41 (IDPCategory) and are seeded per test.

from app import app
from database.db import getConnection
from entity.userAccount import UserAccount
from entity.idp import IDP
from entity.idpCategory import IDPCategory
from control.addCurrentIDPController import AddCurrentIDPController
from control.suspendIDPCategoryController import SuspendIDPCategoryController
from boundary.addCurrentIDPPage import AddCurrentIDPPage


def createDesigner20():
    UserAccount().createUserAccount(
        UserAccount(username="designer20", password="Design@123", fullName="Tengku Uda Designer", email="designer20@archss.com", phone="", profileId=2))
    return UserAccount().verifyCredentials("designer20", "Design@123").userId


def loginAsDesigner20(client):
    return client.post("/designer/login", data={"username": "designer20", "password": "Design@123"})


def createCategory(name="Kitchen"):
    IDPCategory().createIDPCategory(IDPCategory(categoryName=name))
    return IDPCategory().searchIDPCategories(name)[0].categoryId


def formData(categoryId):
    # what the browser posts
    return {"title": "Tampines HDB kitchen", "description": "Open-concept kitchen, carpentry stage.",
            "categoryId": categoryId, "location": "Tampines"}


def makeIDP(designerId, categoryId, **changes):
    # add takes an IDP object now, not a dict
    fields = formData(categoryId)
    fields.update(changes)
    return IDP(designerId=designerId, **fields)


def countIDPs():
    conn = getConnection()
    total = conn.execute("SELECT COUNT(*) FROM idp").fetchone()[0]
    conn.close()
    return total


# ---------- AddCurrentIDPController.addCurrentIDP() / IDP.addCurrentIDP() ----------

def test_ut20_1_addCurrentIDP_valid():
    designerId = createDesigner20()
    categoryId = createCategory()
    assert AddCurrentIDPController().addCurrentIDP(makeIDP(designerId, categoryId)) is True
    idp = IDPCategory().getIDPsInCategory(categoryId)[0]
    assert idp.designerId == designerId
    assert idp.title == "Tampines HDB kitchen"
    assert idp.projectType == "Current"
    assert idp.status == "Active"


def test_ut20_2_addCurrentIDP_suspendedCategoryRejected():
    # the entity checks the category is still Active at the moment of saving (US44)
    designerId = createDesigner20()
    categoryId = createCategory()
    SuspendIDPCategoryController().suspendIDPCategory(categoryId)
    assert AddCurrentIDPController().addCurrentIDP(makeIDP(designerId, categoryId)) is False
    assert countIDPs() == 0


def test_ut20_3_addCurrentIDP_unknownAccount():
    categoryId = createCategory()
    assert AddCurrentIDPController().addCurrentIDP(makeIDP(9999, categoryId)) is False


def test_ut20_4_addCurrentIDP_unknownCategory():
    designerId = createDesigner20()
    assert AddCurrentIDPController().addCurrentIDP(makeIDP(designerId, 9999)) is False
    assert countIDPs() == 0


# ---------- AddCurrentIDPPage.validateInput() ----------

def test_ut20_6_validateInput_valid():
    page = AddCurrentIDPPage()
    assert page.validateInput(makeIDP(1, createCategory())) is True
    assert page.fieldErrors == {}


def test_ut20_7_validateInput_requiredFields():
    page = AddCurrentIDPPage()
    assert page.validateInput(makeIDP(1, createCategory(), title="", description="")) is False
    assert page.fieldErrors["title"] == "This field is required"
    assert page.fieldErrors["description"] == "This field is required"


def test_ut20_8_validateInput_titleTooShort():
    page = AddCurrentIDPPage()
    page.validateInput(makeIDP(1, createCategory(), title="Ab"))
    assert page.fieldErrors["title"] == "Title must be 3-100 characters"


def test_ut20_9_validateInput_tooLong():
    page = AddCurrentIDPPage()
    page.validateInput(makeIDP(1, createCategory(), title="x" * 101, location="x" * 201))
    assert page.fieldErrors["title"] == "Maximum 100 characters"
    assert page.fieldErrors["location"] == "Maximum 200 characters"


def test_ut20_10_validateInput_noCategoryChosen():
    createCategory()
    page = AddCurrentIDPPage()
    page.validateInput(makeIDP(1, None))
    assert page.fieldErrors["categoryId"] == "Choose an available category"


def test_ut20_11_validateInput_unknownOrSuspendedCategory():
    kitchen = createCategory("Kitchen")
    SuspendIDPCategoryController().suspendIDPCategory(kitchen)
    page = AddCurrentIDPPage()
    page.validateInput(makeIDP(1, kitchen))
    assert "categoryId" in page.fieldErrors
    page.validateInput(makeIDP(1, 9999))
    assert "categoryId" in page.fieldErrors


def test_ut20_12_validateInput_locationOptional():
    page = AddCurrentIDPPage()
    assert page.validateInput(makeIDP(1, createCategory(), location="")) is True


# ---------- AddCurrentIDPPage.getAvailableCategories() (borrows US45's controller) ----------

def test_ut20_13_getAvailableCategories_activeOnlySortedByName():
    createCategory("Kitchen")
    createCategory("Bedroom")
    office = createCategory("Office")
    SuspendIDPCategoryController().suspendIDPCategory(office)
    names = [c.categoryName for c in AddCurrentIDPPage().getAvailableCategories()]
    assert names == ["Bedroom", "Kitchen"]


# ---------- AddCurrentIDPPage via the /designer/idps/add route ----------

def test_ut20_16_dashboard_linksToAddCurrentIDP():
    createDesigner20()
    client = app.test_client()
    loginAsDesigner20(client)
    response = client.get("/designer/dashboard")
    assert b'href="/designer/idps/add"' in response.data
    assert b"Current IDPs" in response.data


def test_ut20_17_addPage_showsFormWithCategories():
    createDesigner20()
    createCategory("Kitchen")
    client = app.test_client()
    loginAsDesigner20(client)
    response = client.get("/designer/idps/add")
    assert response.status_code == 200
    for field in (b'name="title"', b'name="categoryId"', b'name="description"', b'name="location"'):
        assert field in response.data
    assert b"Kitchen" in response.data


def test_ut20_18_addPage_noCategoriesYet():
    createDesigner20()
    client = app.test_client()
    loginAsDesigner20(client)
    response = client.get("/designer/idps/add")
    assert b"No IDP categories are available yet" in response.data
    assert b'name="title"' not in response.data


def test_ut20_19_submit_valid_redirectsToDashboardWithMessage():
    createDesigner20()
    categoryId = createCategory()
    client = app.test_client()
    loginAsDesigner20(client)
    response = client.post("/designer/idps/add", data=formData(categoryId), follow_redirects=True)
    assert b"Current IDP added successfully" in response.data
    assert countIDPs() == 1


def test_ut20_20_submit_invalid_showsErrorsAndKeepsInput():
    createDesigner20()
    categoryId = createCategory()
    client = app.test_client()
    loginAsDesigner20(client)
    data = formData(categoryId)
    data["title"] = "Ab"
    response = client.post("/designer/idps/add", data=data)
    assert b"Please fix the highlighted fields" in response.data
    assert b"Title must be 3-100 characters" in response.data
    assert b"Open-concept kitchen" in response.data
    assert countIDPs() == 0


def test_ut20_21_submit_ownerAlwaysFromSession():
    designerId = createDesigner20()
    categoryId = createCategory()
    client = app.test_client()
    loginAsDesigner20(client)
    data = formData(categoryId)
    data["designerId"] = 1          # a forged owner field must be ignored
    client.post("/designer/idps/add", data=data)
    assert IDPCategory().getIDPsInCategory(categoryId)[0].designerId == designerId


def test_ut20_22_addPage_notLoggedIn_redirects():
    response = app.test_client().get("/designer/idps/add")
    assert response.headers["Location"].endswith("/designer/login")


def test_ut20_23_submit_trimsSpaces():
    # the page tidies up the input, so the entity gets clean values
    designerId = createDesigner20()
    categoryId = createCategory()
    client = app.test_client()
    loginAsDesigner20(client)
    data = formData(categoryId)
    data["title"] = "  Tampines HDB kitchen  "
    data["location"] = "  Tampines "
    client.post("/designer/idps/add", data=data)
    idp = IDPCategory().getIDPsInCategory(categoryId)[0]
    assert idp.designerId == designerId
    assert idp.title == "Tampines HDB kitchen"
    assert idp.location == "Tampines"


def test_ut20_24_addedIDP_appearsInManagerCategoryView():
    # US20 + US42 working together: the manager sees the new IDP under its category
    createDesigner20()
    categoryId = createCategory()
    client = app.test_client()
    loginAsDesigner20(client)
    client.post("/designer/idps/add", data=formData(categoryId))
    UserAccount().createUserAccount(UserAccount(username="manager20", password="Manager@123", fullName="Daniel Tan", email="", phone="", profileId=4))
    managerClient = app.test_client()
    managerClient.post("/manager/login", data={"username": "manager20", "password": "Manager@123"})
    response = managerClient.get("/manager/categories/" + str(categoryId))
    assert b"Tampines HDB kitchen" in response.data
