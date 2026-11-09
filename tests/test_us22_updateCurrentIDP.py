import pytest
from flask import session

from app import app
from boundary.updateCurrentIDPPage import UpdateCurrentIDPPage
from control.interiorDesignerLoginController import InteriorDesignerLoginController, REQUIRED_DESIGNER_PERMISSIONS
from control.searchIDPCategoryController import SearchIDPCategoryController
from control.updateCurrentIDPController import UpdateCurrentIDPController
from database.db import getConnection
from entity.idp import IDP
from entity.userAccount import UserAccount


def execute(sql, values=()):
    conn = getConnection()
    try:
        cursor = conn.execute(sql, values)
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def snapshot(table=None):
    conn = getConnection()
    try:
        if table == "idp":
            return [tuple(row) for row in conn.execute("SELECT * FROM idp ORDER BY idpId")]
        return list(conn.iterdump())
    finally:
        conn.close()


def updateUrl(idpId):
    return f"/designer/idps/current/{idpId}/update"


@pytest.fixture
def data():
    owners = []
    for username in ("update22", "other22"):
        UserAccount().createUserAccount(UserAccount(username=username, password="Design@123", fullName=username, email="", phone="", profileId=2))
        owners.append(UserAccount().verifyCredentials(username, "Design@123", REQUIRED_DESIGNER_PERMISSIONS).userId)
    categories = [execute("INSERT INTO idp_category (categoryName, status) VALUES (?, ?)", values)
                  for values in [("Living Room", "Active"), ("Kitchen", "Active"), ("Hidden", "Suspended")]]
    ids = []
    for owner, category, title, kind, status in [
        (owners[0], categories[0], "Own Current Project", "Current", "Active"),
        (owners[1], categories[0], "Other Designer Project", "Current", "Active"),
        (owners[0], categories[0], "Own Past Project", "Past", "Active"),
        (owners[0], categories[0], "Suspended Project", "Current", "Suspended"),
        (owners[0], categories[2], "Hidden Category Project", "Current", "Active")]:
        ids.append(execute("INSERT INTO idp (designerId, categoryId, title, description, location, projectType, status) "
                           "VALUES (?, ?, ?, 'Initial progress', 'Tampines', ?, ?)",
                           (owner, category, title, kind, status)))
    return dict(owner=owners[0], other=owners[1], category=categories[0], target=categories[1],
                hiddenCategory=categories[2], own=ids[0], foreign=ids[1], past=ids[2],
                suspended=ids[3], hidden=ids[4])


@pytest.fixture
def client(data):
    result = app.test_client()
    assert result.post("/designer/login", data={"username": "update22", "password": "Design@123"}).status_code == 302
    return result


def validData(data, **changes):
    # what the form posts (text fields)
    values = dict(title="Updated Current Project", categoryId=str(data["target"]),
                  description="Carpentry installed. Painting in progress.", location="Bedok")
    values.update(changes)
    return values


def validIDP(data, idpId=None, designerId=None, **changes):
    # the IDP object the page builds and passes on
    values = dict(title="Updated Current Project", categoryId=data["target"],
                  description="Carpentry installed. Painting in progress.", location="Bedok")
    values.update(changes)
    return IDP(idpId or data["own"], designerId or data["owner"], values["categoryId"], values["title"],
               values["description"], values["location"])


def submit(client, data, **changes):
    return client.post(updateUrl(data["own"]), data=validData(data, **changes))


def designerSession(data):
    # a request context with the designer's session, for calling the page directly
    context = app.test_request_context()
    context.push()
    session.update(userId=data["owner"], profileId=2, username="update22")
    return context


def test_ut22_1_loadOwnCurrentProject(data):
    project = UpdateCurrentIDPController().getCurrentIDP(data["owner"], data["own"])
    assert project.title == "Own Current Project" and project.description == "Initial progress"
    assert project.categoryId == data["category"] and project.location == "Tampines"


@pytest.mark.parametrize("key", ["foreign", "past", "suspended", "hidden", "missing"])
def test_ut22_2_unavailableProject(data, key):
    idpId = data.get(key, 999999)
    assert UpdateCurrentIDPController().getCurrentIDP(data["owner"], idpId) is None


def test_ut22_3_availableCategoriesBorrowedFromUS45(data, monkeypatch):
    keywords = []
    original = SearchIDPCategoryController.searchIDPCategories
    def spy(self, keyword):
        keywords.append(keyword)
        return original(self, keyword)
    monkeypatch.setattr(SearchIDPCategoryController, "searchIDPCategories", spy)
    result = UpdateCurrentIDPPage().getAvailableCategories()
    assert [category.categoryName for category in result] == ["Kitchen", "Living Room"]
    assert keywords == [""]


