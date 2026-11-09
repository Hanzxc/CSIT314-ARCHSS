import pytest

from app import app
from control.deleteCurrentIDPController import DeleteCurrentIDPController
from control.interiorDesignerLoginController import InteriorDesignerLoginController
from entity.idp import IDP
from entity.userAccount import UserAccount
from test_us22_updateCurrentIDP import data, client, execute, snapshot, validData, updateUrl


def deleteUrl(idpId):
    return f"/designer/idps/current/{idpId}/delete"


def status(idpId):
    return next(row for row in snapshot('idp') if row[0] == idpId)[7]


def postDelete(client, idpId, **extra):
    return client.post(deleteUrl(idpId), data=dict(choice='delete', **extra))


def test_ut23_1_controllerOnlyCallsTheEntity():
    import control.deleteCurrentIDPController as module
    methods = {name for name in vars(DeleteCurrentIDPController) if not name.startswith('_')}
    assert methods == {'getCurrentIDP', 'deleteCurrentIDP'}
    assert not hasattr(module, 'InteriorDesignerLoginController')
    assert not hasattr(IDP, 'getSnapshot')


def test_ut23_2_loadOwnProject(data):
    result = DeleteCurrentIDPController().getCurrentIDP(data['owner'], data['own'])
    assert result.title == 'Own Current Project'


@pytest.mark.parametrize('key', ['foreign', 'past', 'suspended', 'hidden', 'missing'])
def test_ut23_3_excludedProject(data, key):
    assert DeleteCurrentIDPController().getCurrentIDP(data['owner'], data.get(key, 999999)) is None


def test_ut23_4_entitySuspendsAndPreservesRecord(data):
    before = snapshot('idp')
    assert IDP().suspendCurrentIDP(data['owner'], data['own']) is True
    after = snapshot('idp')
    assert len(after) == len(before)
    for old, new in zip(before, after):
        if old[0] == data['own']:
            differences = [(a, b) for a, b in zip(old, new) if a != b]
            assert differences == [('Active', 'Suspended')]
        else:assert new == old


def test_ut23_5_entityGuardsOwner(data):
    before = snapshot()
    assert IDP().suspendCurrentIDP(data['owner'], data['foreign']) is False
    assert snapshot() == before


@pytest.mark.parametrize('key', ['past', 'suspended', 'hidden', 'missing'])
def test_ut23_6_entityGuardsVisibility(data, key):
    before = snapshot()
    assert IDP().suspendCurrentIDP(data['owner'], data.get(key, 999999)) is False
    assert snapshot() == before


def test_ut23_7_onlyTheTwoIds(data):
    assert IDP().suspendCurrentIDP(data['owner'], data['own']) is True
    assert status(data['own']) == 'Suspended'


@pytest.mark.parametrize('field,value', [('title', 'Revised Project'), ('description', 'New progress'),
                                        ('location', 'Bedok'), ('categoryId', 'target')])
def test_ut23_8_detailsNotCompared(data, field, value):
    if value == 'target':
        value = data['target']
    execute('UPDATE idp SET ' + field + '=? WHERE idpId=?', (value, data['own']))
    assert IDP().suspendCurrentIDP(data['owner'], data['own']) is True
    row = next(row for row in snapshot('idp') if row[0] == data['own'])
    assert value in row and row[7] == 'Suspended'


def test_ut23_9_sameDeleteTwice(data):
    assert IDP().suspendCurrentIDP(data['owner'], data['own']) is True
    before = snapshot()
    assert IDP().suspendCurrentIDP(data['owner'], data['own']) is False
    assert snapshot() == before


def test_ut23_10_controllerDeletesOwnProject(data):
    assert DeleteCurrentIDPController().deleteCurrentIDP(data['owner'], data['own']) is True
    assert DeleteCurrentIDPController().getCurrentIDP(data['owner'], data['own']) is None


