import re

import pytest

from app import app
from control.deleteCurrentIDPController import DeleteCurrentIDPController
from entity.idp import IDP
from test_us22_updateCurrentIDP import data, client, execute, snapshot, validData, formToken, updateUrl


def deleteUrl(idpId):
    return f"/designer/idps/current/{idpId}/delete"


def confirmationToken(client, idpId):
    response = client.get(deleteUrl(idpId))
    assert response.status_code == 200
    return re.search(rb'name="confirmationToken" value="([^"]+)"', response.data).group(1).decode()


def expectedData(data):
    project = IDP().getCurrentIDP(data['owner'], data['own'])
    return project.getSnapshot()


@pytest.mark.parametrize('condition', ['active', 'account', 'profile', 'permissions', 'admin', 'customer', 'missing'])
def test_ut23_1_designerAccess(data, condition):
    owner = data['owner']
    if condition == 'account':execute("UPDATE user_account SET status='Suspended' WHERE userId=?", (owner,))
    elif condition == 'profile':execute("UPDATE user_profile SET status='Suspended' WHERE profileId=2")
    elif condition == 'permissions':execute("UPDATE user_profile SET permissions='[]' WHERE profileId=2")
    elif condition != 'active':owner = {'admin': 1, 'customer': 3, 'missing': 999999}[condition]
    assert DeleteCurrentIDPController().canDeleteCurrentIDP(owner) == (condition == 'active')


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


def test_ut23_7_matchingSnapshot(data):
    assert IDP().suspendCurrentIDP(data['owner'], data['own'], expectedData(data)) is True


@pytest.mark.parametrize('field,value', [('title', 'Revised Project'), ('description', 'New progress'),
                                        ('location', 'Bedok'), ('categoryId', 2), ('createdDate', '2000-01-01')])
def test_ut23_8_changedSnapshotCannotDelete(data, field, value):
    reviewed = expectedData(data)
    execute('UPDATE idp SET ' + field + '=? WHERE idpId=?', (value, data['own']))
    before = snapshot()
    assert IDP().suspendCurrentIDP(data['owner'], data['own'], reviewed) is False
    assert snapshot() == before


def test_ut23_9_incompleteSnapshotCannotDelete(data):
    before = snapshot()
    assert IDP().suspendCurrentIDP(data['owner'], data['own'], '') is False
    assert snapshot() == before


def test_ut23_10_controllerDeletesOwnProject(data):
    assert DeleteCurrentIDPController().deleteCurrentIDP(data['owner'], data['own'], expectedData(data)) is True
    assert IDP().getCurrentIDP(data['owner'], data['own']) is None


@pytest.mark.parametrize('operation', ['get', 'delete'])
def test_ut23_11_controllerDenialStopsQueries(data, monkeypatch, operation):
    monkeypatch.setattr(DeleteCurrentIDPController, 'canDeleteCurrentIDP', lambda *args: False)
    def unexpected(*args):pytest.fail('Denied access must stop before entity queries')
    monkeypatch.setattr(IDP, 'getCurrentIDP', unexpected)
    monkeypatch.setattr(IDP, 'suspendCurrentIDP', unexpected)
    controller = DeleteCurrentIDPController()
    with pytest.raises(PermissionError):
        if operation == 'get':controller.getCurrentIDP(data['owner'], data['own'])
        else:controller.deleteCurrentIDP(data['owner'], data['own'])


def test_ut23_12_confirmationGetIsReadOnlyAndUsesTemplate(data, client):
    before = snapshot()
    response = client.get(deleteUrl(data['own']))
    for text in [b'Own Current Project', b'Initial progress', b'role="dialog"', b'aria-modal="true"',
                 b'Delete current IDP?', b'value="delete"', b'value="cancel"', b'name="confirmationToken"', b'Designer navigation']:
        assert text in response.data
    assert response.status_code == 200 and snapshot() == before


def test_ut23_13_cancelPreservesData(data, client):
    token = confirmationToken(client, data['own'])
    before = snapshot()
    response = client.post(deleteUrl(data['own']), data=dict(choice='cancel', confirmationToken=token))
    assert response.status_code == 302 and response.headers['Location'].endswith(f'/current/{data["own"]}')
    assert snapshot() == before
    with client.session_transaction() as session:assert 'currentIDPDeleteConfirmation' not in session


