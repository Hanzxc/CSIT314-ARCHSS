"""US36 customer logout clears current-browser authentication and transient data."""
import pytest

from flask import session

from app import app
from boundary.customerLogoutPage import CustomerLogoutPage
from control.customerLoginController import REQUIRED_CUSTOMER_PERMISSIONS
from control.customerLogoutController import CustomerLogoutController
from control.logoutController import LogoutController
from entity.userAccount import UserAccount
from entity.userProfile import UserProfile
from test_us22_updateCurrentIDP import data, execute, snapshot
from test_us32_viewIDP import projects


@pytest.fixture
def client(projects):
    result = app.test_client()
    result.post('/customer/login', data=dict(username='cust001', password='Cust@123'))
    return result


def test_ut36_1_controllerClearsIdentity():
    with app.test_request_context():
        session.update(userId=3, profileId=3, username='cust001')
        assert CustomerLogoutController().logout() is True
        assert dict(session) == {}


def test_ut36_2_noSession():
    with app.test_request_context():
        assert CustomerLogoutController().logout() is False
        assert dict(session) == {}


def test_ut36_3_repeatedControllerCall():
    with app.test_request_context():
        session['userId'] = 3
        assert CustomerLogoutController().logout() is True
        assert CustomerLogoutController().logout() is False


def test_ut36_4_clearsTransientData():
    with app.test_request_context():
        session.update(userId=3, pendingAction='old', token='old', _flashes=[('error', 'old')])
        CustomerLogoutController().logout()
        assert not session


def test_ut36_5_orphanedData():
    with app.test_request_context():
        session.update(username='cust001', profileId=3, token='orphaned')
        assert CustomerLogoutController().logout() is False
        assert not session


def test_ut36_6_doesNotUseSharedLogout(monkeypatch):
    def refused(self):
        pytest.fail("US36 must not call US2's LogoutController")
    monkeypatch.setattr(LogoutController, 'logout', refused)
    with app.test_request_context():
        session['userId'] = 3
        session['orphaned'] = 'value'
        assert CustomerLogoutController().logout() is True
        assert not session


def test_ut36_7_boundaryDelegates(client, monkeypatch):
    called = []
    def logout(self):
        called.append(True)
        session.clear()
        return True
    monkeypatch.setattr(CustomerLogoutController, 'logout', logout)
    response = client.post('/customer/logout')
    assert called == [True] and response.status_code == 302


def test_ut36_8_dashboardButton(client):
    response = client.get('/customer/dashboard')
    assert b'<form method="POST" action="/customer/logout">' in response.data
    assert b'>Log out</button>' in response.data


def test_ut36_9_searchButton(client):
    assert b'action="/customer/logout"' in client.get('/customer/idps/search').data


def test_ut36_10_detailButton(client, projects):
    assert b'action="/customer/logout"' in client.get(f'/customer/idps/{projects["own"]}').data


def test_ut36_11_unavailablePageButton(client):
    response = client.get('/customer/idps/999999')
    assert response.status_code == 404 and b'action="/customer/logout"' in response.data


def test_ut36_12_redirect(client):
    response = client.post('/customer/logout')
    assert response.status_code == 302
    assert response.headers['Location'].endswith('/customer/login')


def test_ut36_13_successPage(client):
    response = client.post('/customer/logout', follow_redirects=True)
    assert response.status_code == 200 and b'You have logged out successfully' in response.data
    assert b'class="message success"' in response.data and b'role="status"' in response.data
    assert b'action="/customer/login"' in response.data
    assert b'Logged in as' not in response.data


def test_ut36_14_noIdentityRetained(client):
    with client.session_transaction() as state:
        state.update(pendingAction='old', token='old', _flashes=[('error', 'Old message')])
    client.post('/customer/logout')
    with client.session_transaction() as state:
        assert set(state) == {'_flashes'}
        assert state['_flashes'] == [('success', 'You have logged out successfully')]


def test_ut36_15_anonymousLogout(projects):
    response = app.test_client().post('/customer/logout', follow_redirects=True)
    assert response.status_code == 200 and b'Your session has already ended' in response.data
    assert b'class="message info"' in response.data


def test_ut36_16_secondLogout(client):
    client.post('/customer/logout', follow_redirects=True)
    response = client.post('/customer/logout', follow_redirects=True)
    assert b'Your session has already ended' in response.data


@pytest.mark.parametrize('method', ['get', 'put', 'patch', 'delete'])
def test_ut36_17_methodsDoNotLogout(client, method):
    assert getattr(client, method)('/customer/logout').status_code == 405
    assert client.get('/customer/dashboard').status_code == 200


