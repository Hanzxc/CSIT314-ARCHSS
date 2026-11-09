# US21: isolated database fixtures, BCE tests and full Flask request checks.
import pytest

from app import app
from control.interiorDesignerLoginController import InteriorDesignerLoginController, REQUIRED_DESIGNER_PERMISSIONS
from control.viewCurrentIDPController import ViewCurrentIDPController
from database.db import getConnection, initDatabase
from entity.idp import IDP
from entity.userAccount import UserAccount

LIST_URL = "/designer/idps/current"


def execute(sql, parameters=()):
    conn = getConnection()
    try:
        cursor = conn.execute(sql, parameters)
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def databaseSnapshot():
    conn = getConnection()
    try:
        return list(conn.iterdump())
    finally:
        conn.close()


def addProject(designerId, categoryId, title, projectType="Current", status="Active", location="Tampines"):
    return execute("INSERT INTO idp (designerId, categoryId, title, description, location, projectType, status) "
                   "VALUES (?, ?, ?, ?, ?, ?, ?)",
                   (designerId, categoryId, title, "Natural wood finishes.\nWork in progress.",
                    location, projectType, status))


@pytest.fixture
def projects():
    for username in ("designer21", "designer22"):
        assert UserAccount().createUserAccount(UserAccount(username=username, password="Design@123", fullName="Designer " + username,
                                              email=username + "@example.com", phone="", profileId=2))
    owner = UserAccount().verifyCredentials("designer21", "Design@123", REQUIRED_DESIGNER_PERMISSIONS).userId
    other = UserAccount().verifyCredentials("designer22", "Design@123", REQUIRED_DESIGNER_PERMISSIONS).userId
    category = execute("INSERT INTO idp_category (categoryName) VALUES ('Living Room')")
    hiddenCategory = execute("INSERT INTO idp_category (categoryName, status) VALUES ('Hidden Category', 'Suspended')")
    first = addProject(owner, category, "Warm Minimalist Apartment")
    second = addProject(owner, category, "Modern Kitchen Renovation")
    otherIdp = addProject(other, category, "Other Designer Private Project")
    past = addProject(owner, category, "Completed Past Project", projectType="Past")
    suspended = addProject(owner, category, "Suspended Current Project", status="Suspended")
    hidden = addProject(owner, hiddenCategory, "Hidden Category Project")
    return dict(owner=owner, other=other, category=category, hiddenCategory=hiddenCategory,
                first=first, second=second, otherIdp=otherIdp, past=past, suspended=suspended, hidden=hidden)


@pytest.fixture
def designerClient(projects):
    client = app.test_client()
    response = client.post("/designer/login", data={"username": "designer21", "password": "Design@123"})
    assert response.status_code == 302
    return client


def detailUrl(idpId):
    return LIST_URL + "/" + str(idpId)


def test_ut21_1_getCurrentIDPs_ownProjectsOnly(projects):
    result = IDP().getCurrentIDPs(projects["owner"])
    assert {idp.idpId for idp in result} == {projects["first"], projects["second"]}
    assert all(idp.designerId == projects["owner"] for idp in result)


def test_ut21_2_getCurrentIDPs_excludesPast(projects):
    assert projects["past"] not in [p.idpId for p in IDP().getCurrentIDPs(projects["owner"])]


def test_ut21_3_getCurrentIDPs_excludesSuspended(projects):
    assert projects["suspended"] not in [p.idpId for p in IDP().getCurrentIDPs(projects["owner"])]


def test_ut21_4_getCurrentIDPs_excludesSuspendedCategory(projects):
    assert projects["hidden"] not in [p.idpId for p in IDP().getCurrentIDPs(projects["owner"])]


@pytest.mark.parametrize("count", [0, 1, 3])
def test_ut21_5_getCurrentIDPs_zeroOneMany(projects, count):
    execute("DELETE FROM idp WHERE designerId = ?", (projects["owner"],))
    for i in range(count):
        addProject(projects["owner"], projects["category"], "Current project " + str(i))
    assert len(IDP().getCurrentIDPs(projects["owner"])) == count


