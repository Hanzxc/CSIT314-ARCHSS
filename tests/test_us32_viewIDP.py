"""US32 customer detail view uses isolated database fixtures."""
import pytest

from app import app
from control.viewIDPController import ViewIDPController
from entity.companyProfile import CompanyProfile
from entity.idp import IDP
from entity.userAccount import UserAccount
from test_us22_updateCurrentIDP import data, execute, snapshot


@pytest.fixture
def projects(data):
    company = execute('INSERT INTO company_profile (designerId,companyName,description,services,email,phone,address) '
        'VALUES (?,?,?,?,?,?,?)', (data['owner'], 'Studio Thirty Two', 'Thoughtful home interiors.',
        'Space planning and carpentry.', 'private-business@example.test', '12345678', 'Office address'))
    return {**data, 'company': company,
            'customer': UserAccount().verifyCredentials('cust001', 'Cust@123').userId}


@pytest.fixture
def client(projects):
    result = app.test_client()
    result.post('/customer/login', data=dict(username='cust001', password='Cust@123'))
    return result


def url(idpId):
    return f'/customer/idps/{idpId}'


def test_ut32_1_currentProject(projects):
    p = IDP().getIDP(projects['own'])
    assert p.title == 'Own Current Project' and p.categoryName == 'Living Room'
    assert p.projectType == 'Current' and p.location == 'Tampines'


def test_ut32_2_pastProject(projects):
    assert IDP().getIDP(projects['past']).projectType == 'Past'


def test_ut32_3_anotherDesigner(projects):
    assert IDP().getIDP(projects['foreign']).designerId == projects['other']


@pytest.mark.parametrize('key', ['suspended', 'hidden', 'missing'])
def test_ut32_4_hiddenOrMissingEntity(projects, key):
    assert IDP().getIDP(projects.get(key, 999999)) is None


@pytest.mark.parametrize('value', [-1, 0, 999999, "1 OR 1=1", None])
def test_ut32_5_invalidEntityId(projects, value):
    assert IDP().getIDP(value) is None


def test_ut32_6_controllerDetailsAndCompany(projects):
    result = ViewIDPController().viewIDP(projects['customer'], projects['own'])
    assert result['idp'].idpId == projects['own']
    assert result['companyProfile'].companyName == 'Studio Thirty Two'
    assert result['companyProfile'].designerId == result['idp'].designerId


def test_ut32_7_missingCompany(projects):
    result = ViewIDPController().viewIDP(projects['customer'], projects['foreign'])
    assert result['idp'] is not None and result['companyProfile'] is None


def test_ut32_8_suspendedCompany(projects):
    execute("UPDATE company_profile SET status='Suspended' WHERE companyId=?", (projects['company'],))
    result = ViewIDPController().viewIDP(projects['customer'], projects['own'])
    assert result['idp'] is not None and result['companyProfile'] is None


def test_ut32_9_denyBeforeQueries(projects, monkeypatch):
    monkeypatch.setattr(ViewIDPController, 'getCustomer', lambda *args: None)
    def forbidden(*args): pytest.fail('Denied requests must not query project/company')
    monkeypatch.setattr(IDP, 'getIDP', forbidden)
    monkeypatch.setattr(CompanyProfile, 'getCompanyProfile', forbidden)
    with pytest.raises(PermissionError): ViewIDPController().viewIDP(1, projects['own'])


def test_ut32_10_hiddenStopsCompanyQuery(projects, monkeypatch):
    def forbidden(*args): pytest.fail('Unavailable project must not retrieve company')
    monkeypatch.setattr(CompanyProfile, 'getCompanyProfile', forbidden)
    assert ViewIDPController().viewIDP(projects['customer'], projects['hidden']) is None


def test_ut32_11_companyUsesSavedOwner(projects, monkeypatch):
    seen = []
    monkeypatch.setattr(CompanyProfile, 'getCompanyProfile', lambda self, owner: seen.append(owner))
    ViewIDPController().viewIDP(projects['customer'], projects['foreign'])
    assert seen == [projects['other']]


@pytest.mark.parametrize('condition', ['active', 'account', 'profile', 'permission', 'admin', 'missing'])
def test_ut32_12_customerAccess(projects, condition):
    customer = projects['customer']
    if condition == 'account': execute("UPDATE user_account SET status='Suspended' WHERE userId=?", (customer,))
    elif condition == 'profile': execute("UPDATE user_profile SET status='Suspended' WHERE profileId=3")
    elif condition == 'permission': execute("UPDATE user_profile SET permissions='[]' WHERE profileId=3")
    elif condition == 'admin': customer = 1
    elif condition == 'missing': customer = 999999
    assert (ViewIDPController().getCustomer(customer) is not None) == (condition == 'active')


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
def test_ut32_15_otherRoles(projects, profileId):
    UserAccount().createUserAccount('other32', 'Other@123', 'Other', '', '', profileId)
    account = UserAccount().verifyCredentials('other32', 'Other@123')
    client = app.test_client()
    with client.session_transaction() as state:
        state.update(userId=account.userId, username=account.username, profileId=profileId)
    assert client.get(url(projects['own'])).status_code == 403


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
def test_ut32_22_accessRevoked(client, projects, sql):
    execute(sql)
    assert client.get(url(projects['own'])).status_code == 403


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
    before = snapshot()
    for key in ('own', 'past', 'foreign', 'hidden', 'suspended'):
        client.get(url(projects[key]))
    assert snapshot() == before


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


def test_ut32_30_secondAccessCheck(client, projects, monkeypatch):
    original = ViewIDPController.getCustomer
    calls = []
    def changed(self, userId):
        calls.append(userId)
        return original(self, userId) if len(calls) == 1 else None
    monkeypatch.setattr(ViewIDPController, 'getCustomer', changed)
    assert client.get(url(projects['own'])).status_code == 403
    assert len(calls) == 2


def test_ut32_31_sessionIdentity(client, projects):
    with client.session_transaction() as state:
        state.update(username='admin01', profileId=1)
    response = client.get(url(projects['own']))
    assert b'Logged in as cust001 (Customer)' in response.data


def test_ut32_32_emptySearchReturn(client, projects):
    response = client.get(url(projects['own']), query_string=dict(keyword='   '))
    assert b'href="/customer/idps/search?keyword="' in response.data
