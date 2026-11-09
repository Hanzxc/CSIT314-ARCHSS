"""US30 uses the isolated seeded database from conftest, never the demo DB."""
import json

import pytest

from app import app
from boundary.customerLoginPage import CustomerLoginPage
from control.customerLoginController import CustomerLoginController
from database.db import getConnection
from entity.userAccount import UserAccount


@pytest.fixture
def client():
    return app.test_client()


def change(sql, params=()):
    conn = getConnection()
    try:
        conn.execute(sql, params)
        conn.commit()
    finally:
        conn.close()


def login(client, **extra):
    return client.post('/customer/login', data={
        'username': 'cust001', 'password': 'Cust@123', **extra})


def test_ut30_1_correctCustomer():
    account = CustomerLoginController().login('cust001', 'Cust@123')
    assert account.username == 'cust001' and account.profileId == 3


@pytest.mark.parametrize('username,password', [
    ('cust001', 'wrong'), ('unknown', 'Cust@123'),
    ("' OR 1=1 --", 'Cust@123'), ('cust001', "' OR 1=1 --")])
def test_ut30_2_invalidCredentials(username, password):
    assert CustomerLoginController().login(username, password) is None


@pytest.mark.parametrize('username,password', [('', 'x'), ('   ', 'x'),
    (None, 'x'), ('cust001', ''), ('cust001', None)])
def test_ut30_3_emptyControllerInput(username, password, monkeypatch):
    def forbidden(*args):
        pytest.fail('Empty input must not query credentials')
    monkeypatch.setattr(UserAccount, 'verifyCredentials', forbidden)
    assert CustomerLoginController().login(username, password) is None


def test_ut30_4_suspendedAccount():
    change("UPDATE user_account SET status='Suspended' WHERE username='cust001'")
    assert CustomerLoginController().login('cust001', 'Cust@123') is None


def test_ut30_5_suspendedProfile():
    change("UPDATE user_profile SET status='Suspended' WHERE profileId=3")
    assert CustomerLoginController().login('cust001', 'Cust@123') is None


def test_ut30_6_missingPermission():
    change('UPDATE user_profile SET permissions=? WHERE profileId=3', ('[]',))
    assert CustomerLoginController().login('cust001', 'Cust@123') is None


def test_ut30_7_missingProfile(monkeypatch):
    from entity.userProfile import UserProfile
    monkeypatch.setattr(UserProfile, 'getUserProfile', lambda *args: None)
    assert CustomerLoginController().login('cust001', 'Cust@123') is None


@pytest.mark.parametrize('profileId', [1, 2, 4])
def test_ut30_8_otherRoles(profileId):
    UserAccount().createUserAccount(UserAccount(username='other30', password='Other@123', fullName='Other', email='other@x.test', phone='', profileId=profileId))
    assert CustomerLoginController().login('other30', 'Other@123') is None


def test_ut30_9_permissionBasedRole():
    change('UPDATE user_profile SET profileName=? WHERE profileId=3', ('Home Owner',))
    assert CustomerLoginController().login('cust001', 'Cust@123') is not None


def test_ut30_10_exactCredentials():
    assert CustomerLoginController().login('CUST001', 'Cust@123') is None
    assert CustomerLoginController().login(' cust001 ', 'Cust@123') is None
    assert CustomerLoginController().login('cust001', ' Cust@123 ') is None
    UserAccount().createUserAccount(UserAccount(username='spaces30', password=' with spaces ', fullName='Spaces', email='s@x.test', phone='', profileId=3))
    assert CustomerLoginController().login('spaces30', ' with spaces ') is not None


def test_ut30_11_getAuthenticatedCustomer():
    account = CustomerLoginController().login('cust001', 'Cust@123')
    assert CustomerLoginController().getAuthenticatedCustomer(account.userId).username == 'cust001'
    assert CustomerLoginController().getAuthenticatedCustomer(-1) is None
    assert CustomerLoginController().isCustomer(None) is False


@pytest.mark.parametrize('username,password,expected', [
    ('', 'x', False), (' ', 'x', False), (None, 'x', False),
    ('cust001', '', False), ('cust001', None, False), ('cust001', 'Cust@123', True)])
def test_ut30_12_validateInput(username, password, expected):
    assert CustomerLoginPage().validateInput(username, password) is expected


def test_ut30_13_loginForm(client):
    response = client.get('/customer/login')
    assert response.status_code == 200
    assert b'Customer' in response.data and b'action="/customer/login"' in response.data
    assert b'type="password"' in response.data and b'autocomplete="current-password"' in response.data
    assert b'Cache-Control' not in response.data
    assert response.headers['Cache-Control'] == 'no-store'


def test_ut30_14_missingFieldsSkipsControl(client, monkeypatch):
    def forbidden(*args):
        pytest.fail('Empty input must not call the controller')
    monkeypatch.setattr(CustomerLoginController, 'login', forbidden)
    response = client.post('/customer/login', data={})
    assert response.status_code == 200
    assert b'Please enter your username and password' in response.data
    with client.session_transaction() as state:
        assert 'userId' not in state


def test_ut30_15_successFreshSession(client):
    with client.session_transaction() as state:
        state.update(userId=1, profileId=1, username='admin01', staleToken='old', password='old')
    response = login(client)
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/customer/dashboard')
    with client.session_transaction() as state:
        assert set(state) == {'userId', 'profileId', 'username'}
        assert state['username'] == 'cust001' and state['profileId'] == 3