@pytest.mark.parametrize('path', ['/customer/dashboard', '/customer/idps/search', '/customer/idps/1'])
def test_ut36_18_protectedRoutesAfterLogout(client, path):
    client.post('/customer/logout', follow_redirects=True)
    response = client.get(path)
    assert response.status_code == 302 and response.headers['Location'].endswith('/customer/login')


@pytest.mark.parametrize('sql', [
    "UPDATE user_account SET status='Suspended' WHERE username='cust001'",
    "UPDATE user_profile SET status='Suspended' WHERE profileId=3",
    "UPDATE user_profile SET permissions='[]' WHERE profileId=3",
    "DELETE FROM user_account WHERE username='cust001'"])
def test_ut36_19_logoutAfterAccessRevoked(client, sql):
    execute(sql)
    response = client.post('/customer/logout', follow_redirects=True)
    assert b'You have logged out successfully' in response.data
    with client.session_transaction() as state:
        assert not state


def test_ut36_20_loginAgain(client, projects):
    client.post('/customer/logout', follow_redirects=True)
    response = client.post('/customer/login', data=dict(username='cust001', password='Cust@123'))
    assert response.headers['Location'].endswith('/customer/dashboard')
    assert client.get(f'/customer/idps/{projects["own"]}').status_code == 200


def test_ut36_21_anotherBrowserUnaffected(client):
    second = app.test_client()
    second.post('/customer/login', data=dict(username='cust001', password='Cust@123'))
    client.post('/customer/logout', follow_redirects=True)
    assert client.get('/customer/dashboard').status_code == 302
    assert second.get('/customer/dashboard').status_code == 200


def test_ut36_22_noDatabaseChanges(client):
    before = snapshot()
    client.post('/customer/logout', follow_redirects=True)
    assert snapshot() == before
    assert UserAccount().verifyCredentials('cust001', 'Cust@123', REQUIRED_CUSTOMER_PERMISSIONS) is not None


def test_ut36_23_noStore(client):
    response = client.post('/customer/logout', follow_redirects=True)
    assert response.headers['Cache-Control'] == 'no-store'
    assert response.history[0].headers['Cache-Control'] == 'no-store'
    assert client.get('/customer/dashboard').headers['Cache-Control'] == 'no-store'


def test_ut36_24_genericLogoutStillWorks(projects):
    admin = app.test_client()
    admin.post('/login', data=dict(username='admin01', password='Admin@123'))
    response = admin.post('/logout')
    assert b'You have logged out successfully' in response.data
    assert admin.get('/dashboard').status_code == 302


def test_ut36_25_designerLogoutStillWorks(projects):
    designer = app.test_client()
    designer.post('/designer/login', data=dict(username='update22', password='Design@123'))
    response = designer.post('/designer/logout')
    assert response.headers['Location'].endswith('/designer/login')
    assert designer.get('/designer/dashboard').status_code == 302


def test_ut36_26_messageShownOnce(client):
    response = client.post('/customer/logout', follow_redirects=True)
    assert b'You have logged out successfully' in response.data
    assert b'You have logged out successfully' not in client.get('/customer/login').data


def test_ut36_27_ignoresSubmittedIdentityAndReturnUrl(client):
    response = client.post('/customer/logout?next=https://example.test', data=dict(
        userId=1, username='admin01', returnUrl='https://example.test'))
    assert response.headers['Location'].endswith('/customer/login')
    client.get('/customer/login')
    with client.session_transaction() as state:
        assert not state


def test_ut36_28_noEntityAccessNeeded(client, monkeypatch):
    def forbidden(*args): pytest.fail('Logout must work without reading account/profile')
    monkeypatch.setattr(UserAccount, 'getUserAccount', forbidden)
    monkeypatch.setattr(UserProfile, 'getUserProfile', forbidden)
    assert client.post('/customer/logout', follow_redirects=True).status_code == 200


def test_ut36_29_cookieRemovedAfterMessage(client):
    assert client.get_cookie('session') is not None
    response = client.post('/customer/logout', follow_redirects=True)
    assert client.get_cookie('session') is None
    assert 'Expires=Thu, 01 Jan 1970' in response.headers['Set-Cookie']


def test_ut36_30_orphanedBrowserSession(projects):
    client = app.test_client()
    with client.session_transaction() as state:
        state.update(username='cust001', profileId=3, pendingAction='orphaned')
    response = client.post('/customer/logout', follow_redirects=True)
    assert b'Your session has already ended' in response.data
    with client.session_transaction() as state:
        assert not state
