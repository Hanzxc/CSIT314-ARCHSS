# Unit tests for US45 Search IDP categories.
# conftest.py creates a fresh database for every test.
# Manager tests add manager45 / Manager@123 (Platform Manager, profile 4).

from app import app
from entity.userAccount import UserAccount
from entity.idpCategory import IDPCategory
from control.searchIDPCategoryController import SearchIDPCategoryController
from control.suspendIDPCategoryController import SuspendIDPCategoryController


def createManager45():
    UserAccount().createUserAccount(
        "manager45", "Manager@123", "Daniel Tan", "manager45@archss.com", "", 4)


def loginAsManager45(client):
    return client.post("/manager/login", data={"username": "manager45", "password": "Manager@123"})


def createSampleCategories():
    IDPCategory().createIDPCategory("Kitchen", "Cooking and dining spaces")
    IDPCategory().createIDPCategory("Bedroom", "Calm sleeping spaces")
    IDPCategory().createIDPCategory("Office", "Work spaces with a kitchenette")


def names(categories):
    return [category.categoryName for category in categories]


# ---------- IDPCategory.searchIDPCategories() ----------

def test_ut45_1_search_byName():
    createSampleCategories()
    assert names(IDPCategory().searchIDPCategories("Bedroom")) == ["Bedroom"]


def test_ut45_2_search_byDescription():
    createSampleCategories()
    assert names(IDPCategory().searchIDPCategories("sleeping")) == ["Bedroom"]


def test_ut45_3_search_ignoresCase():
    createSampleCategories()
    assert names(IDPCategory().searchIDPCategories("BEDROOM")) == ["Bedroom"]


def test_ut45_4_search_partialMatchesNameAndDescription():
    createSampleCategories()
    assert names(IDPCategory().searchIDPCategories("kitchen")) == ["Kitchen", "Office"]


def test_ut45_5_search_emptyKeywordReturnsAll():
    createSampleCategories()
    assert names(IDPCategory().searchIDPCategories("")) == ["Kitchen", "Bedroom", "Office"]


def test_ut45_6_search_includesSuspended():
    createSampleCategories()
    categoryId = IDPCategory().searchIDPCategories("Bedroom")[0].categoryId
    SuspendIDPCategoryController().suspendIDPCategory(categoryId)
    result = IDPCategory().searchIDPCategories("Bedroom")
    assert result[0].status == "Suspended"


# ---------- SearchIDPCategoryController.searchIDPCategories() ----------

def test_ut45_7_control_trimsKeyword():
    createSampleCategories()
    assert names(SearchIDPCategoryController().searchIDPCategories("  Bedroom ")) == ["Bedroom"]


def test_ut45_8_control_noneKeywordReturnsAll():
    createSampleCategories()
    assert len(SearchIDPCategoryController().searchIDPCategories(None)) == 3


def test_ut45_9_control_noMatches():
    createSampleCategories()
    assert SearchIDPCategoryController().searchIDPCategories("garage") == []


# ---------- SearchIDPCategoryPage via the /manager/categories route ----------

def test_ut45_10_listPage_showsAll():
    createManager45()
    createSampleCategories()
    client = app.test_client()
    loginAsManager45(client)
    response = client.get("/manager/categories")
    assert response.status_code == 200
    for name in (b"Kitchen", b"Bedroom", b"Office"):
        assert name in response.data


def test_ut45_11_searchPage_showsMatchesAndKeepsKeyword():
    createManager45()
    createSampleCategories()
    client = app.test_client()
    loginAsManager45(client)
    response = client.get("/manager/categories?keyword=sleeping")
    assert b"Bedroom" in response.data
    assert b"Cooking and dining" not in response.data
    assert b'value="sleeping"' in response.data


def test_ut45_12_searchPage_noResultsMessage():
    createManager45()
    createSampleCategories()
    client = app.test_client()
    loginAsManager45(client)
    response = client.get("/manager/categories?keyword=garage")
    assert b"No IDP categories found" in response.data


def test_ut45_13_searchPage_notLoggedIn_redirects():
    response = app.test_client().get("/manager/categories?keyword=kitchen")
    assert response.headers["Location"].endswith("/manager/login")


def test_ut45_14_searchPage_adminForbidden():
    client = app.test_client()
    client.post("/login", data={"username": "admin01", "password": "Admin@123"})
    assert client.get("/manager/categories").status_code == 403


def test_ut45_15_dashboard_linksToCategories():
    createManager45()
    client = app.test_client()
    loginAsManager45(client)
    response = client.get("/manager/dashboard")
    assert b'href="/manager/categories"' in response.data
    assert b"IDP Categories" in response.data