def test_ut21_6_getCurrentIDPs_newestFirst(projects):
    execute("DELETE FROM idp WHERE designerId=?", (projects["owner"],))
    # Deliberately insert out of ID order, matching the documented UT21.6 inputs.
    for idpId in [10, 12, 11]:
        execute("INSERT INTO idp (idpId, designerId, categoryId, title, description) VALUES (?, ?, ?, ?, ?)",
                (idpId, projects["owner"], projects["category"], "Current project " + str(idpId), "In progress."))
    assert [p.idpId for p in IDP().getCurrentIDPs(projects["owner"])] == [12, 11, 10]


def test_ut21_7_getCurrentIDP_customerFields(projects):
    idp = IDP().getCurrentIDP(projects["owner"], projects["first"])
    assert idp.title == "Warm Minimalist Apartment"
    assert idp.categoryName == "Living Room"
    assert idp.description == "Natural wood finishes.\nWork in progress."
    assert idp.location == "Tampines"
    assert idp.projectType == "Current" and idp.status == "Active"
    assert idp.createdDate


def test_ut21_8_getCurrentIDP_otherOwner(projects):
    assert IDP().getCurrentIDP(projects["owner"], projects["otherIdp"]) is None


@pytest.mark.parametrize("key", ["past", "suspended"])
def test_ut21_9_getCurrentIDP_unavailableProject(projects, key):
    assert IDP().getCurrentIDP(projects["owner"], projects[key]) is None


def test_ut21_10_getCurrentIDP_unavailableCategory(projects):
    assert IDP().getCurrentIDP(projects["owner"], projects["hidden"]) is None


@pytest.mark.parametrize("idpId", [0, -1, 999999])
def test_ut21_11_getCurrentIDP_invalidId(projects, idpId):
    assert IDP().getCurrentIDP(projects["owner"], idpId) is None


def test_ut21_12_controllerOnlyHasTheTwoViewMethods():
    import control.viewCurrentIDPController as module
    methods = {name for name in vars(ViewCurrentIDPController) if not name.startswith("_")}
    assert methods == {"viewCurrentIDPs", "viewCurrentIDP"}
    assert not hasattr(module, "InteriorDesignerLoginController")


@pytest.mark.parametrize("change", ["account", "profile", "permission"])
def test_ut21_13_designerNotCheckedAgain(projects, change):
    # being logged in is the precondition (UC13) - a change after logging in isn't checked again
    statements = {
        "account": ("UPDATE user_account SET status='Suspended' WHERE userId=?", projects["owner"]),
        "profile": ("UPDATE user_profile SET status='Suspended' WHERE profileId=?", 2),
        "permission": ("UPDATE user_profile SET permissions='[]' WHERE profileId=?", 2),
    }
    sql, value = statements[change]
    execute(sql, (value,))
    titles = [idp.title for idp in ViewCurrentIDPController().viewCurrentIDPs(projects["owner"])]
    assert titles == ["Modern Kitchen Renovation", "Warm Minimalist Apartment"]


def test_ut21_14_viewCurrentIDPs_delegatesOwner(projects, monkeypatch):
    seen = []
    monkeypatch.setattr(IDP, "getCurrentIDPs", lambda self, designerId: seen.append(designerId) or [])
    assert ViewCurrentIDPController().viewCurrentIDPs(projects["owner"]) == []
    assert seen == [projects["owner"]]


def test_ut21_15_viewCurrentIDP_delegatesOwnerAndId(projects, monkeypatch):
    seen = []
    monkeypatch.setattr(IDP, "getCurrentIDP", lambda self, designerId, idpId: seen.append((designerId, idpId)))
    ViewCurrentIDPController().viewCurrentIDP(projects["owner"], projects["first"])
    assert seen == [(projects["owner"], projects["first"])]