@pytest.mark.parametrize("value,valid", [("", False), ("AB", False), ("ABC", True),
                                          ("A" * 100, True), ("A" * 101, False)])
def test_ut22_4_titleBoundaries(data, value, valid):
    page = UpdateCurrentIDPPage()
    page.validateInput(validIDP(data, title=value))
    assert ("title" not in page.fieldErrors) == valid


@pytest.mark.parametrize("value,valid", [("", False), ("A", True), ("A" * 2000, True), ("A" * 2001, False)])
def test_ut22_5_descriptionBoundaries(data, value, valid):
    page = UpdateCurrentIDPPage()
    page.validateInput(validIDP(data, description=value))
    assert ("description" not in page.fieldErrors) == valid


@pytest.mark.parametrize("value,valid", [("", True), ("A" * 200, True), ("A" * 201, False)])
def test_ut22_6_locationBoundaries(data, value, valid):
    page = UpdateCurrentIDPPage()
    assert page.validateInput(validIDP(data, location=value)) == valid
    assert ("location" not in page.fieldErrors) == valid


@pytest.mark.parametrize("value", [None, 0, -1, 999999, "hidden"])
def test_ut22_7_invalidCategory(data, value):
    if value == "hidden":
        value = data["hiddenCategory"]
    page = UpdateCurrentIDPPage()
    assert page.validateInput(validIDP(data, categoryId=value)) is False
    assert page.fieldErrors["categoryId"] == "Choose an available category"


def test_ut22_8_pageTrimsBeforeSaving(data):
    context = designerSession(data)
    try:
        response = UpdateCurrentIDPPage().submitUpdate(data["own"], "  Updated title  ", data["target"],
                                                       "  Latest progress  ", "  Bedok  ")
    finally:
        context.pop()
    assert response.status_code == 302
    project = IDP().getCurrentIDP(data["owner"], data["own"])
    assert (project.title, project.description, project.location, project.categoryName) == (
        "Updated title", "Latest progress", "Bedok", "Kitchen")


def test_ut22_9_invalidInputSkipsController(data, monkeypatch):
    def unexpected(*args):
        pytest.fail("bad input must not reach the controller")
    monkeypatch.setattr(UpdateCurrentIDPController, "updateCurrentIDP", unexpected)
    before = snapshot()
    context = designerSession(data)
    try:
        page = UpdateCurrentIDPPage()
        response = page.submitUpdate(data["own"], "AB", data["target"], "Some progress", "Bedok")
    finally:
        context.pop()
    assert page.fieldErrors["title"] == "Title must be 3-100 characters"
    assert "Please fix the highlighted fields" in response
    assert snapshot() == before


def test_ut22_10_entityGuardsOwner(data):
    before = snapshot()
    assert IDP().updateCurrentIDP(validIDP(data, idpId=data["foreign"])) is False
    assert snapshot() == before


@pytest.mark.parametrize("key", ["past", "suspended", "hidden", "missing"])
def test_ut22_11_entityGuardsSource(data, key):
    before = snapshot()
    assert IDP().updateCurrentIDP(validIDP(data, idpId=data.get(key, 999999))) is False
    assert snapshot() == before


@pytest.mark.parametrize("category", ["hidden", "missing"])
def test_ut22_12_entityGuardsDestination(data, category):
    before = snapshot()
    categoryId = data["hiddenCategory"] if category == "hidden" else 999999
    assert IDP().updateCurrentIDP(validIDP(data, categoryId=categoryId)) is False
    assert snapshot() == before


def test_ut22_13_onlyEditableFieldsChange(data, client):
    original = IDP().getCurrentIDP(data["owner"], data["own"])
    otherBefore = IDP().getCurrentIDP(data["other"], data["foreign"]).__dict__
    response = submit(client, data, designerId=str(data["other"]), idpId=str(data["foreign"]),
                      projectType="Past", status="Suspended", createdDate="2000-01-01")
    assert response.status_code == 302
    after = IDP().getCurrentIDP(data["owner"], data["own"])
    for field in ("idpId", "designerId", "projectType", "status", "createdDate"):
        assert getattr(after, field) == getattr(original, field)
    assert (after.title, after.categoryId) == ("Updated Current Project", data["target"])
    assert IDP().getCurrentIDP(data["other"], data["foreign"]).__dict__ == otherBefore


def test_ut22_14_unchangedSaveIsSuccessful(data):
    original = IDP().getCurrentIDP(data["owner"], data["own"])
    assert IDP().updateCurrentIDP(original) is True