def test_ut23_11_noLoginControllerOneEntityCall(data, monkeypatch):
    def refused(*args):
        pytest.fail('the controller must not check the designer again')
    monkeypatch.setattr(InteriorDesignerLoginController, 'login', lambda self, username, password: None)
    monkeypatch.setattr(UserAccount, 'verifyCredentials', refused)
    monkeypatch.setattr(UserAccount, 'getUserAccount', refused)
    calls = []
    monkeypatch.setattr(IDP, 'getCurrentIDP', lambda self, designerId, idpId: calls.append('get') or 'idp')
    monkeypatch.setattr(IDP, 'suspendCurrentIDP', lambda self, designerId, idpId: calls.append('suspend') or True)
    controller = DeleteCurrentIDPController()
    assert controller.getCurrentIDP(data['owner'], data['own']) == 'idp'
    assert controller.deleteCurrentIDP(data['owner'], data['own']) is True
    assert calls == ['get', 'suspend']


def test_ut23_12_confirmationGetIsReadOnly(data, client):
    with client.session_transaction() as state:
        sessionBefore = dict(state)
    before = snapshot()
    response = client.get(deleteUrl(data['own']))
    assert response.status_code == 200
    for text in [b'Own Current Project', b'Initial progress', b'role="dialog"', b'aria-modal="true"',
                 b'Delete current IDP?', b'value="delete"', b'value="cancel"', b'Designer navigation']:
        assert text in response.data
    assert b'type="hidden"' not in response.data and b'Token' not in response.data
    with client.session_transaction() as state:
        assert dict(state) == sessionBefore
    assert snapshot() == before


def test_ut23_13_cancelPreservesData(data, client):
    assert client.get(deleteUrl(data['own'])).status_code == 200
    before = snapshot()
    response = client.post(deleteUrl(data['own']), data=dict(choice='cancel'))
    assert response.status_code == 302 and response.headers['Location'].endswith(f'/current/{data["own"]}')
    assert snapshot() == before


def test_ut23_14_deleteHidesListPreviewAndUpdate(data, client):
    response = client.post(deleteUrl(data['own']), data=dict(choice='delete'), follow_redirects=True)
    assert response.status_code == 200 and b'Current IDP deleted successfully' in response.data
    assert b'Own Current Project' not in response.data
    assert client.get(f'/designer/idps/current/{data["own"]}').status_code == 404
    assert client.get(updateUrl(data['own'])).status_code == 404
    assert client.post(updateUrl(data['own']), data=validData(data)).status_code == 404


def test_ut23_15_lastVisibleProjectGivesEmptyState(data, client):
    response = client.post(deleteUrl(data['own']), data=dict(choice='delete'), follow_redirects=True)
    assert b'Current IDP deleted successfully' in response.data
    assert b'You have no current IDPs to display' in response.data


@pytest.mark.parametrize('method', ['get', 'post'])
def test_ut23_16_signedOutRedirect(data, method):
    before = snapshot()
    response = getattr(app.test_client(), method)(deleteUrl(data['own']))
    assert response.status_code == 302 and response.headers['Location'].endswith('/designer/login')
    assert snapshot() == before


@pytest.mark.parametrize('method', ['get', 'post'])
def test_ut23_17_roleNotCheckedAgain(data, method):
    # admin01 has a session, so the page runs - but the IDP isn't admin01's, so nothing is found
    browser = app.test_client()
    browser.post('/login', data=dict(username='admin01', password='Admin@123'))
    before = snapshot()
    response = getattr(browser, method)(deleteUrl(data['own']), data=dict(choice='delete'))
    assert response.status_code == 404
    assert snapshot() == before


@pytest.mark.parametrize('key', ['foreign', 'past', 'suspended', 'hidden', 'missing'])
@pytest.mark.parametrize('method', ['get', 'post'])
def test_ut23_18_excludedRouteNoDisclosure(data, client, key, method):
    before = snapshot()
    response = getattr(client, method)(deleteUrl(data.get(key, 999999)), data=dict(choice='delete'))
    assert response.status_code == 404
    assert b'Initial progress' not in response.data and b'Other Designer Project' not in response.data
    assert snapshot() == before


