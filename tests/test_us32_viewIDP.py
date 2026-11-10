"""US32 customer detail view uses isolated database fixtures."""
import inspect

import pytest

from app import app
from control.customerLoginController import CustomerLoginController, REQUIRED_CUSTOMER_PERMISSIONS
from control.viewCompanyProfileController import ViewCompanyProfileController
from control.viewIDPController import ViewIDPController
from database.db import getConnection
from entity.companyProfile import CompanyProfile
from entity.idp import IDP
from entity.idpAnalytics import IDPAnalytics
from entity.savedIDP import SavedIDP
from entity.userAccount import UserAccount
from test_us22_updateCurrentIDP import data, execute, snapshot


@pytest.fixture
def projects(data):
    company = execute('INSERT INTO company_profile (designerId,companyName,description,services,email,phone,address) '
        'VALUES (?,?,?,?,?,?,?)', (data['owner'], 'Studio Thirty Two', 'Thoughtful home interiors.',
        'Space planning and carpentry.', 'private-business@example.test', '12345678', 'Office address'))
    return {**data, 'company': company,
            'customer': UserAccount().verifyCredentials('cust001', 'Cust@123', REQUIRED_CUSTOMER_PERMISSIONS).userId}


@pytest.fixture
def client(projects):
    result = app.test_client()
    result.post('/customer/login', data=dict(username='cust001', password='Cust@123'))
    return result


def url(idpId):
    return f'/customer/idps/{idpId}'


def viewRows(idpId=None):
    conn = getConnection()
    try:
        if idpId is None:
            return conn.execute('SELECT COUNT(*) FROM idp_view').fetchone()[0]
        return conn.execute('SELECT COUNT(*) FROM idp_view WHERE idpId=?', (idpId,)).fetchone()[0]
    finally:
        conn.close()


def spyCompanyProfile(monkeypatch):
    # records what the borrowed US15 controller is asked for and what it gives back
    calls = []
    original = ViewCompanyProfileController.viewCompanyProfile
    def spy(self, designerId):
        company = original(self, designerId)
        calls.append((designerId, company))
        return company
    monkeypatch.setattr(ViewCompanyProfileController, 'viewCompanyProfile', spy)
    return calls


def test_ut32_1_currentProject(projects):
    p = IDP().viewIDP(projects['own'], False)
    assert p.title == 'Own Current Project' and p.categoryName == 'Living Room'
    assert p.projectType == 'Current' and p.location == 'Tampines'


def test_ut32_2_pastProject(projects):
    assert IDP().viewIDP(projects['past'], False).projectType == 'Past'


def test_ut32_3_anotherDesigner(projects):
    assert IDP().viewIDP(projects['foreign'], False).designerId == projects['other']


@pytest.mark.parametrize('key', ['suspended', 'hidden', 'missing'])
def test_ut32_4_hiddenOrMissingEntity(projects, key):
    assert IDP().viewIDP(projects.get(key, 999999), True) is None
    assert viewRows() == 0


@pytest.mark.parametrize('value', [-1, 0, 999999, "1 OR 1=1", None])
def test_ut32_5_invalidEntityId(projects, value):
    before = snapshot()
    assert IDP().viewIDP(value, True) is None
    assert snapshot() == before


def test_ut32_6_controllerOneEntityCall(projects, monkeypatch):
    calls = []
    monkeypatch.setattr(IDP, 'viewIDP', lambda self, idpId, countView: calls.append((idpId, countView)) or 'idp')
    def unexpected(*args): pytest.fail('the controller must not look up the company')
    monkeypatch.setattr(CompanyProfile, 'getCompanyProfile', unexpected)
    assert ViewIDPController().viewIDP(projects['own'], True) == 'idp'
    assert calls == [(projects['own'], True)]


def test_ut32_7_missingCompany(client, projects, monkeypatch):
    calls = spyCompanyProfile(monkeypatch)
    response = client.get(url(projects['foreign']))
    assert calls == [(projects['other'], None)]
    assert response.status_code == 200 and b'Other Designer Project' in response.data