def test_ut23_14_deleteHidesListPreviewAndUpdate(data, client):
    token = confirmationToken(client, data['own'])
    response = client.post(deleteUrl(data['own']), data=dict(choice='delete', confirmationToken=token), follow_redirects=True)
    assert response.status_code == 200 and b'Current IDP deleted successfully' in response.data
    assert b'Own Current Project' not in response.data
    assert client.get(f'/designer/idps/current/{data["own"]}').status_code == 404
    assert client.get(updateUrl(data['own'])).status_code == 404
    assert client.post(updateUrl(data['own']), data=validData(data)).status_code == 404


def test_ut23_15_lastVisibleProjectGivesEmptyState(data, client):
    token = confirmationToken(client, data['own'])
    response = client.post(deleteUrl(data['own']), data=dict(choice='delete', confirmationToken=token), follow_redirects=True)
    assert b'You have no current IDPs to display' in response.data


@pytest.mark.parametrize('method', ['get', 'post'])
def test_ut23_16_signedOutRedirect(data, method):
    before = snapshot()
    response = getattr(app.test_client(), method)(deleteUrl(data['own']))
    assert response.status_code == 302 and response.headers['Location'].endswith('/designer/login')
    assert snapshot() == before


@pytest.mark.parametrize('method', ['get', 'post'])
def test_ut23_17_nonDesignerForbidden(data, method):
    browser = app.test_client()
    browser.post('/login', data=dict(username='admin01', password='Admin@123'))
    before = snapshot()
    assert getattr(browser, method)(deleteUrl(data['own'])).status_code == 403
    assert snapshot() == before


@pytest.mark.parametrize('key', ['foreign', 'past', 'suspended', 'hidden', 'missing'])
@pytest.mark.parametrize('method', ['get', 'post'])
def test_ut23_18_excludedRouteNoDisclosure(data, client, key, method):
    before = snapshot()
    response = getattr(client, method)(deleteUrl(data.get(key, 999999)))
    assert response.status_code == 404
    assert b'Initial progress' not in response.data and b'Other Designer Project' not in response.data
    assert snapshot() == before


@pytest.mark.parametrize('kind', ['missing', 'forged', 'unicode', 'stale'])
def test_ut23_19_badConfirmationToken(data, client, kind):
    token = confirmationToken(client, data['own'])
    if kind == 'missing':token = ''
    elif kind == 'forged':token = 'not-the-token'
    elif kind == 'unicode':token = '无效'
    else:confirmationToken(client, data['own'])
    before = snapshot()
    assert client.post(deleteUrl(data['own']), data=dict(choice='delete', confirmationToken=token)).status_code == 403
    assert snapshot() == before


@pytest.mark.parametrize('choice', ['', 'yes', 'DELETE'])
def test_ut23_20_explicitDeleteChoiceRequired(data, client, choice):
    token = confirmationToken(client, data['own'])
    before = snapshot()
    assert client.post(deleteUrl(data['own']), data=dict(choice=choice, confirmationToken=token)).status_code == 400
    assert snapshot() == before


@pytest.mark.parametrize('change,status', [('account',403),('profile',403),('permissions',403),
                                         ('project',404),('category',404),('past',404)])
def test_ut23_21_rechecksAtConfirmation(data, client, change, status):
    token = confirmationToken(client, data['own'])
    statements = {
        'account':("UPDATE user_account SET status='Suspended' WHERE userId=?",data['owner']),
        'profile':("UPDATE user_profile SET status='Suspended' WHERE profileId=?",2),
        'permissions':("UPDATE user_profile SET permissions='[]' WHERE profileId=?",2),
        'project':("UPDATE idp SET status='Suspended' WHERE idpId=?",data['own']),
        'category':("UPDATE idp_category SET status='Suspended' WHERE categoryId=?",data['category']),
        'past':("UPDATE idp SET projectType='Past' WHERE idpId=?",data['own'])}
    sql,value = statements[change];execute(sql,(value,))
    before = snapshot()
    assert client.post(deleteUrl(data['own']), data=dict(choice='delete',confirmationToken=token)).status_code == status
    assert snapshot() == before


def test_ut23_22_editAfterConfirmationNeedsFreshReview(data, client):
    token = confirmationToken(client, data['own'])
    updateToken = formToken(client, data['own'])
    assert client.post(updateUrl(data['own']), data={**validData(data),'updateToken':updateToken}).status_code == 302
    before = snapshot()
    response = client.post(deleteUrl(data['own']),data=dict(choice='delete',confirmationToken=token))
    assert response.status_code == 409 and b'This IDP changed' in response.data
    assert snapshot() == before
    token = confirmationToken(client,data['own'])
    assert client.post(deleteUrl(data['own']),data=dict(choice='delete',confirmationToken=token)).status_code == 302