def test_ut22_15_controllerOnlyCallsTheEntity():
    import control.updateCurrentIDPController as module
    methods = {name for name in vars(UpdateCurrentIDPController) if not name.startswith("_")}
    assert methods == {"getCurrentIDP", "updateCurrentIDP"}
    assert not hasattr(module, "InteriorDesignerLoginController")
    assert not hasattr(module, "IDPCategory")


def test_ut22_16_noLoginControllerOneEntityCall(data, monkeypatch):
    def refused(*args):
        pytest.fail("the controller must not check the designer again")
    monkeypatch.setattr(InteriorDesignerLoginController, "login", lambda self, username, password: None)
    monkeypatch.setattr(UserAccount, "verifyCredentials", refused)
    monkeypatch.setattr(UserAccount, "getUserAccount", refused)
    calls = []
    monkeypatch.setattr(IDP, "getCurrentIDP", lambda self, designerId, idpId: calls.append("get") or "idp")
    monkeypatch.setattr(IDP, "updateCurrentIDP", lambda self, idp: calls.append("update") or True)
    controller = UpdateCurrentIDPController()
    assert controller.getCurrentIDP(data["owner"], data["own"]) == "idp"
    assert controller.updateCurrentIDP(validIDP(data)) is True
    assert calls == ["get", "update"]


def test_ut22_17_formPrefilledWithoutToken(data, client):
    response = client.get(updateUrl(data["own"]))
    assert response.status_code == 200
    for text in [b'"profile-form"', b'"/static/style.css"', b'Designer navigation', b'Logged in as update22',
                 b'Own Current Project', b'Initial progress', b'Tampines', b'Kitchen', b'Living Room', b'Save changes', b'Cancel']:
        assert text in response.data
    assert f'value="{data["category"]}" selected'.encode() in response.data
    assert b'>Hidden</option>' not in response.data
    assert b'type="hidden"' not in response.data and b'Token' not in response.data


@pytest.mark.parametrize("method", ["get", "post"])
def test_ut22_18_signedOutRedirects(data, method):
    before = snapshot()
    response = getattr(app.test_client(), method)(updateUrl(data["own"]))
    assert response.status_code == 302 and response.headers['Location'].endswith('/designer/login')
    assert snapshot() == before


@pytest.mark.parametrize("method", ["get", "post"])
def test_ut22_19_roleNotCheckedAgain(data, method):
    # admin01 has a session, so the page runs - but the IDP isn't admin01's, so it's not found
    client = app.test_client()
    client.post('/login', data=dict(username='admin01', password='Admin@123'))
    before = snapshot()
    response = getattr(client, method)(updateUrl(data["own"]), data=validData(data))
    assert response.status_code == 404
    assert snapshot() == before


def test_ut22_20_errorsPreserveInputWithoutSaving(data, client):
    before = snapshot()
    response = submit(client, data, title="AB", location="Still typed here")
    assert response.status_code == 200
    for text in [b'Please fix the highlighted fields', b'Title must be 3-100 characters', b'value="AB"',
                 b'Still typed here', b'Carpentry installed.', b'field-error', b'aria-describedby="title-error"']:
        assert text in response.data
    assert snapshot() == before


def test_ut22_21_saveRedirectsToUpdatedPreview(data, client):
    response = submit(client, data)
    assert response.status_code == 302 and response.headers['Location'].endswith(f'/current/{data["own"]}')
    preview = client.get(response.headers['Location'])
    for text in [b'Current IDP updated successfully', b'Updated Current Project', b'Carpentry installed.', b'Kitchen', b'Bedok']:
        assert text in preview.data


def test_ut22_22_cancelDoesNotSave(data, client):
    before = snapshot()
    assert client.get(updateUrl(data["own"])).status_code == 200
    assert client.get(f'/designer/idps/current/{data["own"]}').status_code == 200
    assert snapshot() == before


@pytest.mark.parametrize("change,status", [("account", 302), ("profile", 302), ("permission", 302),
                                          ("project", 404), ("category", 404), ("past", 404)])
