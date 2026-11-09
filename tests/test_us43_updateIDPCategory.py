# Unit tests for US43 Update IDP category.
# conftest.py creates a fresh database for every test.
# Manager tests add manager43 / Manager@123 (Platform Manager, profile 4).

from app import app
from entity.userAccount import UserAccount
from entity.idpCategory import IDPCategory
from control.updateIDPCategoryController import UpdateIDPCategoryController
from control.suspendIDPCategoryController import SuspendIDPCategoryController
from boundary.updateIDPCategoryPage import UpdateIDPCategoryPage, MSG_CANNOT_UPDATE


def createManager43():
    UserAccount().createUserAccount(
        UserAccount(username="manager43", password="Manager@123", fullName="Daniel Tan", email="manager43@archss.com", phone="", profileId=4))


def loginAsManager43(client):
    return client.post("/manager/login", data={"username": "manager43", "password": "Manager@123"})


def makeCategory(categoryId, categoryName, description=""):
    # update takes an IDPCategory object now, not three values
    return IDPCategory(categoryId=categoryId, categoryName=categoryName, description=description)


def createCategory(name, description=""):
    IDPCategory().createIDPCategory(IDPCategory(categoryName=name, description=description))
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
    assert UpdateIDPCategoryController().updateIDPCategory(makeCategory(categoryId, "Kitchens", "New text")) is True
    category = IDPCategory().getIDPCategory(categoryId)
    assert category.categoryName == "Kitchens"
    assert category.description == "New text"


def test_ut43_4_updateIDPCategory_nameTaken():
    createCategory("Kitchen")
    bedroom = createCategory("Bedroom")
    assert UpdateIDPCategoryController().updateIDPCategory(makeCategory(bedroom, "KITCHEN", "")) is False
    assert IDPCategory().getIDPCategory(bedroom).categoryName == "Bedroom"


def test_ut43_5_updateIDPCategory_notFound():
    assert UpdateIDPCategoryController().updateIDPCategory(makeCategory(9999, "Kitchen", "")) is False




def test_ut43_7_updateIDPCategory_keepSameName():
    categoryId = createCategory("Kitchen", "Old text")
    assert UpdateIDPCategoryController().updateIDPCategory(makeCategory(categoryId, "Kitchen", "New text")) is True


def test_ut43_8_updateIDPCategory_suspendedCannotBeUpdated():
    # only an Active category can be updated - the entity changes nothing for a Suspended one
    categoryId = createCategory("Kitchen")
    SuspendIDPCategoryController().suspendIDPCategory(categoryId)
    assert UpdateIDPCategoryController().updateIDPCategory(makeCategory(categoryId, "Kitchens", "")) is False
    category = IDPCategory().getIDPCategory(categoryId)
    assert category.categoryName == "Kitchen"
    assert category.status == "Suspended"


# ---------- UpdateIDPCategoryPage ----------

def test_ut43_9_validateInput_sameRulesAsCreate():
    page = UpdateIDPCategoryPage()
    assert page.validateInput(makeCategory(1, "Kitchen", "")) is True
    assert page.validateInput(makeCategory(1, "Ki", "")) is False
    assert page.validateInput(makeCategory(1, "Kitchen", "x" * 501)) is False


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
    assert MSG_CANNOT_UPDATE.encode() in response.data
    assert b'value="kitchen"' in response.data
    assert b"Typed text" in response.data
    assert IDPCategory().getIDPCategory(bedroom).categoryName == "Bedroom"


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


def test_ut43_6_submit_emptyName_showsFieldError():
    # an empty name is now caught by the page, so the controller is never called
    createManager43()
    categoryId = createCategory("Kitchen")
    client = app.test_client()
    loginAsManager43(client)
    response = client.post("/manager/categories/" + str(categoryId) + "/update",
                           data={"categoryName": "  ", "description": ""})
    assert b"Category name must be 3-50 characters" in response.data
    assert IDPCategory().getIDPCategory(categoryId).categoryName == "Kitchen"


def test_ut43_15_updatePage_notLoggedIn_redirects():
    categoryId = createCategory("Kitchen")
    url = "/manager/categories/" + str(categoryId) + "/update"
    response = app.test_client().post(url, data={"categoryName": "Hacked", "description": ""})
    assert response.headers["Location"].endswith("/manager/login")
    assert IDPCategory().getIDPCategory(categoryId).categoryName == "Kitchen"


def test_ut43_16_submit_suspendedCategory_showsCannotUpdate():
    createManager43()
    categoryId = createCategory("Kitchen", "Old text")
    SuspendIDPCategoryController().suspendIDPCategory(categoryId)
    client = app.test_client()
    loginAsManager43(client)
    response = client.post("/manager/categories/" + str(categoryId) + "/update",
                           data={"categoryName": "Kitchens", "description": "New text"})
    assert MSG_CANNOT_UPDATE.encode() in response.data
    # the re-shown form has no status row
    assert b"Status:" not in response.data
    category = IDPCategory().getIDPCategory(categoryId)
    assert (category.categoryName, category.description, category.status) == ("Kitchen", "Old text", "Suspended")


def test_ut43_17_detailsPage_suspendedHasNoUpdateButton():
    createManager43()
    categoryId = createCategory("Kitchen")
    client = app.test_client()
    loginAsManager43(client)
    updateLink = ("/manager/categories/" + str(categoryId) + "/update").encode()
    assert updateLink in client.get("/manager/categories/" + str(categoryId)).data
    SuspendIDPCategoryController().suspendIDPCategory(categoryId)
    assert updateLink not in client.get("/manager/categories/" + str(categoryId)).data


# ---------- system tests (TC) ----------

def test_tc43_3_nameUsedByAnotherCategory():
    createManager43()
    createCategory("Kitchen")
    bedroom = createCategory("Bedroom")
    client = app.test_client()
    loginAsManager43(client)
    response = client.post("/manager/categories/" + str(bedroom) + "/update",
                           data={"categoryName": "kitchen", "description": ""})
    assert b"This IDP category could not be updated - the name is already used or the category is suspended" in response.data
    assert IDPCategory().getIDPCategory(bedroom).categoryName == "Bedroom"


def test_tc43_5_suspendedCategoryCannotBeUpdated():
    createManager43()
    categoryId = createCategory("Kitchen")
    SuspendIDPCategoryController().suspendIDPCategory(categoryId)
    client = app.test_client()
    loginAsManager43(client)
    url = "/manager/categories/" + str(categoryId) + "/update"
    assert client.get(url).status_code == 200
    response = client.post(url, data={"categoryName": "Kitchens", "description": ""})
    assert b"This IDP category could not be updated - the name is already used or the category is suspended" in response.data
    category = IDPCategory().getIDPCategory(categoryId)
    assert category.categoryName == "Kitchen"
    assert category.status == "Suspended"


def test_tc43_8_noUpdateButtonOnSuspendedCategory():
    createManager43()
    categoryId = createCategory("Kitchen")
    SuspendIDPCategoryController().suspendIDPCategory(categoryId)
    client = app.test_client()
    loginAsManager43(client)
    response = client.get("/manager/categories/" + str(categoryId))
    assert b"Suspended" in response.data
    assert b">Update</a>" not in response.data