@pytest.mark.parametrize('mutation', ['wrong', 'unknown', 'account', 'profile', 'permission', 'admin'])
def test_ut30_16_genericFailure(client, mutation):
    data = {}
    if mutation == 'wrong': data['password'] = 'bad'
    if mutation == 'unknown': data['username'] = 'nobody'
    if mutation == 'account': change("UPDATE user_account SET status='Suspended' WHERE username='cust001'")
    if mutation == 'profile': change("UPDATE user_profile SET status='Suspended' WHERE profileId=3")
    if mutation == 'permission': change("UPDATE user_profile SET permissions='[]' WHERE profileId=3")
    if mutation == 'admin': data = dict(username='admin01', password='Admin@123')
    response = login(client, **data)
    assert response.status_code == 200
    assert b'Invalid login details or access unavailable' in response.data
    assert b'Cust@123' not in response.data
    with client.session_transaction() as state:
        assert 'userId' not in state


def test_ut30_17_dashboard(client):
    login(client)
    response = client.get('/customer/dashboard')
    assert response.status_code == 200
    assert b'Welcome back, cust001' in response.data and b'Saved IDPs' in response.data
    assert b'href="/customer/saved-list"' in response.data
    assert b'User Accounts' not in response.data and b'Company Profile' not in response.data
    assert response.headers['Cache-Control'] == 'no-store'


def test_ut30_18_dashboardNoSession(client):
    assert client.get('/customer/dashboard').headers['Location'].endswith('/customer/login')


@pytest.mark.parametrize('profileId', [1, 2, 4])
def test_ut30_19_dashboardOtherRole(client, profileId):
    UserAccount().createUserAccount(UserAccount(username='other30', password='Other@123', fullName='Other', email='other@x.test', phone='', profileId=profileId))
    account = UserAccount().verifyCredentials('other30', 'Other@123')
    with client.session_transaction() as state:
        state.update(userId=account.userId, username=account.username, profileId=profileId)
    response = client.get('/customer/dashboard')
    assert response.status_code == 403
    assert b'Access unavailable' in response.data


@pytest.mark.parametrize('sql', [
    "UPDATE user_account SET status='Suspended' WHERE username='cust001'",
    "UPDATE user_profile SET status='Suspended' WHERE profileId=3",
    "UPDATE user_profile SET permissions='[]' WHERE profileId=3",
    "UPDATE user_account SET profileId=1 WHERE username='cust001'",
    "DELETE FROM user_account WHERE username='cust001'"])
def test_ut30_20_accessRevokedAfterLogin(client, sql):
    login(client)
    change(sql)
    assert client.get('/customer/dashboard').status_code == 403


def test_ut30_21_forgedSessionMetadata(client):
    login(client)
    with client.session_transaction() as state:
        state.update(username='admin01', profileId=1)
    response = client.get('/customer/dashboard')
    assert b'Welcome back, cust001' in response.data
    change("UPDATE user_account SET profileId=1 WHERE username='cust001'")
    with client.session_transaction() as state:
        state['profileId'] = 3
    assert client.get('/customer/dashboard').status_code == 403


def test_ut30_22_sharedLogin(client):
    # /login is only for User Admins (US1) - customers get the error there and use /customer/login
    response = client.post('/login', data=dict(username='cust001', password='Cust@123'))
    assert b'Invalid login details or account suspended' in response.data
    assert client.get('/dashboard').headers['Location'].endswith('/login')


def test_ut30_23_sharedAdminUnchanged(client):
    response = client.post('/login', data=dict(username='admin01', password='Admin@123'))
    assert response.headers['Location'].endswith('/dashboard')
    assert client.get('/accounts').status_code == 200


# the User Admin pages (/accounts, /profiles) aren't here any more: their loginRequired only checks
# there's a session, because logged in as a User Admin is their precondition (US1)
@pytest.mark.parametrize('path', ['/designer/dashboard', '/manager/dashboard'])
def test_ut30_24_otherAreasDenied(client, path):
    login(client)
    assert client.get(path).status_code == 403


def test_ut30_25_existingLogout(client):
    login(client)
    assert client.post('/logout').status_code == 200
    with client.session_transaction() as state:
        assert 'userId' not in state
    assert client.get('/customer/dashboard').headers['Location'].endswith('/customer/login')


def test_ut30_26_escaping(client):
    UserAccount().createUserAccount(UserAccount(username='<script>x</script>', password='Secret@123', fullName='X', email='x@x.test', phone='', profileId=3))
    login(client, username='<script>x</script>', password='Secret@123')
    response = client.get('/customer/dashboard')
    assert b'&lt;script&gt;x&lt;/script&gt;' in response.data
    assert b'<script>' not in response.data and b'Secret@123' not in response.data


def test_ut30_27_noDatabaseWrites(client):
    conn = getConnection()
    before = '\n'.join(conn.iterdump())
    conn.close()
    login(client)
    client.get('/customer/dashboard')
    login(client, password='wrong')
    conn = getConnection()
    assert '\n'.join(conn.iterdump()) == before
    conn.close()


@pytest.mark.parametrize('path,method', [('/customer/login', 'put'),
    ('/customer/login', 'delete'), ('/customer/dashboard', 'post')])
def test_ut30_28_unsupportedMethods(client, path, method):
    assert getattr(client, method)(path).status_code == 405


def test_ut30_29_failedAttemptDoesNotReplaceSession(client):
    login(client)
    with client.session_transaction() as state:
        before = dict(state)
    login(client, username='admin01', password='bad')
    with client.session_transaction() as state:
        assert dict(state) == before


def test_ut30_30_noCredentialsInSession(client):
    login(client)
    with client.session_transaction() as state:
        assert 'Cust@123' not in json.dumps(dict(state))
        assert UserAccount().verifyCredentials('cust001', 'Cust@123').password not in json.dumps(dict(state))