@pytest.mark.parametrize("detail", [False, True])
def test_ut21_16_noLoginControllerOneEntityCall(projects, monkeypatch, detail):
    def refused(*args):
        pytest.fail("the controller must not check the designer again")
    monkeypatch.setattr(InteriorDesignerLoginController, "login", lambda self, username, password: None)
    monkeypatch.setattr(UserAccount, "verifyCredentials", refused)
    monkeypatch.setattr(UserAccount, "getUserAccount", refused)
    calls = []
    monkeypatch.setattr(IDP, "getCurrentIDPs", lambda self, designerId: calls.append(designerId) or ["list"])
    monkeypatch.setattr(IDP, "getCurrentIDP", lambda self, designerId, idpId: calls.append(idpId) or "idp")
    controller = ViewCurrentIDPController()
    if detail:
        assert controller.viewCurrentIDP(projects["owner"], projects["first"]) == "idp"
        assert calls == [projects["first"]]
    else:
        assert controller.viewCurrentIDPs(projects["owner"]) == ["list"]
        assert calls == [projects["owner"]]


@pytest.mark.parametrize("path", [LIST_URL, detailUrl(1)])
def test_ut21_17_signedOutRedirectsToLogin(path):
    response = app.test_client().get(path)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/designer/login")


@pytest.mark.parametrize("loginUrl,username,password", [("/login", "admin01", "Admin@123"),
                                                        ("/customer/login", "cust001", "Cust@123")])
def test_ut21_18_roleNotCheckedAgain(projects, loginUrl, username, password):
    # each role logs in on its own page (/login is only for User Admins, US1). the designer pages
    # don't check the role again (precondition UC13) - these users just own no current IDPs
    client = app.test_client()
    assert client.post(loginUrl, data={"username": username, "password": password}).status_code == 302
    response = client.get(LIST_URL)
    assert response.status_code == 200
    assert b"You have no current IDPs to display" in response.data
    response = client.get(detailUrl(projects["first"]))
    assert response.status_code == 404
    assert b"Warm Minimalist Apartment" not in response.data


def test_ut21_19_emptyListShowsMessage(projects, designerClient):
    execute("DELETE FROM idp WHERE designerId=?", (projects["owner"],))
    response = designerClient.get(LIST_URL)
    assert response.status_code == 200
    assert b"You have no current IDPs to display" in response.data
    assert b"Other Designer Private Project" not in response.data


def test_ut21_20_detailShowsOnlyCustomerContent(projects, designerClient):
    response = designerClient.get(detailUrl(projects["first"]))
    assert response.status_code == 200
    for text in [b"Warm Minimalist Apartment", b"Living Room", b"Natural wood finishes.", b"Tampines", b"Back to list"]:
        assert text in response.data
    content = response.data.split(b'<main class="content">', 1)[1]
    for text in [b"Design@123", b"designer21@example.com", b"designerId", b"createdDate", b"<input", b"<textarea", b'type="submit"']:
        assert text not in content


@pytest.mark.parametrize("key", ["otherIdp", "past", "suspended", "hidden", "missing", "zero", "negative"])
def test_ut21_21_unavailableDetailDoesNotDiscloseData(projects, designerClient, key):
    idpId = {**projects, "missing": 999999, "zero": 0, "negative": -1}[key]
    response = designerClient.get(detailUrl(idpId))
    assert response.status_code == 404
    assert b"Current IDP not found" in response.data
    assert b"Other Designer Private Project" not in response.data
    assert b"Natural wood finishes" not in response.data


def test_ut21_22_forgedOwnerIgnored(projects, designerClient):
    query = "?designerId=" + str(projects["other"]) + "&userId=" + str(projects["other"])
    response = designerClient.get(LIST_URL + query)
    assert b"Warm Minimalist Apartment" in response.data
    assert b"Other Designer Private Project" not in response.data
    assert designerClient.get(detailUrl(projects["otherIdp"]) + query).status_code == 404
    assert designerClient.get(detailUrl(projects["first"]) + query).status_code == 200


@pytest.mark.parametrize("change,status", [("account", 200), ("profile", 200), ("permission", 200),
                                          ("project", 404), ("category", 404), ("past", 404)])