def test_ut32_8_suspendedCompany(client, projects, monkeypatch):
    execute("UPDATE company_profile SET status='Suspended' WHERE companyId=?", (projects['company'],))
    calls = spyCompanyProfile(monkeypatch)
    response = client.get(url(projects['own']))
    assert calls == [(projects['owner'], None)]
    assert b'Designer information is not currently available.' in response.data


def test_ut32_9_controllerDoesNotCheckCustomer(projects, monkeypatch):
    def refused(*args): pytest.fail('the controller must not check the customer again')
    monkeypatch.setattr(CustomerLoginController, 'login', refused)
    monkeypatch.setattr(UserAccount, 'getUserAccount', refused)
    assert list(inspect.signature(ViewIDPController.viewIDP).parameters) == ['self', 'idpId', 'countView']
    # no session / customerId at all - still one entity call, no error
    assert ViewIDPController().viewIDP(projects['own'], False).idpId == projects['own']
    assert ViewIDPController().viewIDP(999999, False) is None


def test_ut32_10_hiddenSkipsCompanyLookup(client, projects, monkeypatch):
    def unexpected(*args): pytest.fail('an unavailable IDP must not look up the company')
    monkeypatch.setattr(ViewCompanyProfileController, 'viewCompanyProfile', unexpected)
    assert client.get(url(projects['hidden'])).status_code == 404


def test_ut32_11_companyUsesSavedOwner(client, projects, monkeypatch):
    calls = spyCompanyProfile(monkeypatch)
    client.get(url(projects['foreign']), query_string=dict(designerId=projects['owner']))
    assert [designerId for designerId, company in calls] == [projects['other']]


def test_ut32_12_normalViewAddsOneRow(client, projects):
    assert client.get(url(projects['own'])).status_code == 200
    assert viewRows(projects['own']) == 1 and viewRows() == 1


def test_ut32_13_fullDetailsPage(client, projects):
    description = 'Full project description.\n' + 'x'*1900
    execute('UPDATE idp SET description=? WHERE idpId=?', (description, projects['own']))
    response = client.get(url(projects['own']))
    assert response.status_code == 200
    for text in ('Own Current Project', 'Living Room', 'Tampines', 'Current', description,
                 'Studio Thirty Two', 'Thoughtful home interiors.', 'Space planning and carpentry.'):
        assert text.encode() in response.data
    assert b'white-space: pre-wrap' in response.data
    assert b'Update current IDP' not in response.data and b'Delete current IDP' not in response.data
    assert b'private-business@example.test' not in response.data
    assert b'Office address' not in response.data and b'Design@123' not in response.data
    assert response.headers['Cache-Control'] == 'no-store'


def test_ut32_14_noSession(projects):
    response = app.test_client().get(url(projects['own']))
    assert response.status_code == 302 and response.headers['Location'].endswith('/customer/login')


@pytest.mark.parametrize('profileId', [1, 2, 4])
def test_ut32_15_roleNotCheckedAgain(projects, profileId):
    # being a customer is the precondition (customerLoginRequired only checks there's a session)
    client = app.test_client()
    with client.session_transaction() as state:
        state.update(userId=1, username='other32', profileId=profileId)
    response = client.get(url(projects['own']))
    assert response.status_code == 200 and b'Own Current Project' in response.data


@pytest.mark.parametrize('key', ['suspended', 'hidden', 'missing'])
def test_ut32_16_notFoundPage(client, projects, key):
    response = client.get(url(projects.get(key, 999999)), query_string=dict(keyword='kitchen'))
    assert response.status_code == 404 and b'This IDP is not available.' in response.data
    assert b'Initial progress' not in response.data and b'Studio Thirty Two' not in response.data
    assert b'keyword=kitchen' in response.data


@pytest.mark.parametrize('value', ['-1', '0', '999999', 'abc', '1%20OR%201=1'])
def test_ut32_17_badUrlId(client, value):
    assert client.get(url(value)).status_code == 404


