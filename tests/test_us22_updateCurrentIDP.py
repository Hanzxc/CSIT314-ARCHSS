import re

import pytest

from app import app
from control.updateCurrentIDPController import UpdateCurrentIDPController
from database.db import getConnection
from entity.idp import IDP
from entity.idpCategory import IDPCategory
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
        UserAccount().createUserAccount(username, "Design@123", username, "", "", 2)
        owners.append(UserAccount().verifyCredentials(username, "Design@123").userId)
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
    values = dict(title="Updated Current Project", categoryId=str(data["target"]),
                  description="Carpentry installed. Painting in progress.", location="Bedok")
    values.update(changes)
    return values


def formToken(client, idpId):
    response = client.get(updateUrl(idpId))
    assert response.status_code == 200
    return re.search(rb'name="updateToken" value="([^"]+)"', response.data).group(1).decode()


def submit(client, data, **changes):
    token = formToken(client, data["own"])
    return client.post(updateUrl(data["own"]), data={**validData(data, **changes), "updateToken": token})


def test_ut22_1_loadOwnCurrentProject(data):
    project = UpdateCurrentIDPController().getCurrentIDP(data["owner"], data["own"])
    assert project.title == "Own Current Project" and project.description == "Initial progress"
    assert project.categoryId == data["category"] and project.location == "Tampines"


@pytest.mark.parametrize("key", ["foreign", "past", "suspended", "hidden", "missing"])
def test_ut22_2_unavailableProject(data, key):
    idpId = data.get(key, 999999)
    assert UpdateCurrentIDPController().getCurrentIDP(data["owner"], idpId) is None


def test_ut22_3_activeCategories(data):
    result = UpdateCurrentIDPController().getActiveIDPCategories(data["owner"])
    assert [category.categoryName for category in result] == ["Kitchen", "Living Room"]


@pytest.mark.parametrize("value,valid", [("", False), ("   ", False), ("AB", False), ("ABC", True),
                                          ("A" * 100, True), ("A" * 101, False), ("  ABC  ", True)])
def test_ut22_4_titleBoundaries(data, value, valid):
    errors = UpdateCurrentIDPController().getFieldErrors(validData(data, title=value))
    assert ("title" not in errors) == valid


@pytest.mark.parametrize("value,valid", [("", False), ("   ", False), ("A", True), ("A" * 2000, True), ("A" * 2001, False)])
def test_ut22_5_descriptionBoundaries(data, value, valid):
    errors = UpdateCurrentIDPController().getFieldErrors(validData(data, description=value))
    assert ("description" not in errors) == valid


@pytest.mark.parametrize("value,valid", [("", True), ("A" * 200, True), ("A" * 201, False)])
def test_ut22_6_locationBoundaries(data, value, valid):
    errors = UpdateCurrentIDPController().getFieldErrors(validData(data, location=value))
    assert ("location" not in errors) == valid


@pytest.mark.parametrize("value", [None, "", "0", "-1", "999999", "abc", "1 OR 1=1", "hidden"])
def test_ut22_7_invalidCategory(data, value):
    if value == "hidden":
        value = str(data["hiddenCategory"])
    assert "categoryId" in UpdateCurrentIDPController().getFieldErrors(validData(data, categoryId=value))


def test_ut22_8_updateTrimsAndChangesCategory(data):
    controller = UpdateCurrentIDPController()
    assert controller.updateCurrentIDP(data["owner"], data["own"],
                                       validData(data, title="  Updated title  ", description="  Latest progress  ", location="  Bedok  "))
    project = IDP().getCurrentIDP(data["owner"], data["own"])
    assert (project.title, project.description, project.location, project.categoryName) == (
        "Updated title", "Latest progress", "Bedok", "Kitchen")


def test_ut22_9_invalidInputDoesNotWrite(data):
    before = snapshot()
    assert UpdateCurrentIDPController().updateCurrentIDP(data["owner"], data["own"], validData(data, title="AB")) is False
    assert snapshot() == before


def test_ut22_10_entityGuardsOwner(data):
    before = snapshot()
    assert IDP().updateCurrentIDP(data["owner"], data["foreign"], validData(data)) is False
    assert snapshot() == before


@pytest.mark.parametrize("key", ["past", "suspended", "hidden", "missing"])
def test_ut22_11_entityGuardsSource(data, key):
    before = snapshot()
    assert IDP().updateCurrentIDP(data["owner"], data.get(key, 999999), validData(data)) is False
    assert snapshot() == before


@pytest.mark.parametrize("category", ["hidden", "missing"])
def test_ut22_12_entityGuardsDestination(data, category):
    before = snapshot()
    assert IDP().updateCurrentIDP(data["owner"], data["own"],
                                 validData(data, categoryId=data["hiddenCategory"] if category == "hidden" else 999999)) is False
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
    assert IDP().getCurrentIDP(data["other"], data["foreign"]).__dict__ == otherBefore


def test_ut22_14_unchangedSaveIsSuccessful(data):
    original = IDP().getCurrentIDP(data["owner"], data["own"])
    values = {key: getattr(original, key) for key in ("title", "categoryId", "description", "location")}
    assert IDP().updateCurrentIDP(data["owner"], data["own"], values) is True


@pytest.mark.parametrize("change", ["active", "account", "profile", "permissions", "admin", "customer", "missing"])
def test_ut22_15_designerAccess(data, change):
    owner = data["owner"]
    if change == "account":
        execute("UPDATE user_account SET status='Suspended' WHERE userId=?", (owner,))
    elif change == "profile":
        execute("UPDATE user_profile SET status='Suspended' WHERE profileId=2")
    elif change == "permissions":
        execute("UPDATE user_profile SET permissions='[]' WHERE profileId=2")
    elif change != "active":
        owner = {"admin": 1, "customer": 3, "missing": 999999}[change]
    assert UpdateCurrentIDPController().canUpdateCurrentIDP(owner) == (change == "active")