def test_ut22_23_changesAfterFormOpened(data, client, change, status):
    assert client.get(updateUrl(data["own"])).status_code == 200
    statements = {
        "account": ("UPDATE user_account SET status='Suspended' WHERE userId=?", data["owner"]),
        "profile": ("UPDATE user_profile SET status='Suspended' WHERE profileId=?", 2),
        "permission": ("UPDATE user_profile SET permissions='[]' WHERE profileId=?", 2),
        "project": ("UPDATE idp SET status='Suspended' WHERE idpId=?", data["own"]),
        "category": ("UPDATE idp_category SET status='Suspended' WHERE categoryId=?", data["category"]),
        "past": ("UPDATE idp SET projectType='Past' WHERE idpId=?", data["own"]),
    }
    sql, value = statements[change]
    execute(sql, (value,))
    before = snapshot('idp')
    response = submit(client, data)
    assert response.status_code == status
    if status == 302:
        # the account isn't checked again (precondition UC13) - the save goes through
        conn = getConnection()
        title = conn.execute("SELECT title FROM idp WHERE idpId=?", (data["own"],)).fetchone()["title"]
        conn.close()
        assert title == "Updated Current Project"
    else:
        assert snapshot('idp') == before


def test_ut22_24_noFormToken(data, client):
    assert submit(client, data, title="First save").status_code == 302
    assert submit(client, data, title="Second save", updateToken="forged-token").status_code == 302
    assert IDP().getCurrentIDP(data["owner"], data["own"]).title == "Second save"
    with client.session_transaction() as state:
        assert set(state) <= {"userId", "profileId", "username", "_flashes"}


@pytest.mark.parametrize("source", [False, True])
def test_ut22_25_categorySuspendedJustBeforeUpdate(data, client, monkeypatch, source):
    original = IDP.updateCurrentIDP
    def suspendThenWrite(self, idp):
        execute("UPDATE idp_category SET status='Suspended' WHERE categoryId=?",
                (data["category"] if source else data["target"],))
        return original(self, idp)
    monkeypatch.setattr(IDP, 'updateCurrentIDP', suspendThenWrite)
    before = snapshot('idp')
    response = submit(client, data)
    assert response.status_code == 404 and b'Current IDP not found' in response.data
    assert snapshot('idp') == before


@pytest.mark.parametrize("key", ["foreign", "past", "suspended", "hidden", "missing"])
@pytest.mark.parametrize("method", ["get", "post"])
def test_ut22_26_unavailableRouteHasNoDetails(data, client, key, method):
    before = snapshot()
    response = getattr(client, method)(updateUrl(data.get(key, 999999)), data=validData(data))
    assert response.status_code == 404
    assert b'Initial progress' not in response.data and b'Other Designer Project' not in response.data
    assert snapshot() == before


def test_ut22_27_customerTextEscaped(data, client):
    attack = '<script>alert("test")</script>'
    response = submit(client, data, title=attack, description=attack, location=attack)
    assert response.status_code == 302
    for url in [updateUrl(data['own']), f'/designer/idps/current/{data["own"]}']:
        result = client.get(url)
        assert b'<script>' not in result.data and b'&lt;script&gt;' in result.data


def test_ut22_28_updateLinkAndForeignOwnerIgnored(data, client):
    response = client.get(f'/designer/idps/current/{data["own"]}')
    assert updateUrl(data['own']).encode() in response.data
    response = client.get(updateUrl(data['foreign']) + f'?designerId={data["other"]}')
    assert response.status_code == 404


def test_ut22_29_formStillOpensAfterProfileSuspended(data, client):
    execute("UPDATE user_profile SET status='Suspended' WHERE profileId=2")
    response = client.get(updateUrl(data['own']))
    assert response.status_code == 200 and b'Own Current Project' in response.data


def test_ut22_30_anotherDesignerCannotUpdate(data, client):
    client.post('/designer/logout')
    assert client.post('/designer/login', data=dict(username='other22', password='Design@123')).status_code == 302
    before = snapshot()
    response = submit(client, data)
    assert response.status_code == 404
    assert snapshot() == before


# ---------- system tests (Flask test client) ----------

def test_tc22_9_profileSuspendedWhileEditing(data, client):
    assert client.get(updateUrl(data["own"])).status_code == 200
    execute("UPDATE user_profile SET status='Suspended' WHERE profileId=2")
    # being logged in is the precondition (UC13), so the save still goes through
    response = submit(client, data)
    assert response.status_code == 302
    assert IDP().getCurrentIDP(data["owner"], data["own"]).title == "Updated Current Project"
    # the next login is refused
    client.post('/designer/logout')
    response = client.post('/designer/login', data=dict(username='update22', password='Design@123'))
    assert b'Invalid login details or access unavailable' in response.data


def test_tc22_11_sameFormSentTwice(data, client):
    assert client.get(updateUrl(data["own"])).status_code == 200
    assert submit(client, data).status_code == 302
    # Back, then the same form again - there's no form token, so it saves again
    assert submit(client, data).status_code == 302
    project = IDP().getCurrentIDP(data["owner"], data["own"])
    assert (project.title, project.categoryId, project.location) == ("Updated Current Project", data["target"], "Bedok")