@pytest.mark.parametrize('token', [None, 'old', 'forged'])
def test_ut23_19_noConfirmationToken(data, client, token):
    extra = {} if token is None else {'confirmationToken': token}
    if token == 'old':
        assert client.get(deleteUrl(data['own'])).status_code == 200
    response = postDelete(client, data['own'], **extra)
    assert response.status_code == 302 and response.headers['Location'].endswith('/designer/idps/current')
    assert status(data['own']) == 'Suspended'


@pytest.mark.parametrize('choice', ['', 'yes', 'DELETE'])
def test_ut23_20_onlyDeleteChoiceDeletes(data, client, choice):
    before = snapshot()
    response = client.post(deleteUrl(data['own']), data=dict(choice=choice))
    assert response.status_code == 302 and response.headers['Location'].endswith(f'/current/{data["own"]}')
    assert snapshot() == before
    assert status(data['own']) == 'Active'


@pytest.mark.parametrize('change,code', [('account', 302), ('profile', 302), ('permissions', 302),
                                         ('project', 404), ('category', 404), ('past', 404)])
def test_ut23_21_changesAfterBoxOpened(data, client, change, code):
    assert client.get(deleteUrl(data['own'])).status_code == 200
    statements = {
        'account': ("UPDATE user_account SET status='Suspended' WHERE userId=?", data['owner']),
        'profile': ("UPDATE user_profile SET status='Suspended' WHERE profileId=?", 2),
        'permissions': ("UPDATE user_profile SET permissions='[]' WHERE profileId=?", 2),
        'project': ("UPDATE idp SET status='Suspended' WHERE idpId=?", data['own']),
        'category': ("UPDATE idp_category SET status='Suspended' WHERE categoryId=?", data['category']),
        'past': ("UPDATE idp SET projectType='Past' WHERE idpId=?", data['own'])}
    sql, value = statements[change]
    execute(sql, (value,))
    before = snapshot()
    assert postDelete(client, data['own']).status_code == code
    if code == 302:
        # the account isn't checked again (precondition UC13) - the IDP is deleted
        assert status(data['own']) == 'Suspended'
    else:
        assert snapshot() == before


def test_ut23_22_deleteAfterAnEdit(data, client):
    assert client.get(deleteUrl(data['own'])).status_code == 200
    assert client.post(updateUrl(data['own']), data=validData(data)).status_code == 302
    response = postDelete(client, data['own'])
    assert response.status_code == 302
    row = next(row for row in snapshot('idp') if row[0] == data['own'])
    assert row[3] == 'Updated Current Project' and row[7] == 'Suspended'


@pytest.mark.parametrize('change,code', [('edit', 302), ('category', 404)])
def test_ut23_23_changeJustBeforeUpdate(data, client, monkeypatch, change, code):
    original = IDP.suspendCurrentIDP
    def changeThenDelete(self, designerId, idpId):
        if change == 'edit':
            execute("UPDATE idp SET description='New progress' WHERE idpId=?", (idpId,))
        else:
            execute("UPDATE idp_category SET status='Suspended' WHERE categoryId=?", (data['category'],))
        return original(self, designerId, idpId)
    monkeypatch.setattr(IDP, 'suspendCurrentIDP', changeThenDelete)
    assert postDelete(client, data['own']).status_code == code
    assert status(data['own']) == ('Suspended' if change == 'edit' else 'Active')


def test_ut23_24_sameDeleteSentTwice(data, client):
    assert postDelete(client, data['own']).status_code == 302
    before = snapshot()
    response = postDelete(client, data['own'])
    assert response.status_code == 404 and b'Current IDP not found' in response.data
    assert snapshot() == before


def test_ut23_25_confirmationEscapesProjectText(data,client):
    execute("UPDATE idp SET title='<script>alert(1)</script>' WHERE idpId=?",(data['own'],))
    response=client.get(deleteUrl(data['own']))
    assert b'<script>' not in response.data and b'&lt;script&gt;' in response.data


def test_ut23_26_nothingKeptInSession(data, client):
    assert client.get(updateUrl(data['own'])).status_code == 200
    assert client.get(deleteUrl(data['own'])).status_code == 200
    assert postDelete(client, data['own']).status_code == 302
    with client.session_transaction() as state:
        assert set(state) <= {'userId', 'profileId', 'username', '_flashes'}