@pytest.mark.parametrize("operation", ["get", "categories", "update"])
def test_ut22_16_controllerDenialStopsQueries(data, monkeypatch, operation):
    monkeypatch.setattr(UpdateCurrentIDPController, "canUpdateCurrentIDP", lambda *args: False)
    def unexpected(*args):
        pytest.fail("Denied requests must stop before entity access")
    monkeypatch.setattr(IDP, "getCurrentIDP", unexpected)
    monkeypatch.setattr(IDP, "updateCurrentIDP", unexpected)
    monkeypatch.setattr(IDPCategory, "getActiveIDPCategories", unexpected)
    control = UpdateCurrentIDPController()
    with pytest.raises(PermissionError):
        if operation == "get":
            control.getCurrentIDP(data["owner"], data["own"])
        elif operation == "categories":
            control.getActiveIDPCategories(data["owner"])
        else:
            control.updateCurrentIDP(data["owner"], data["own"], validData(data))


def test_ut22_17_formPrefilledAndMatchesSharedLayout(data, client):
    response = client.get(updateUrl(data["own"]))
    assert response.status_code == 200
    for text in [b'"profile-form"', b'"/static/style.css"', b'Designer navigation', b'Logged in as update22',
                 b'Own Current Project', b'Initial progress', b'Tampines', b'Kitchen', b'Living Room', b'Save changes', b'Cancel']:
        assert text in response.data
    assert f'value="{data["category"]}" selected'.encode() in response.data
    assert b'>Hidden</option>' not in response.data
    assert b'name="updateToken"' in response.data


@pytest.mark.parametrize("method", ["get", "post"])
def test_ut22_18_signedOutRedirects(data, method):
    before = snapshot()
    response = getattr(app.test_client(), method)(updateUrl(data["own"]))
    assert response.status_code == 302 and response.headers['Location'].endswith('/designer/login')
    assert snapshot() == before


@pytest.mark.parametrize("method", ["get", "post"])
def test_ut22_19_nonDesignerForbidden(data, method):
    client = app.test_client()
    client.post('/login', data=dict(username='admin01', password='Admin@123'))
    before = snapshot()
    assert getattr(client, method)(updateUrl(data["own"])).status_code == 403
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


@pytest.mark.parametrize("change,status", [("account", 403), ("profile", 403), ("permission", 403),
                                          ("project", 404), ("category", 404), ("past", 404)])
def test_ut22_23_recheckAtSubmission(data, client, change, status):
    token = formToken(client, data["own"])
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
    before = snapshot()
    response = client.post(updateUrl(data["own"]), data={**validData(data), 'updateToken': token})
    assert response.status_code == status
    assert snapshot() == before


@pytest.mark.parametrize("kind", ["missing", "bad", "unicode", "stale", "replayed"])
def test_ut22_24_invalidFormToken(data, client, kind):
    token = formToken(client, data["own"])
    if kind == "missing": token = ""
    elif kind == "bad": token = "forged-token"
    elif kind == "unicode": token = "无效"
    elif kind == "stale": formToken(client, data["own"])
    elif kind == "replayed":
        assert client.post(updateUrl(data["own"]), data={**validData(data), 'updateToken': token}).status_code == 302
    before = snapshot()
    response = client.post(updateUrl(data["own"]), data={**validData(data, title="Replay should not save"), 'updateToken': token})
    assert response.status_code == 403
    assert b'This update form is no longer valid' in response.data
    assert snapshot() == before


@pytest.mark.parametrize("source", [False, True])
def test_ut22_25_atomicCategoryRecheck(data, client, monkeypatch, source):
    original = IDP.updateCurrentIDP
    def suspendThenWrite(self, designerId, idpId, idpData):
        execute("UPDATE idp_category SET status='Suspended' WHERE categoryId=?",
                (data["category"] if source else data["target"],))
        return original(self, designerId, idpId, idpData)
    monkeypatch.setattr(IDP, 'updateCurrentIDP', suspendThenWrite)
    before = snapshot('idp')
    response = submit(client, data)
    assert response.status_code == (404 if source else 200)
    if not source: assert b'Choose an available category' in response.data
    assert snapshot('idp') == before


@pytest.mark.parametrize("key", ["foreign", "past", "suspended", "hidden", "missing"])
@pytest.mark.parametrize("method", ["get", "post"])
def test_ut22_26_unavailableRouteHasNoDetails(data, client, key, method):
    before = snapshot()
    response = getattr(client, method)(updateUrl(data.get(key, 999999)))
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


def test_ut22_29_controllerRecheckHandled(data, client, monkeypatch):
    checks = iter([True, False])
    monkeypatch.setattr(UpdateCurrentIDPController, 'canUpdateCurrentIDP', lambda *args: next(checks))
    response = client.get(updateUrl(data['own']))
    assert response.status_code == 403


def test_ut22_30_formTokenBoundToProjectAndUser(data, client):
    token = formToken(client, data['own'])
    second = execute("INSERT INTO idp (designerId, categoryId, title, description) VALUES (?, ?, 'Second Project', 'Progress')",
                     (data['owner'], data['category']))
    before = snapshot()
    response = client.post(updateUrl(second), data={**validData(data), 'updateToken': token})
    assert response.status_code == 403 and snapshot() == before
    client.post('/designer/logout')
    client.post('/designer/login', data=dict(username='other22', password='Design@123'))
    response = client.post(updateUrl(data['foreign']), data={**validData(data), 'updateToken': token})
    assert response.status_code == 403 and snapshot() == before