def test_ut32_18_noCompanyPage(client, projects):
    response = client.get(url(projects['foreign']))
    assert response.status_code == 200 and b'Other Designer Project' in response.data
    assert b'Designer information is not currently available.' in response.data


def test_ut32_19_hiddenCompanyPage(client, projects):
    execute("UPDATE company_profile SET status='Suspended' WHERE companyId=?", (projects['company'],))
    response = client.get(url(projects['own']))
    assert response.status_code == 200 and b'Own Current Project' in response.data
    assert b'Studio Thirty Two' not in response.data
    assert b'Designer information is not currently available.' in response.data


def test_ut32_20_searchLinksAndReturn(client, projects):
    keyword = '  Own Current  '
    search = client.get('/customer/idps/search', query_string=dict(keyword=keyword))
    assert f'/customer/idps/{projects["own"]}?keyword=Own+Current'.encode() in search.data
    assert b'aria-label="View Own Current Project"' in search.data
    detail = client.get(url(projects['own']), query_string=dict(keyword=keyword))
    assert b'href="/customer/idps/search?keyword=Own+Current"' in detail.data
    assert b'class="active">Search IDPs' in detail.data


def test_ut32_21_directLinkAndPast(client, projects):
    response = client.get(url(projects['past']))
    assert response.status_code == 200 and b'Past' in response.data
    assert b'Back to search' in response.data


@pytest.mark.parametrize('sql', [
    "UPDATE user_account SET status='Suspended' WHERE username='cust001'",
    "UPDATE user_profile SET status='Suspended' WHERE profileId=3",
    "UPDATE user_profile SET permissions='[]' WHERE profileId=3",
    "DELETE FROM user_account WHERE username='cust001'"])
def test_ut32_22_notCheckedAgainAfterLogin(client, projects, sql):
    execute(sql)
    assert client.get(url(projects['own'])).status_code == 200
    # the next customer login is refused
    client.post('/customer/logout')
    response = client.post('/customer/login', data=dict(username='cust001', password='Cust@123'))
    assert b'Invalid login details or access unavailable' in response.data


@pytest.mark.parametrize('target', ['idp', 'category'])
def test_ut32_23_visibilityChangedAfterSearch(client, projects, target):
    assert client.get('/customer/idps/search').status_code == 200
    if target == 'idp': execute("UPDATE idp SET status='Suspended' WHERE idpId=?", (projects['own'],))
    else: execute("UPDATE idp_category SET status='Suspended' WHERE categoryId=?", (projects['category'],))
    assert client.get(url(projects['own'])).status_code == 404


def test_ut32_24_freshSavedContent(client, projects):
    client.get(url(projects['own']))
    execute('UPDATE idp SET description=? WHERE idpId=?', ('Latest progress saved', projects['own']))
    execute('UPDATE company_profile SET services=? WHERE companyId=?', ('Latest services', projects['company']))
    response = client.get(url(projects['own']))
    assert b'Latest progress saved' in response.data and b'Latest services' in response.data


def test_ut32_25_forgedQueryFields(client, projects):
    response = client.get(url(projects['own']), query_string=dict(
        designerId=projects['other'], idpId=projects['foreign'], status='Suspended',
        returnUrl='https://example.test', keyword='https://example.test'))
    assert b'Own Current Project' in response.data and b'Studio Thirty Two' in response.data
    assert b'Other Designer Project' not in response.data
    assert b'href="https://example.test' not in response.data


def test_ut32_26_readOnly(client, projects):
    # viewing changes nothing, except US37: each IDP a customer can see gets one idp_view row
    def withoutViews():
        return [line for line in snapshot() if "idp_view" not in line]   # its rows + id counter
    before = withoutViews()
    for key in ('own', 'past', 'foreign', 'hidden', 'suspended'):
        client.get(url(projects[key]))
    assert withoutViews() == before
    viewed = [line for line in snapshot() if 'INSERT INTO "idp_view"' in line]
    assert len(viewed) == 3