def test_ut21_23_changesAfterListing(projects, designerClient, change, status):
    assert designerClient.get(LIST_URL).status_code == 200
    statements = {
        "account": ("UPDATE user_account SET status='Suspended' WHERE userId=?", projects["owner"]),
        "profile": ("UPDATE user_profile SET status='Suspended' WHERE profileId=?", 2),
        "permission": ("UPDATE user_profile SET permissions='[]' WHERE profileId=?", 2),
        "project": ("UPDATE idp SET status='Suspended' WHERE idpId=?", projects["first"]),
        "category": ("UPDATE idp_category SET status='Suspended' WHERE categoryId=?", projects["category"]),
        "past": ("UPDATE idp SET projectType='Past' WHERE idpId=?", projects["first"]),
    }
    sql, value = statements[change]
    execute(sql, (value,))
    # the account isn't checked again (precondition UC13), only the IDP itself
    assert designerClient.get(detailUrl(projects["first"])).status_code == status
    if status == 200:
        assert designerClient.get(LIST_URL).status_code == 200


def test_ut21_24_repeatedViewsAreReadOnly(projects, designerClient):
    before = databaseSnapshot()
    for _ in range(2):
        assert designerClient.get(LIST_URL).status_code == 200
        assert designerClient.get(detailUrl(projects["first"])).status_code == 200
    assert databaseSnapshot() == before


def test_ut21_25_optionalLocationOmitted(projects, designerClient):
    execute("UPDATE idp SET location='' WHERE idpId=?", (projects["first"],))
    response = designerClient.get(detailUrl(projects["first"]))
    assert response.status_code == 200
    assert b"Location:" not in response.data
    assert b"None" not in response.data


def test_ut21_26_textEscapedInListAndDetail(projects, designerClient):
    attack = '<script>alert("test")</script>'
    execute("UPDATE idp SET title=?, description=?, location=? WHERE idpId=?",
            (attack, attack, attack, projects["first"]))
    execute("UPDATE idp_category SET categoryName=? WHERE categoryId=?", (attack, projects["category"]))
    for url in [LIST_URL, detailUrl(projects["first"])]:
        response = designerClient.get(url)
        assert response.status_code == 200
        assert b"<script>" not in response.data
        assert b"&lt;script&gt;" in response.data


def test_ut21_27_navigationAndListOrdering(projects, designerClient):
    response = designerClient.get("/designer/dashboard")
    assert b'href="/designer/idps/current"' in response.data
    response = designerClient.get(LIST_URL)
    assert response.data.index(b"Modern Kitchen Renovation") < response.data.index(b"Warm Minimalist Apartment")
    for key in ["first", "second"]:
        assert ('href="' + detailUrl(projects[key]) + '"').encode() in response.data
    assert b"Other Designer Private Project" not in response.data


@pytest.mark.parametrize("method", ["post", "put", "patch", "delete"])
def test_ut21_28_routesRejectWrites(projects, designerClient, method):
    before = databaseSnapshot()
    for url in [LIST_URL, detailUrl(projects["first"])]:
        assert getattr(designerClient, method)(url).status_code == 405
    assert databaseSnapshot() == before


def test_ut21_30_initialisationPreservesExistingData(projects):
    before = databaseSnapshot()
    initDatabase()
    initDatabase()
    assert databaseSnapshot() == before


def test_ut21_31_demoDataCanBeViewedAndIsRepeatable():
    from database.seedCurrentIDPData import seedCurrentIDPData

    assert seedCurrentIDPData() == 4
    before = databaseSnapshot()
    assert seedCurrentIDPData() == 0
    assert databaseSnapshot() == before
    client = app.test_client()
    response = client.post("/designer/login", data={"username": "idpdemo001", "password": "Demo@123"})
    assert response.status_code == 302
    response = client.get(LIST_URL)
    assert response.status_code == 200
    assert b"Warm Minimalist Apartment" in response.data
    assert b"Modern Kitchen Renovation" in response.data


# ---------- system test (Flask test client) ----------

def test_tc21_10_profileSuspendedAfterLogin(projects, designerClient):
    execute("UPDATE user_profile SET status='Suspended' WHERE profileId=2")
    # being logged in is the precondition (UC13), so the list still opens for this session
    response = designerClient.get(LIST_URL)
    assert response.status_code == 200 and b"Warm Minimalist Apartment" in response.data
    # the next login is refused
    designerClient.post("/designer/logout")
    response = designerClient.post("/designer/login", data={"username": "designer21", "password": "Design@123"})
    assert response.status_code == 200
    assert b"Invalid login details or access unavailable" in response.data
    assert designerClient.get(LIST_URL).headers["Location"].endswith("/designer/login")