@pytest.mark.parametrize('change,status',[('edit',409),('category',404)])
def test_ut23_23_atomicGuard(data,client,monkeypatch,change,status):
    token=confirmationToken(client,data['own'])
    original=IDP.suspendCurrentIDP
    def changeThenDelete(self,designerId,idpId,expectedSnapshot=None):
        if change=='edit':execute("UPDATE idp SET description='New progress' WHERE idpId=?",(idpId,))
        else:execute("UPDATE idp_category SET status='Suspended' WHERE categoryId=?",(data['category'],))
        return original(self,designerId,idpId,expectedSnapshot)
    monkeypatch.setattr(IDP,'suspendCurrentIDP',changeThenDelete)
    assert client.post(deleteUrl(data['own']),data=dict(choice='delete',confirmationToken=token)).status_code==status
    row=next(row for row in snapshot('idp') if row[0]==data['own'])
    assert row[7]=='Active'


@pytest.mark.parametrize('firstChoice,repeatStatus',[('cancel',403),('delete',404)])
def test_ut23_24_confirmationSingleUse(data,client,firstChoice,repeatStatus):
    token=confirmationToken(client,data['own'])
    assert client.post(deleteUrl(data['own']),data=dict(choice=firstChoice,confirmationToken=token)).status_code==302
    before=snapshot()
    assert client.post(deleteUrl(data['own']),data=dict(choice='delete',confirmationToken=token)).status_code==repeatStatus
    assert snapshot()==before


def test_ut23_25_confirmationEscapesProjectText(data,client):
    execute("UPDATE idp SET title='<script>alert(1)</script>' WHERE idpId=?",(data['own'],))
    response=client.get(deleteUrl(data['own']))
    assert b'<script>' not in response.data and b'&lt;script&gt;' in response.data


def test_ut23_26_oldUpdateTokenRemoved(data,client):
    formToken(client,data['own'])
    token=confirmationToken(client,data['own'])
    client.post(deleteUrl(data['own']),data=dict(choice='delete',confirmationToken=token))
    with client.session_transaction() as session:assert str(data['own']) not in session.get('currentIDPUpdateTokens',{})


def test_ut23_27_recheckFailureHandled(data,client,monkeypatch):
    checks=iter([True,False])
    monkeypatch.setattr(DeleteCurrentIDPController,'canDeleteCurrentIDP',lambda *args:next(checks))
    assert client.get(deleteUrl(data['own'])).status_code==403


def test_ut23_28_confirmationBoundToTargetAndSession(data,client):
    token=confirmationToken(client,data['own'])
    second=execute("INSERT INTO idp (designerId,categoryId,title,description) VALUES (?,?,'Second Project','Progress')",
                   (data['owner'],data['category']))
    before=snapshot()
    assert client.post(deleteUrl(second),data=dict(choice='delete',confirmationToken=token)).status_code==403
    client.post('/designer/logout')
    client.post('/designer/login',data=dict(username='other22',password='Design@123'))
    assert client.post(deleteUrl(data['foreign']),data=dict(choice='delete',confirmationToken=token)).status_code==403
    assert snapshot()==before


def test_ut23_29_getCannotDeleteAndPreviewHasLink(data,client):
    before=snapshot()
    assert client.get(deleteUrl(data['own'])+'?choice=delete').status_code==200
    assert snapshot()==before
    assert client.put(deleteUrl(data['own'])).status_code==405
    assert deleteUrl(data['own']).encode() in client.get(f'/designer/idps/current/{data["own"]}').data


def test_ut23_30_postedMetadataCannotRetarget(data,client):
    token=confirmationToken(client,data['own'])
    otherBefore=IDP().getCurrentIDP(data['other'],data['foreign']).__dict__
    response=client.post(deleteUrl(data['own']),data=dict(choice='delete',confirmationToken=token,
        designerId=data['other'],idpId=data['foreign'],status='Active',expectedData='forged'))
    assert response.status_code==302
    assert IDP().getCurrentIDP(data['owner'],data['own']) is None
    assert IDP().getCurrentIDP(data['other'],data['foreign']).__dict__==otherBefore


def test_ut23_31_confirmationStaysCompactForLongUnicodeDescription(data,client):
    description=''.join(chr(0x4e00+i) for i in range(2000))
    execute('UPDATE idp SET description=? WHERE idpId=?',(description,data['own']))
    response=client.get(deleteUrl(data['own']))
    assert response.status_code==200
    with client.session_transaction() as session:
        confirmation=session['currentIDPDeleteConfirmation']
        assert len(confirmation['expectedSnapshot'])==64
        assert description not in str(confirmation)
    assert all(len(header)<4093 for header in response.headers.getlist('Set-Cookie'))
