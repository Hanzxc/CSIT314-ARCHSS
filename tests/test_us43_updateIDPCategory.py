# Unit tests for US43 Update IDP category.
# conftest.py creates a fresh database for every test.
# Manager tests add manager43 / Manager@123 (Platform Manager, profile 4).

from app import app
from entity.userAccount import UserAccount
from entity.idpCategory import IDPCategory
from control.updateIDPCategoryController import UpdateIDPCategoryController
from control.suspendIDPCategoryController import SuspendIDPCategoryController
from boundary.updateIDPCategoryPage import UpdateIDPCategoryPage


def createManager43():
    UserAccount().createUserAccount(
        "manager43", "Manager@123", "Daniel Tan", "manager43@archss.com", "", 4)


def loginAsManager43(client):
    return client.post("/manager/login", data={"username": "manager43", "password": "Manager@123"})


def createCategory(name, description=""):
    IDPCategory().createIDPCategory(name, description)
    return IDPCategory().searchIDPCategories(name)[0].categoryId


# ---------- IDPCategory.isCategoryNameTaken(name, categoryId) ----------

def test_ut43_1_isCategoryNameTaken_ownNameNotTaken():
    categoryId = createCategory("Kitchen")
    assert IDPCategory().isCategoryNameTaken("Kitchen", categoryId) is False


def test_ut43_2_isCategoryNameTaken_otherCategorysName():
    createCategory("Kitchen")
    bedroom = createCategory("Bedroom")
    assert IDPCategory().isCategoryNameTaken("kitchen", bedroom) is True


# ---------- UpdateIDPCategoryController.updateIDPCategory() ----------

def test_ut43_3_updateIDPCategory_valid():
    categoryId = createCategory("Kitchen", "Old text")
    assert UpdateIDPCategoryController().updateIDPCategory(categoryId, "Kitchens", "New text") is True
    category = IDPCategory().getIDPCategory(categoryId)
    assert category.categoryName == "Kitchens"
    assert category.description == "New text"


def test_ut43_4_updateIDPCategory_nameTaken():
    createCategory("Kitchen")
    bedroom = createCategory("Bedroom")
    assert UpdateIDPCategoryController().updateIDPCategory(bedroom, "KITCHEN", "") is False
    assert IDPCategory().getIDPCategory(bedroom).categoryName == "Bedroom"


def test_ut43_5_updateIDPCategory_notFound():
    assert UpdateIDPCategoryController().updateIDPCategory(9999, "Kitchen", "") is False


def test_ut43_6_updateIDPCategory_emptyName():
    categoryId = createCategory("Kitchen")
    assert UpdateIDPCategoryController().updateIDPCategory(categoryId, "  ", "") is False


def test_ut43_7_updateIDPCategory_keepSameName():
    categoryId = createCategory("Kitchen", "Old text")
    assert UpdateIDPCategoryController().updateIDPCategory(categoryId, "Kitchen", "New text") is True


def test_ut43_8_updateIDPCategory_doesNotUnsuspend():
    categoryId = createCategory("Kitchen")
    SuspendIDPCategoryController().suspendIDPCategory(categoryId)
    assert UpdateIDPCategoryController().updateIDPCategory(categoryId, "Kitchens", "") is True
    assert IDPCategory().getIDPCategory(categoryId).status == "Suspended"


# ---------- UpdateIDPCategoryPage ----------

def test_ut43_9_validateInput_sameRulesAsCreate():
    page = UpdateIDPCategoryPage()
    assert page.validateInput("Kitchen", "") is True
    assert page.validateInput("Ki", "") is False
    assert page.validateInput("Kitchen", "x" * 501) is False


def test_ut43_10_updatePage_showsFilledForm():
    createManager43()
    categoryId = createCategory("Kitchen", "Kitchen renovations")
    client = app.test_client()
    loginAsManager43(client)
    response = client.get("/manager/categories/" + str(categoryId) + "/update")
    assert response.status_code == 200
    assert b'value="Kitchen"' in response.data
    assert b"Kitchen renovations" in response.data


def test_ut43_11_submit_valid_redirectsToDetailsWithMessage():
    createManager43()
    categoryId = createCategory("Kitchen")
    client = app.test_client()
    loginAsManager43(client)
    response = client.post("/manager/categories/" + str(categoryId) + "/update",
                           data={"categoryName": "Kitchens", "description": "All kitchens"},
                           follow_redirects=True)
    assert b"IDP category updated successfully" in response.data
    assert b"Kitchens" in response.data
    assert b"All kitchens" in response.data


def test_ut43_12_submit_nameTaken_showsErrorAndKeepsInput():
    createManager43()
    createCategory("Kitchen")
    bedroom = createCategory("Bedroom")
    client = app.test_client()
    loginAsManager43(client)
    response = client.post("/manager/categories/" + str(bedroom) + "/update",
                           data={"categoryName": "kitchen", "description": "Typed text"})
    assert b"An IDP category with this name already exists" in response.data
    assert b"Typed text" in response.data


def test_ut43_13_submit_invalid_showsFieldErrors():
    createManager43()
    categoryId = createCategory("Kitchen")
    client = app.test_client()
    loginAsManager43(client)
    response = client.post("/manager/categories/" + str(categoryId) + "/update",
                           data={"categoryName": "K", "description": ""})
    assert b"Please fix the highlighted fields" in response.data
    assert IDPCategory().getIDPCategory(categoryId).categoryName == "Kitchen"


def test_ut43_14_updatePage_notFound():
    createManager43()
    client = app.test_client()
    loginAsManager43(client)
    response = client.get("/manager/categories/9999/update")
    assert b"IDP category not found" in response.data


def test_ut43_15_updatePage_adminForbidden():
    categoryId = createCategory("Kitchen")
    client = app.test_client()
    client.post("/login", data={"username": "admin01", "password": "Admin@123"})
    url = "/manager/categories/" + str(categoryId) + "/update"
    assert client.get(url).status_code == 403
    assert client.post(url, data={"categoryName": "Hacked", "description": ""}).status_code == 403
    assert IDPCategory().getIDPCategory(categoryId).categoryName == "Kitchen"
