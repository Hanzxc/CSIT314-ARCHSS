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
from boundary.addCurrentIDPPage import AddCurrentIDPPage


def createDesigner20():
    UserAccount().createUserAccount(
        "designer20", "Design@123", "Tengku Uda Designer", "designer20@archss.com", "", 2)
    return UserAccount().verifyCredentials("designer20", "Design@123").userId


def loginAsDesigner20(client):
    return client.post("/designer/login", data={"username": "designer20", "password": "Design@123"})


def createCategory(name="Kitchen"):
    IDPCategory().createIDPCategory(name, "")
    return IDPCategory().searchIDPCategories(name)[0].categoryId


def idpData(categoryId):
    return {"title": "Tampines HDB kitchen", "description": "Open-concept kitchen, carpentry stage.",
            "categoryId": categoryId, "location": "Tampines"}


def countIDPs():
    conn = getConnection()
    total = conn.execute("SELECT COUNT(*) FROM idp").fetchone()[0]
    conn.close()
    return total


# ---------- AddCurrentIDPController.addCurrentIDP() ----------

def test_ut20_1_addCurrentIDP_valid():
    designerId = createDesigner20()
    categoryId = createCategory()
    assert AddCurrentIDPController().addCurrentIDP(designerId, idpData(categoryId)) is True
    idp = IDP().getIDPsInCategory(categoryId)[0]
    assert idp.designerId == designerId
    assert idp.title == "Tampines HDB kitchen"
    assert idp.projectType == "Current"
    assert idp.status == "Active"


def test_ut20_2_addCurrentIDP_adminRejected():
    categoryId = createCategory()
    assert AddCurrentIDPController().addCurrentIDP(1, idpData(categoryId)) is False
    assert countIDPs() == 0


def test_ut20_3_addCurrentIDP_unknownAccount():
    categoryId = createCategory()
    assert AddCurrentIDPController().addCurrentIDP(9999, idpData(categoryId)) is False


def test_ut20_4_addCurrentIDP_suspendedDesigner():
    designerId = createDesigner20()
    categoryId = createCategory()
    conn = getConnection()
    conn.execute("UPDATE user_account SET status = 'Suspended' WHERE userId = ?", (designerId,))
    conn.commit()
    conn.close()
    assert AddCurrentIDPController().addCurrentIDP(designerId, idpData(categoryId)) is False


def test_ut20_5_addCurrentIDP_invalidDataRejected():
    designerId = createDesigner20()
    data = idpData(createCategory())
    data["title"] = ""
    assert AddCurrentIDPController().addCurrentIDP(designerId, data) is False
    assert countIDPs() == 0


# ---------- AddCurrentIDPController.getFieldErrors() ----------

def test_ut20_6_getFieldErrors_valid():
    assert AddCurrentIDPController().getFieldErrors(idpData(createCategory())) == {}


def test_ut20_7_getFieldErrors_requiredFields():
    data = idpData(createCategory())
    data["title"] = " "
    data["description"] = ""
    errors = AddCurrentIDPController().getFieldErrors(data)
    assert errors["title"] == "This field is required"
    assert errors["description"] == "This field is required"


def test_ut20_8_getFieldErrors_titleTooShort():
    data = idpData(createCategory())
    data["title"] = "Ab"
    assert AddCurrentIDPController().getFieldErrors(data)["title"] == "Title must be 3-100 characters"


def test_ut20_9_getFieldErrors_tooLong():
    data = idpData(createCategory())
    data["title"] = "x" * 101
    data["location"] = "x" * 201
    errors = AddCurrentIDPController().getFieldErrors(data)
    assert errors["title"] == "Maximum 100 characters"
    assert errors["location"] == "Maximum 200 characters"


def test_ut20_10_getFieldErrors_noCategoryChosen():
    data = idpData(createCategory())
    data["categoryId"] = None
    assert AddCurrentIDPController().getFieldErrors(data)["categoryId"] == "Choose an available category"


def test_ut20_11_getFieldErrors_unknownCategory():
    data = idpData(createCategory())
    data["categoryId"] = 9999
    assert "categoryId" in AddCurrentIDPController().getFieldErrors(data)


def test_ut20_12_getFieldErrors_locationOptional():
    data = idpData(createCategory())
    data["location"] = ""
    assert AddCurrentIDPController().getFieldErrors(data) == {}


# ---------- AddCurrentIDPController.getActiveIDPCategories() / canAddCurrentIDP() ----------

def test_ut20_13_getActiveIDPCategories_sortedByName():
    createCategory("Kitchen")
    createCategory("Bedroom")
    names = [c.categoryName for c in AddCurrentIDPController().getActiveIDPCategories()]
    assert names == ["Bedroom", "Kitchen"]


def test_ut20_14_canAddCurrentIDP_onlyDesigner():
    designerId = createDesigner20()
    control = AddCurrentIDPController()
    assert control.canAddCurrentIDP(designerId) is True
    assert control.canAddCurrentIDP(1) is False


def test_ut20_15_validateInput_setsFieldErrors():
    page = AddCurrentIDPPage()
    data = idpData(createCategory())
    data["title"] = ""
    assert page.validateInput(data) is False
    assert "title" in page.fieldErrors


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
    response = client.post("/designer/idps/add", data=idpData(categoryId), follow_redirects=True)
    assert b"Current IDP added successfully" in response.data
    assert countIDPs() == 1


def test_ut20_20_submit_invalid_showsErrorsAndKeepsInput():
    createDesigner20()
    categoryId = createCategory()
    client = app.test_client()
    loginAsDesigner20(client)
    data = idpData(categoryId)
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
    data = idpData(categoryId)
    data["designerId"] = 1          # a forged owner field must be ignored
    client.post("/designer/idps/add", data=data)
    assert IDP().getIDPsInCategory(categoryId)[0].designerId == designerId


def test_ut20_22_addPage_notLoggedIn_redirects():
    response = app.test_client().get("/designer/idps/add")
    assert response.headers["Location"].endswith("/designer/login")


def test_ut20_23_addPage_managerForbidden():
    UserAccount().createUserAccount("manager20", "Manager@123", "Daniel Tan", "", "", 4)
    categoryId = createCategory()
    client = app.test_client()
    client.post("/manager/login", data={"username": "manager20", "password": "Manager@123"})
    assert client.get("/designer/idps/add").status_code == 403
    assert client.post("/designer/idps/add", data=idpData(categoryId)).status_code == 403
    assert countIDPs() == 0


def test_ut20_24_addedIDP_appearsInManagerCategoryView():
    # US20 + US42 working together: the manager sees the new IDP under its category
    createDesigner20()
    categoryId = createCategory()
    client = app.test_client()
    loginAsDesigner20(client)
    client.post("/designer/idps/add", data=idpData(categoryId))
    UserAccount().createUserAccount("manager20", "Manager@123", "Daniel Tan", "", "", 4)
    managerClient = app.test_client()
    managerClient.post("/manager/login", data={"username": "manager20", "password": "Manager@123"})
    response = managerClient.get("/manager/categories/" + str(categoryId))
    assert b"Tampines HDB kitchen" in response.data
