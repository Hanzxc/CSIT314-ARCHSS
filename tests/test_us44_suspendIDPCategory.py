# Unit tests for US44 Suspend IDP category.
# conftest.py creates a fresh database for every test.
# Manager tests add manager44 / Manager@123 (Platform Manager, profile 4).
# "Users can no longer see or select it" is checked against the US20 category drop-down.

from app import app
from entity.userAccount import UserAccount
from entity.idp import IDP
from entity.idpCategory import IDPCategory
from control.suspendIDPCategoryController import SuspendIDPCategoryController
from control.addCurrentIDPController import AddCurrentIDPController
from boundary.addCurrentIDPPage import AddCurrentIDPPage


def createManager44():
    UserAccount().createUserAccount(
        UserAccount(username="manager44", password="Manager@123", fullName="Daniel Tan", email="manager44@archss.com", phone="", profileId=4))


def createDesigner44():
    UserAccount().createUserAccount(
        UserAccount(username="designer44", password="Design@123", fullName="Tengku Uda Designer", email="designer44@archss.com", phone="", profileId=2))
    return UserAccount().verifyCredentials("designer44", "Design@123").userId


def loginAsManager44(client):
    return client.post("/manager/login", data={"username": "manager44", "password": "Manager@123"})


def createCategory(name, description=""):
    IDPCategory().createIDPCategory(IDPCategory(categoryName=name, description=description))
    return IDPCategory().searchIDPCategories(name)[0].categoryId


def makeIDP(designerId, categoryId):
    return IDP(designerId=designerId, categoryId=categoryId, title="Tampines HDB kitchen",
               description="Work in progress.")


# ---------- SuspendIDPCategoryController.suspendIDPCategory() ----------

def test_ut44_1_suspendIDPCategory_active():
    categoryId = createCategory("Kitchen")
    assert SuspendIDPCategoryController().suspendIDPCategory(categoryId) is True
    assert IDPCategory().getIDPCategory(categoryId).status == "Suspended"


def test_ut44_2_suspendIDPCategory_alreadySuspended():
    categoryId = createCategory("Kitchen")
    SuspendIDPCategoryController().suspendIDPCategory(categoryId)
    assert SuspendIDPCategoryController().suspendIDPCategory(categoryId) is False


def test_ut44_3_suspendIDPCategory_notFound():
    assert SuspendIDPCategoryController().suspendIDPCategory(9999) is False


def test_ut44_4_suspendIDPCategory_keepsIDPs():
    designerId = createDesigner44()
    categoryId = createCategory("Kitchen")
    AddCurrentIDPController().addCurrentIDP(makeIDP(designerId, categoryId))
    SuspendIDPCategoryController().suspendIDPCategory(categoryId)
    assert len(IDPCategory().getIDPsInCategory(categoryId)) == 1


# ---------- IDPCategory.isActive() / suspendIDPCategory() ----------

def test_ut44_5_isActive():
    assert IDPCategory(status="Active").isActive() is True
    assert IDPCategory(status="Suspended").isActive() is False


def test_ut44_6_entitySuspend_onlyChangesActiveRow():
    categoryId = createCategory("Kitchen")
    assert IDPCategory().suspendIDPCategory(categoryId) is True
    assert IDPCategory().suspendIDPCategory(categoryId) is False


# ---------- users can no longer see or select it (US20 integration) ----------

def test_ut44_7_suspended_notOfferedInAddIDPDropDown():
    kitchen = createCategory("Kitchen")
    createCategory("Bedroom")
    SuspendIDPCategoryController().suspendIDPCategory(kitchen)
    names = [c.categoryName for c in AddCurrentIDPPage().getAvailableCategories()]
    assert names == ["Bedroom"]


def test_ut44_8_suspended_cannotBeSelectedForNewIDP():
    designerId = createDesigner44()
    categoryId = createCategory("Kitchen")
    SuspendIDPCategoryController().suspendIDPCategory(categoryId)
    assert AddCurrentIDPController().addCurrentIDP(makeIDP(designerId, categoryId)) is False
    assert IDPCategory().getIDPsInCategory(categoryId) == []


def test_ut44_9_suspended_notShownOnDesignerForm():
    createDesigner44()
    categoryId = createCategory("Kitchen")
    createCategory("Bedroom")
    SuspendIDPCategoryController().suspendIDPCategory(categoryId)
    client = app.test_client()
    client.post("/designer/login", data={"username": "designer44", "password": "Design@123"})
    response = client.get("/designer/idps/add")
    assert b"Bedroom" in response.data
    assert b"Kitchen" not in response.data