def test_ut23_27_boxStillOpensAfterProfileSuspended(data, client):
    execute("UPDATE user_profile SET status='Suspended' WHERE profileId=2")
    response = client.get(deleteUrl(data['own']))
    assert response.status_code == 200 and b'Delete current IDP?' in response.data


def test_ut23_28_anotherDesignerCannotDelete(data, client):
    client.post('/designer/logout')
    assert client.post('/designer/login', data=dict(username='other22', password='Design@123')).status_code == 302
    before = snapshot()
    assert postDelete(client, data['own']).status_code == 404
    assert snapshot() == before


def test_ut23_29_getCannotDeleteAndPreviewHasLink(data,client):
    before=snapshot()
    assert client.get(deleteUrl(data['own'])+'?choice=delete').status_code==200
    assert snapshot()==before
    assert client.put(deleteUrl(data['own'])).status_code==405
    assert deleteUrl(data['own']).encode() in client.get(f'/designer/idps/current/{data["own"]}').data


def test_ut23_30_postedMetadataCannotRetarget(data, client):
    otherBefore = IDP().getCurrentIDP(data['other'], data['foreign']).__dict__
    response = client.post(deleteUrl(data['own']), data=dict(choice='delete', designerId=data['other'],
                                                              idpId=data['foreign'], status='Active'))
    assert response.status_code == 302
    assert IDP().getCurrentIDP(data['owner'], data['own']) is None
    assert IDP().getCurrentIDP(data['other'], data['foreign']).__dict__ == otherBefore


def test_ut23_31_longUnicodeDescriptionNotKeptInSession(data, client):
    description = ''.join(chr(0x4e00 + i) for i in range(2000))
    execute('UPDATE idp SET description=? WHERE idpId=?', (description, data['own']))
    response = client.get(deleteUrl(data['own']))
    assert response.status_code == 200
    with client.session_transaction() as state:
        assert set(state) <= {'userId', 'profileId', 'username'}
        assert description[:20] not in str(dict(state))
    assert response.headers.getlist('Set-Cookie') == []


# ---------- system tests (Flask test client) ----------

def test_tc23_8_profileSuspendedAfterBoxOpened(data, client):
    assert client.get(deleteUrl(data['own'])).status_code == 200
    execute("UPDATE user_profile SET status='Suspended' WHERE profileId=2")
    # being logged in is the precondition (UC13), so the delete still goes through
    assert postDelete(client, data['own']).status_code == 302
    assert status(data['own']) == 'Suspended'
    # the next login is refused
    client.post('/designer/logout')
    response = client.post('/designer/login', data=dict(username='update22', password='Design@123'))
    assert b'Invalid login details or access unavailable' in response.data


def test_tc23_9_deleteWithoutOpeningTheBox(data, client):
    response = postDelete(client, data['own'])
    assert response.status_code == 302 and response.headers['Location'].endswith('/designer/idps/current')
    assert status(data['own']) == 'Suspended'


def test_tc23_10_editedAfterTheBoxOpened(data, client):
    assert client.get(deleteUrl(data['own'])).status_code == 200
    assert client.post(updateUrl(data['own']), data=validData(data, title='Changed title')).status_code == 302
    response = postDelete(client, data['own'])
    assert response.status_code == 302 and response.headers['Location'].endswith('/designer/idps/current')
    assert status(data['own']) == 'Suspended'


def test_tc23_11_sentTwiceOrAnotherDesigner(data, client):
    second = execute("INSERT INTO idp (designerId, categoryId, title, description) VALUES (?, ?, 'Second Project', 'Progress')",
                     (data['owner'], data['category']))
    assert postDelete(client, data['own']).status_code == 302
    before = snapshot()
    assert postDelete(client, data['own']).status_code == 404
    other = app.test_client()
    assert other.post('/designer/login', data=dict(username='other22', password='Design@123')).status_code == 302
    assert postDelete(other, second).status_code == 404
    assert snapshot() == before
    assert status(second) == 'Active'
