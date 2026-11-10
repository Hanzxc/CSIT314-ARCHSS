# Unit tests for US37 View IDP view statistics.
# conftest.py gives each test a fresh database with the default users (cust001 is the customer).
# Designer tests add designer37 / Design@123 (profile 2). Categories and IDPs are made per test.
# The helpers here are shared with the US38 and US46 - US48 tests.

from app import app
from database.db import getConnection
from entity.userAccount import UserAccount
from entity.idpCategory import IDPCategory
from entity.idpAnalytics import IDPAnalytics
from control.viewIDPViewStatisticsController import ViewIDPViewStatisticsController
from boundary.viewIDPViewStatisticsPage import MSG_NO_IDPS
from control.customerLoginController import REQUIRED_CUSTOMER_PERMISSIONS
from control.interiorDesignerLoginController import REQUIRED_DESIGNER_PERMISSIONS


def createDesigner(username="designer37"):
    UserAccount().createUserAccount(UserAccount(username=username, password="Design@123", fullName="Statistics Designer",
                                    email=username + "@archss.com", phone="", profileId=2))
    return UserAccount().verifyCredentials(username, "Design@123", REQUIRED_DESIGNER_PERMISSIONS).userId


def loginAsDesigner(client, username="designer37"):
    return client.post("/designer/login", data={"username": username, "password": "Design@123"})


def customerId():
    return UserAccount().verifyCredentials("cust001", "Cust@123", REQUIRED_CUSTOMER_PERMISSIONS).userId


def createCategory(name="Kitchen", status="Active"):
    IDPCategory().createIDPCategory(IDPCategory(categoryName=name))
    categoryId = IDPCategory().searchIDPCategories(name)[0].categoryId
    if status != "Active":
        execute("UPDATE idp_category SET status = ? WHERE categoryId = ?", (status, categoryId))
    return categoryId


def addIDP(designerId, categoryId, title, projectType="Current", status="Active"):
    return execute("INSERT INTO idp (designerId, categoryId, title, description, projectType, status) "
                   "VALUES (?, ?, ?, 'Test project', ?, ?)",
                   (designerId, categoryId, title, projectType, status))


# times are stored in UTC like CURRENT_TIMESTAMP. 12:00 UTC is the same calendar day in
# Singapore (8pm), so the local-time reports put it on the date written here
def addView(idpId, viewedAt="2026-11-05 12:00:00"):
    execute("INSERT INTO idp_view (idpId, viewedAt) VALUES (?, ?)", (idpId, viewedAt))


def addSave(customer, idpId, savedDate="2026-11-05 12:00:00"):
    execute("INSERT INTO saved_idp (customerId, idpId, savedDate) VALUES (?, ?, ?)",
            (customer, idpId, savedDate))


def execute(sql, params=()):
    conn = getConnection()
    cursor = conn.execute(sql, params)
    conn.commit()
    conn.close()
    return cursor.lastrowid


def countViews(idpId):
    conn = getConnection()
    total = conn.execute("SELECT COUNT(*) FROM idp_view WHERE idpId = ?", (idpId,)).fetchone()[0]
    conn.close()
    return total


# ---------- IDPAnalytics.getViewStatistics() ----------

def test_ut37_1_getViewStatistics_noIDPs():
    assert IDPAnalytics().getViewStatistics(createDesigner()) == []


def test_ut37_2_getViewStatistics_countsEachIDPIncludingZero():
    designer = createDesigner()
    kitchen = createCategory("Kitchen")
    viewed = addIDP(designer, kitchen, "Modern Kitchen")
    never = addIDP(designer, kitchen, "Old Kitchen", "Past")
    addView(viewed)
    addView(viewed)
    counts = {row.idpId: row.views for row in IDPAnalytics().getViewStatistics(designer)}
    assert counts == {viewed: 2, never: 0}


def test_ut37_3_getViewStatistics_onlyOwnIDPs():
    designer = createDesigner()
    other = createDesigner("designer37b")
    kitchen = createCategory("Kitchen")
    own = addIDP(designer, kitchen, "Own Kitchen")
    addView(addIDP(other, kitchen, "Someone Else's Kitchen"))
    assert [row.idpId for row in IDPAnalytics().getViewStatistics(designer)] == [own]


def test_ut37_4_getViewStatistics_skipsDeletedIDPs():
    designer = createDesigner()
    kitchen = createCategory("Kitchen")
    addIDP(designer, kitchen, "Deleted Kitchen", status="Suspended")
    assert IDPAnalytics().getViewStatistics(designer) == []


