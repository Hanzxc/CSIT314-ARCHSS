# Unit tests for US42 View IDP category (and the IDPs in it).
# conftest.py creates a fresh database for every test.
# Manager tests add manager42 / Manager@123 (Platform Manager, profile 4).
# IDPs are added through US20 by designer42 / Design@123 (Interior Designer, profile 2).

from app import app
from entity.userAccount import UserAccount
from entity.idp import IDP
from entity.idpCategory import IDPCategory
from control.viewIDPCategoryController import ViewIDPCategoryController
from control.addCurrentIDPController import AddCurrentIDPController


def createManager42():
    UserAccount().createUserAccount(
        UserAccount(username="manager42", password="Manager@123", fullName="Daniel Tan", email="manager42@archss.com", phone="", profileId=4))
    return UserAccount().verifyCredentials("manager42", "Manager@123").userId


def createDesigner42():
    UserAccount().createUserAccount(
        UserAccount(username="designer42", password="Design@123", fullName="Tengku Uda Designer", email="designer42@archss.com", phone="", profileId=2))
    return UserAccount().verifyCredentials("designer42", "Design@123").userId


def loginAsManager42(client):
    return client.post("/manager/login", data={"username": "manager42", "password": "Manager@123"})


def createCategory(name, description=""):
    IDPCategory().createIDPCategory(IDPCategory(categoryName=name, description=description))
    return IDPCategory().searchIDPCategories(name)[0].categoryId


def addIDP(designerId, categoryId, title):
    return AddCurrentIDPController().addCurrentIDP(IDP(
        designerId=designerId, categoryId=categoryId, title=title,
        description="Work in progress.", location="Tampines"))


# ---------- IDPCategory.getIDPCategory() ----------

def test_ut42_1_getIDPCategory_exists():
    categoryId = createCategory("Kitchen", "Kitchen renovations")
    category = IDPCategory().getIDPCategory(categoryId)
    assert category.categoryName == "Kitchen"
    assert category.description == "Kitchen renovations"


def test_ut42_2_getIDPCategory_notFound():
    assert IDPCategory().getIDPCategory(9999) is None


# ---------- IDPCategory.getIDPsInCategory() ----------

def test_ut42_3_getIDPsInCategory_onlyThatCategory():
    designerId = createDesigner42()
    kitchen = createCategory("Kitchen")
    bedroom = createCategory("Bedroom")
    addIDP(designerId, kitchen, "Tampines HDB kitchen")
    addIDP(designerId, bedroom, "Master bedroom refresh")
    idps = IDPCategory().getIDPsInCategory(kitchen)
    assert [idp.title for idp in idps] == ["Tampines HDB kitchen"]


def test_ut42_4_getIDPsInCategory_empty():
    assert IDPCategory().getIDPsInCategory(createCategory("Kitchen")) == []


# ---------- ViewIDPCategoryController ----------

def test_ut42_5_viewIDPCategory_exists():
    categoryId = createCategory("Kitchen")
    assert ViewIDPCategoryController().viewIDPCategory(categoryId).categoryName == "Kitchen"


def test_ut42_6_viewIDPCategory_notFound():
    assert ViewIDPCategoryController().viewIDPCategory(9999) is None


def test_ut42_7_getIDPsInCategory_passesThrough():
    designerId = createDesigner42()
    categoryId = createCategory("Kitchen")
    addIDP(designerId, categoryId, "Tampines HDB kitchen")
    idps = ViewIDPCategoryController().getIDPsInCategory(categoryId)
    assert len(idps) == 1
    assert idps[0].designerId == designerId




# ---------- ViewIDPCategoryPage via the /manager/categories/<id> route ----------

def test_ut42_9_viewPage_showsDetailsAndIDPs():
    createManager42()
    designerId = createDesigner42()
    categoryId = createCategory("Kitchen", "Kitchen renovations")
    addIDP(designerId, categoryId, "Tampines HDB kitchen")
    client = app.test_client()
    loginAsManager42(client)
    response = client.get("/manager/categories/" + str(categoryId))
    assert response.status_code == 200
    assert b"Kitchen renovations" in response.data
    assert b"Tampines HDB kitchen" in response.data
    assert b"Active" in response.data


def test_ut42_10_viewPage_noIDPsMessage():
    createManager42()
    categoryId = createCategory("Kitchen")
    client = app.test_client()
    loginAsManager42(client)
    response = client.get("/manager/categories/" + str(categoryId))
    assert b"No IDPs are in this category yet" in response.data


def test_ut42_11_viewPage_notFound():
    createManager42()
    client = app.test_client()
    loginAsManager42(client)
    response = client.get("/manager/categories/9999")
    assert b"IDP category not found" in response.data


def test_ut42_12_viewPage_listLinksToDetails():
    createManager42()
    categoryId = createCategory("Kitchen")
    client = app.test_client()
    loginAsManager42(client)
    response = client.get("/manager/categories")
    assert ("/manager/categories/" + str(categoryId)).encode() in response.data


def test_ut42_13_viewPage_notLoggedIn_redirects():
    categoryId = createCategory("Kitchen")
    response = app.test_client().get("/manager/categories/" + str(categoryId))
    assert response.headers["Location"].endswith("/manager/login")
