# Unit tests for US41 Create IDP category.
# conftest.py creates a fresh database for every test.
# Manager tests add manager41 / Manager@123 (Platform Manager, profile 4).

from app import app
from database.db import getConnection
from entity.userAccount import UserAccount
from entity.idpCategory import IDPCategory
from control.createIDPCategoryController import CreateIDPCategoryController
from boundary.createIDPCategoryPage import CreateIDPCategoryPage


def createManager41():
    UserAccount().createUserAccount(
        "manager41", "Manager@123", "Daniel Tan", "manager41@archss.com", "", 4)
    return UserAccount().verifyCredentials("manager41", "Manager@123").userId


def loginAsManager41(client):
    return client.post("/manager/login", data={"username": "manager41", "password": "Manager@123"})


def countCategories():
    conn = getConnection()
    total = conn.execute("SELECT COUNT(*) FROM idp_category").fetchone()[0]
    conn.close()
    return total


# ---------- IDPCategory.createIDPCategory() / isCategoryNameTaken() ----------

def test_ut41_1_createIDPCategory_entityStartsActive():
    assert IDPCategory().createIDPCategory("Kitchen", "Kitchen renovations") is True
    category = IDPCategory().searchIDPCategories("Kitchen")[0]
    assert category.categoryName == "Kitchen"
    assert category.description == "Kitchen renovations"
    assert category.status == "Active"


def test_ut41_2_isCategoryNameTaken_newName():
    assert IDPCategory().isCategoryNameTaken("Kitchen") is False


def test_ut41_3_isCategoryNameTaken_existingName():
    IDPCategory().createIDPCategory("Kitchen", "")
    assert IDPCategory().isCategoryNameTaken("Kitchen") is True


def test_ut41_4_isCategoryNameTaken_ignoresCaseAndSpaces():
    IDPCategory().createIDPCategory("Kitchen", "")
    assert IDPCategory().isCategoryNameTaken("  kITCHEN ") is True


# ---------- CreateIDPCategoryController.createIDPCategory() ----------

def test_ut41_5_createIDPCategory_valid():
    assert CreateIDPCategoryController().createIDPCategory("Living Room", "Lounges") is True
    assert countCategories() == 1


def test_ut41_6_createIDPCategory_nameTaken():
    control = CreateIDPCategoryController()
    assert control.createIDPCategory("Living Room", "") is True
    assert control.createIDPCategory("living room", "Another one") is False
    assert countCategories() == 1


def test_ut41_7_createIDPCategory_emptyName():
    assert CreateIDPCategoryController().createIDPCategory("   ", "Lounges") is False
    assert countCategories() == 0


def test_ut41_8_createIDPCategory_descriptionOptional():
    assert CreateIDPCategoryController().createIDPCategory("Bathroom", "") is True


def test_ut41_19_canCreateIDPCategory_onlyManager():
    managerId = createManager41()
    control = CreateIDPCategoryController()
    assert control.canCreateIDPCategory(managerId) is True
    assert control.canCreateIDPCategory(1) is False      # admin01
    assert control.canCreateIDPCategory(9999) is False


# ---------- CreateIDPCategoryPage.validateInput() ----------

def test_ut41_9_validateInput_valid():
    assert CreateIDPCategoryPage().validateInput("Kitchen", "Kitchen renovations") is True


def test_ut41_10_validateInput_nameTooShort():
    page = CreateIDPCategoryPage()
    assert page.validateInput("Ki", "") is False
    assert page.fieldErrors["categoryName"] == "Category name must be 3-50 characters"


def test_ut41_11_validateInput_nameTooLong():
    page = CreateIDPCategoryPage()
    assert page.validateInput("K" * 51, "") is False
    assert "categoryName" in page.fieldErrors


def test_ut41_12_validateInput_descriptionTooLong():
    page = CreateIDPCategoryPage()
    assert page.validateInput("Kitchen", "x" * 501) is False
    assert page.fieldErrors["description"] == "Description must be 500 characters or fewer"


# ---------- CreateIDPCategoryPage via the /manager/categories/create route ----------

def test_ut41_13_createPage_notLoggedIn_redirectsToManagerLogin():
    response = app.test_client().get("/manager/categories/create")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/manager/login")


def test_ut41_14_createPage_adminForbidden():
    client = app.test_client()
    client.post("/login", data={"username": "admin01", "password": "Admin@123"})
    assert client.get("/manager/categories/create").status_code == 403
    assert client.post("/manager/categories/create", data={"categoryName": "Kitchen"}).status_code == 403
    assert countCategories() == 0


def test_ut41_15_createPage_showsForm():
    createManager41()
    client = app.test_client()
    loginAsManager41(client)
    response = client.get("/manager/categories/create")
    assert response.status_code == 200
    assert b'name="categoryName"' in response.data
    assert b'name="description"' in response.data


def test_ut41_16_submit_valid_redirectsToListWithMessage():
    createManager41()
    client = app.test_client()
    loginAsManager41(client)
    response = client.post("/manager/categories/create",
                           data={"categoryName": "Kitchen", "description": "Kitchen renovations"},
                           follow_redirects=True)
    assert b"IDP category created successfully" in response.data
    assert b"Kitchen" in response.data
    assert countCategories() == 1


def test_ut41_17_submit_nameTaken_showsErrorAndKeepsInput():
    createManager41()
    IDPCategory().createIDPCategory("Kitchen", "")
    client = app.test_client()
    loginAsManager41(client)
    response = client.post("/manager/categories/create",
                           data={"categoryName": "kitchen", "description": "Typed text"})
    assert b"An IDP category with this name already exists" in response.data
    assert b"Typed text" in response.data
    assert countCategories() == 1


def test_ut41_18_submit_invalid_showsFieldErrors():
    createManager41()
    client = app.test_client()
    loginAsManager41(client)
    response = client.post("/manager/categories/create", data={"categoryName": "K", "description": ""})
    assert b"Please fix the highlighted fields" in response.data
    assert b"Category name must be 3-50 characters" in response.data
    assert countCategories() == 0