def test_ut37_5_getViewStatistics_mostViewedFirst_withCategoryAndType():
    designer = createDesigner()
    kitchen = createCategory("Kitchen")
    less = addIDP(designer, kitchen, "A Kitchen")
    more = addIDP(designer, kitchen, "B Kitchen", "Past")
    addView(less)
    for _ in range(3):
        addView(more)
    rows = IDPAnalytics().getViewStatistics(designer)
    assert [row.idpId for row in rows] == [more, less]
    assert rows[0].categoryName == "Kitchen" and rows[0].projectType == "Past"


def test_ut37_6_getViewStatistics_returnsIDPAnalyticsObjects():
    designer = createDesigner()
    idpId = addIDP(designer, createCategory("Kitchen"), "Modern Kitchen")
    addView(idpId)
    rows = IDPAnalytics().getViewStatistics(designer)
    assert rows and all(isinstance(row, IDPAnalytics) for row in rows)
    assert (rows[0].idpId, rows[0].title, rows[0].projectType, rows[0].categoryName, rows[0].views) == \
        (idpId, "Modern Kitchen", "Current", "Kitchen", 1)


# ---------- ViewIDPViewStatisticsController.getViewStatistics() ----------

def test_ut37_7_controller_oneEntityCall_returnsListUnchanged(monkeypatch):
    calls = []
    statistics = [IDPAnalytics(idpId=1, views=3)]
    monkeypatch.setattr(IDPAnalytics, "getViewStatistics",
                        lambda self, designerId: calls.append(designerId) or statistics)
    assert ViewIDPViewStatisticsController().getViewStatistics(37) is statistics
    assert calls == [37]


# ---------- views are added by UC32 View IDP (IDP.viewIDP) ----------

def test_ut37_8_customerOpeningIDP_countsAView():
    idpId = addIDP(createDesigner(), createCategory("Kitchen"), "Modern Kitchen")
    client = app.test_client()
    client.post("/customer/login", data={"username": "cust001", "password": "Cust@123"})
    assert client.get(f"/customer/idps/{idpId}").status_code == 200
    client.get(f"/customer/idps/{idpId}")
    assert countViews(idpId) == 2


def test_ut37_9_customerOpeningMissingIDP_noView():
    client = app.test_client()
    client.post("/customer/login", data={"username": "cust001", "password": "Cust@123"})
    assert client.get("/customer/idps/999999").status_code == 404
    assert countViews(999999) == 0


# ---------- ViewIDPViewStatisticsController.getViewStatistics() ----------

def test_ut37_10_controller_passesDesignerThrough():
    designer = createDesigner()
    idpId = addIDP(designer, createCategory("Kitchen"), "Modern Kitchen")
    addView(idpId)
    fromController = ViewIDPViewStatisticsController().getViewStatistics(designer)
    fromEntity = IDPAnalytics().getViewStatistics(designer)
    assert [(row.idpId, row.views) for row in fromController] == \
        [(row.idpId, row.views) for row in fromEntity] == [(idpId, 1)]


# ---------- ViewIDPViewStatisticsPage (through the Flask route) ----------

def test_ut37_11_page_showsTableOfOwnIDPs():
    designer = createDesigner()
    idpId = addIDP(designer, createCategory("Kitchen"), "Modern Kitchen")
    for _ in range(4):
        addView(idpId)
    client = app.test_client()
    loginAsDesigner(client)
    response = client.get("/designer/idps/statistics/views")
    html = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "Modern Kitchen" in html and "<strong>4</strong>" in html
    assert "A view is counted each time a customer opens the IDP" in html


def test_ut37_12_page_noIDPs_showsMessage():
    createDesigner()
    client = app.test_client()
    loginAsDesigner(client)
    html = client.get("/designer/idps/statistics/views").get_data(as_text=True)
    assert MSG_NO_IDPS.replace("'", "&#39;") in html
    assert "<table" not in html


def test_ut37_13_page_notLoggedIn_redirectsToDesignerLogin():
    response = app.test_client().get("/designer/idps/statistics/views")
    assert response.status_code == 302
    assert "/designer/login" in response.headers["Location"]


def test_ut37_14_dashboardAndMenu_linkToStatistics():
    createDesigner()
    client = app.test_client()
    loginAsDesigner(client)
    html = client.get("/designer/dashboard").get_data(as_text=True)
    assert html.count('href="/designer/idps/statistics/views"') == 2    # side menu + dashboard card