@pytest.mark.parametrize('method', ['post', 'put', 'patch', 'delete'])
def test_ut32_27_methods(client, projects, method):
    assert getattr(client, method)(url(projects['own'])).status_code == 405


def test_ut32_28_escaping(client, projects):
    execute('UPDATE idp SET title=?,description=?,location=? WHERE idpId=?',
        ('<script>project</script>', '<img src=x onerror=alert(1)>', '<script>place</script>', projects['own']))
    execute('UPDATE company_profile SET companyName=?,description=?,services=? WHERE companyId=?',
        ('<script>studio</script>', '<script>about</script>', '<script>service</script>', projects['company']))
    response = client.get(url(projects['own']), query_string=dict(keyword='<script>'))
    assert b'&lt;script&gt;' in response.data and b'&lt;img' in response.data
    assert b'<script>' not in response.data and b'<img src=x' not in response.data


def test_ut32_29_missingOptionalLocation(client, projects):
    execute("UPDATE idp SET location='' WHERE idpId=?", (projects['own'],))
    response = client.get(url(projects['own']))
    assert response.status_code == 200 and b'<strong>Location:</strong>' not in response.data


def test_ut32_30_pageCallsControllerOnce(client, projects, monkeypatch):
    def refused(*args): pytest.fail('the page must not check the customer again')
    monkeypatch.setattr(CustomerLoginController, 'login', refused)
    calls = []
    original = ViewIDPController.viewIDP
    def spy(self, *args):
        calls.append(args)
        return original(self, *args)
    monkeypatch.setattr(ViewIDPController, 'viewIDP', spy)
    assert client.get(url(projects['own'])).status_code == 200
    assert calls == [(projects['own'], True)]


def test_ut32_31_headerFromSession(client, projects, monkeypatch):
    def refused(*args): pytest.fail('the page must not load the account again')
    monkeypatch.setattr(UserAccount, 'getUserAccount', refused)
    monkeypatch.setattr(UserAccount, 'verifyCredentials', refused)
    response = client.get(url(projects['own']))
    assert b'Logged in as cust001 (Customer)' in response.data


def test_ut32_32_emptySearchReturn(client, projects):
    response = client.get(url(projects['own']), query_string=dict(keyword='   '))
    assert b'href="/customer/idps/search?keyword="' in response.data


def test_ut32_33_viewWithoutCounting(projects):
    assert IDP().viewIDP(projects['own'], False).idpId == projects['own']
    assert viewRows() == 0


def test_ut32_34_savedRedirectNotCounted(client, projects):
    response = client.get(url(projects['own']), query_string=dict(saved='1'))
    assert response.status_code == 200 and b'Own Current Project' in response.data
    assert viewRows() == 0


def test_ut32_35_saveButtonAlwaysShown(client, projects):
    assert SavedIDP().createSavedRecord(projects['customer'], projects['own'])
    response = client.get(url(projects['own']))
    assert b'>Save IDP</button>' in response.data and b'Saved</span>' not in response.data


# ---------- system tests (Flask test client) ----------

def views(projects, idpId):
    return next(row.views for row in IDPAnalytics().getViewStatistics(projects['owner']) if row.idpId == idpId)


def test_tc32_12_saveDoesNotCountAView(client, projects):
    assert client.get(url(projects['own'])).status_code == 200
    assert views(projects, projects['own']) == 1
    assert client.post(f'/customer/idps/{projects["own"]}/save').status_code == 302
    # the page shown after Save (?saved=1) adds no view
    response = client.get(url(projects['own']), query_string=dict(saved='1'))
    assert response.status_code == 200 and b'IDP saved to your saved list' in response.data
    assert views(projects, projects['own']) == 1


def test_tc32_13_saveButtonShownForSavedIDP(client, projects):
    assert client.post(f'/customer/idps/{projects["own"]}/save').status_code == 302
    response = client.get(url(projects['own']))
    assert b'>Save IDP</button>' in response.data
    response = client.post(f'/customer/idps/{projects["own"]}/save', follow_redirects=True)
    assert b'This IDP is already in your saved list' in response.data