# ---------- SuspendIDPCategoryPage via the /manager/categories/<id>/suspend route ----------

def test_ut44_10_clickSuspend_showsConfirmation():
    createManager44()
    categoryId = createCategory("Kitchen")
    client = app.test_client()
    loginAsManager44(client)
    response = client.get("/manager/categories/" + str(categoryId) + "/suspend")
    assert b"Suspend IDP category?" in response.data
    assert IDPCategory().getIDPCategory(categoryId).status == "Active"


def test_ut44_11_confirmSuspend_showsSuccess():
    createManager44()
    categoryId = createCategory("Kitchen")
    client = app.test_client()
    loginAsManager44(client)
    response = client.post("/manager/categories/" + str(categoryId) + "/suspend",
                           data={"choice": "ok"}, follow_redirects=True)
    assert b"IDP category suspended successfully" in response.data
    assert b"Suspended" in response.data
    assert IDPCategory().getIDPCategory(categoryId).status == "Suspended"


def test_ut44_12_cancelSuspend_noChange():
    createManager44()
    categoryId = createCategory("Kitchen")
    client = app.test_client()
    loginAsManager44(client)
    response = client.post("/manager/categories/" + str(categoryId) + "/suspend",
                           data={"choice": "cancel"})
    assert response.headers["Location"].endswith("/manager/categories/" + str(categoryId))
    assert IDPCategory().getIDPCategory(categoryId).status == "Active"


def test_ut44_13_confirmSuspend_alreadySuspended_showsError():
    createManager44()
    categoryId = createCategory("Kitchen")
    SuspendIDPCategoryController().suspendIDPCategory(categoryId)
    client = app.test_client()
    loginAsManager44(client)
    response = client.post("/manager/categories/" + str(categoryId) + "/suspend",
                           data={"choice": "ok"}, follow_redirects=True)
    assert b"This IDP category cannot be suspended" in response.data


def test_ut44_14_suspendedCategory_hasNoSuspendButton():
    createManager44()
    categoryId = createCategory("Kitchen")
    SuspendIDPCategoryController().suspendIDPCategory(categoryId)
    client = app.test_client()
    loginAsManager44(client)
    response = client.get("/manager/categories/" + str(categoryId))
    assert ("/manager/categories/" + str(categoryId) + "/suspend").encode() not in response.data


def test_ut44_15_suspend_notLoggedIn_redirects():
    categoryId = createCategory("Kitchen")
    url = "/manager/categories/" + str(categoryId) + "/suspend"
    response = app.test_client().post(url, data={"choice": "ok"})
    assert response.headers["Location"].endswith("/manager/login")
    assert IDPCategory().getIDPCategory(categoryId).status == "Active"


def test_ut44_16_clickSuspend_notFound():
    # US42's controller finds no category, so no box - just the error
    createManager44()
    client = app.test_client()
    loginAsManager44(client)
    response = client.get("/manager/categories/9999/suspend", follow_redirects=True)
    assert b"This IDP category cannot be suspended" in response.data
    assert b"Suspend IDP category?" not in response.data


def test_ut44_17_clickSuspend_alreadySuspended_boxThenEntitySaysNo():
    # the page doesn't call isActive() first - the box shows, and OK gets False from the entity
    createManager44()
    categoryId = createCategory("Kitchen")
    SuspendIDPCategoryController().suspendIDPCategory(categoryId)
    client = app.test_client()
    loginAsManager44(client)
    url = "/manager/categories/" + str(categoryId) + "/suspend"
    assert b"Suspend IDP category?" in client.get(url).data
    response = client.post(url, data={"choice": "ok"}, follow_redirects=True)
    assert b"This IDP category cannot be suspended" in response.data
    assert IDPCategory().getIDPCategory(categoryId).status == "Suspended"


# ---------- system tests (TC) ----------

def test_tc44_1_suspendCategory():
    createManager44()
    categoryId = createCategory("Kitchen")
    client = app.test_client()
    loginAsManager44(client)
    url = "/manager/categories/" + str(categoryId) + "/suspend"
    assert b"Suspend IDP category?" in client.get(url).data
    response = client.post(url, data={"choice": "ok"}, follow_redirects=True)
    assert b"IDP category suspended successfully" in response.data
    assert b'<span class="badge suspended">Suspended</span>' in response.data
    assert url.encode() not in response.data
    assert ("/manager/categories/" + str(categoryId) + "/update").encode() not in response.data
