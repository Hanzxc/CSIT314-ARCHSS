"""US31 customer catalogue search; isolated DB and existing US22 fixtures."""
import pytest

from app import app
from boundary.searchIDPPage import SearchIDPPage
from control.searchIDPController import SearchIDPController
from entity.idp import IDP
from entity.userAccount import UserAccount
from test_us22_updateCurrentIDP import data, execute, snapshot

SEARCH_URL = '/customer/idps/search'


@pytest.fixture
def catalogue(data):
    second = execute('INSERT INTO idp (designerId,categoryId,title,description,location) VALUES (?,?,?,?,?)',
        (data['other'], data['target'], 'Kitchen 100%_Plan', "Straße carpentry O'Neil 客厅 Café C:\\plans", 'Bedok'))
    return {**data, 'second': second}


@pytest.fixture
def client(catalogue):
    result = app.test_client()
    assert result.post('/customer/login', data=dict(username='cust001', password='Cust@123')).status_code == 302
    return result


def ids(keyword):
    return [p.idpId for p in IDP().searchIDPs(keyword)]


def test_ut31_1_title(catalogue):
    assert ids('Own Current') == [catalogue['own']]


def test_ut31_2_description(catalogue):
    assert ids('carpentry') == [catalogue['second']]


def test_ut31_3_location(catalogue):
    assert ids('Bedok') == [catalogue['second']]


def test_ut31_4_category(catalogue):
    assert ids('Living Room') == [catalogue[k] for k in ('past', 'foreign', 'own')]


@pytest.mark.parametrize('keyword', ['KITCHEN', 'kItChEn', 'STRASSE', 'straße', 'CAFÉ', '客厅'])
def test_ut31_5_unicodeCase(catalogue, keyword):
    assert ids(keyword) == [catalogue['second']]


@pytest.mark.parametrize('keyword', ['', None, '   ', '\t\n'])
def test_ut31_6_emptyBrowse(catalogue, keyword):
    assert ids(keyword) == [catalogue[k] for k in ('second', 'past', 'foreign', 'own')]


def test_ut31_7_trim(catalogue):
    assert ids('  Bedok  ') == [catalogue['second']]


def test_ut31_8_newestFirst(catalogue):
    results = ids('Initial progress')
    assert results == sorted(results, reverse=True)


def test_ut31_9_noMatches(catalogue):
    assert ids('unmatched-zebra') == []


def test_ut31_10_acrossDesigners(catalogue):
    results = IDP().searchIDPs('Initial progress')
    assert {p.designerId for p in results} == {catalogue['owner'], catalogue['other']}


def test_ut31_11_currentAndPast(catalogue):
    assert {p.projectType for p in IDP().searchIDPs('')} == {'Current', 'Past'}


@pytest.mark.parametrize('title', ['Suspended Project', 'Hidden Category Project'])
def test_ut31_12_hiddenResults(catalogue, title):
    assert ids(title) == []


@pytest.mark.parametrize('keyword', ['%', '_', "'", '\\'])
def test_ut31_13_literalCharacters(catalogue, keyword):
    assert ids(keyword) == [catalogue['second']]


def test_ut31_14_sqlIsData(catalogue):
    before = snapshot()
    assert ids("' OR 1=1 --") == []
    assert snapshot() == before


def test_ut31_15_noDuplicatesAndFields(catalogue):
    results = IDP().searchIDPs('Kitchen')
    assert len(results) == 1
    p = results[0]
    assert p.categoryName == 'Kitchen' and p.location == 'Bedok'
    assert p.title == 'Kitchen 100%_Plan' and 'carpentry' in p.description


@pytest.mark.parametrize('condition', ['active', 'account', 'profile', 'permission', 'admin', 'missing'])
def test_ut31_16_customerAccess(catalogue, condition):
    customerId = UserAccount().verifyCredentials('cust001', 'Cust@123').userId
    if condition == 'account': execute("UPDATE user_account SET status='Suspended' WHERE userId=?", (customerId,))
    elif condition == 'profile': execute("UPDATE user_profile SET status='Suspended' WHERE profileId=3")
    elif condition == 'permission': execute("UPDATE user_profile SET permissions='[]' WHERE profileId=3")
    elif condition == 'admin': customerId = 1
    elif condition == 'missing': customerId = 999999
    assert (SearchIDPController().getCustomer(customerId) is not None) == (condition == 'active')


def test_ut31_17_deniedController(catalogue, monkeypatch):
    monkeypatch.setattr(SearchIDPController, 'getCustomer', lambda *args: None)
    def forbidden(*args): pytest.fail('Denied search must not query IDPs')
    monkeypatch.setattr(IDP, 'searchIDPs', forbidden)
    with pytest.raises(PermissionError): SearchIDPController().searchIDPs(1, 'x')


def test_ut31_18_controllerDelegation(catalogue, monkeypatch):
    customerId = UserAccount().verifyCredentials('cust001', 'Cust@123').userId
    seen = []
    monkeypatch.setattr(IDP, 'searchIDPs', lambda self, keyword: seen.append(keyword) or [])
    assert SearchIDPController().searchIDPs(customerId, '  kitchen  ') == []
    assert seen == ['kitchen']


def test_ut31_19_noSession(catalogue):
    response = app.test_client().get(SEARCH_URL)
    assert response.status_code == 302 and response.headers['Location'].endswith('/customer/login')


@pytest.mark.parametrize('profileId', [1, 2, 4])
def test_ut31_20_otherRoles(catalogue, profileId):
    UserAccount().createUserAccount(UserAccount(username='other31', password='Other@123', fullName='Other', email='', phone='', profileId=profileId))
    account = UserAccount().verifyCredentials('other31', 'Other@123')
    client = app.test_client()
    with client.session_transaction() as state:
        state.update(userId=account.userId, profileId=profileId, username=account.username)
    assert client.get(SEARCH_URL).status_code == 403


def test_ut31_21_resultsAndTemplate(client, catalogue):
    response = client.get(SEARCH_URL, query_string=dict(keyword='  KITCHEN  '))
    assert response.status_code == 200 and b'1 IDP found' in response.data
    assert b'value="KITCHEN"' in response.data and b'Kitchen 100%_Plan' in response.data
    assert b'Category:' in response.data and b'Project type:' in response.data
    assert b'carpentry' in response.data and b'Bedok' in response.data
    assert b'(Customer)' in response.data and b'Update current IDP' not in response.data
    assert b'/designer/idps/' not in response.data
    assert b'class="search-bar"' in response.data and b'method="GET"' in response.data


def test_ut31_22_noMatches(client):
    response = client.get(SEARCH_URL, query_string=dict(keyword='loft-zebra'))
    assert response.status_code == 200 and b'No matching IDPs found' in response.data
    assert b'value="loft-zebra"' in response.data


def test_ut31_23_emptyCatalogue(client):
    execute("UPDATE idp SET status='Suspended'")
    response = client.get(SEARCH_URL)
    assert response.status_code == 200 and b'No IDPs are currently available' in response.data
    response = client.get(SEARCH_URL, query_string=dict(keyword='kitchen'))
    assert b'No matching IDPs found' in response.data


def test_ut31_24_clearAndNavigation(client):
    client.get(SEARCH_URL, query_string=dict(keyword='kitchen'))
    response = client.get(SEARCH_URL)
    assert b'4 IDPs found' in response.data and b'value=""' in response.data
    assert b'href="/customer/idps/search" class="btn-small btn-grey">Clear' in response.data
    assert b'Back to dashboard' in response.data
    assert b'href="/customer/idps/search"' in client.get('/customer/dashboard').data
    assert b'class="active">Search IDPs' in response.data


@pytest.mark.parametrize('sql', [
    "UPDATE user_account SET status='Suspended' WHERE username='cust001'",
    "UPDATE user_profile SET status='Suspended' WHERE profileId=3",
    "UPDATE user_profile SET permissions='[]' WHERE profileId=3",
    "DELETE FROM user_account WHERE username='cust001'"])
def test_ut31_25_accessRevoked(client, sql):
    execute(sql)
    assert client.get(SEARCH_URL).status_code == 403


def test_ut31_26_forgedFilters(client):
    response = client.get(SEARCH_URL, query_string=dict(designerId=1, status='Suspended', projectType='Past'))
    assert b'4 IDPs found' in response.data
    assert b'Suspended Project' not in response.data and b'Hidden Category Project' not in response.data


def test_ut31_27_freshResults(client, catalogue):
    execute('UPDATE idp SET title=? WHERE idpId=?', ('Fresh title', catalogue['own']))
    assert b'Fresh title' in client.get(SEARCH_URL, query_string=dict(keyword='Fresh')).data
    execute("UPDATE idp SET status='Suspended' WHERE idpId=?", (catalogue['own'],))
    assert b'No matching IDPs found' in client.get(SEARCH_URL, query_string=dict(keyword='Fresh')).data
    execute("UPDATE idp_category SET status='Suspended' WHERE categoryId=?", (catalogue['target'],))
    assert b'Kitchen 100%_Plan' not in client.get(SEARCH_URL).data


def test_ut31_28_readOnlyAndNoStats(client):
    before = snapshot()
    client.get(SEARCH_URL)
    client.get(SEARCH_URL, query_string=dict(keyword='kitchen'))
    client.get(SEARCH_URL, query_string=dict(keyword='unknown'))
    assert snapshot() == before


@pytest.mark.parametrize('method', ['post', 'put', 'patch', 'delete'])
def test_ut31_29_methods(client, method):
    assert getattr(client, method)(SEARCH_URL).status_code == 405


def test_ut31_30_escapingAndSummary(client, catalogue):
    execute('UPDATE idp SET title=?,description=?,location=? WHERE idpId=?',
        ('<script>title</script>', '<img src=x onerror=alert(1)> ' + 'x'*300,
         '<script>place</script>', catalogue['own']))
    response = client.get(SEARCH_URL, query_string=dict(keyword='<script>'))
    assert b'&lt;script&gt;' in response.data and b'<script>' not in response.data
    assert b'&lt;img' in response.data and b'<img src=x' not in response.data
    assert b'x'*201 not in response.data
    assert response.headers['Cache-Control'] == 'no-store'


def test_ut31_31_secondAccessCheck(client, monkeypatch):
    original = SearchIDPController.getCustomer
    calls = []
    def changed(self, userId):
        calls.append(userId)
        return original(self, userId) if len(calls) == 1 else None
    monkeypatch.setattr(SearchIDPController, 'getCustomer', changed)
    response = client.get(SEARCH_URL)
    assert response.status_code == 403 and len(calls) == 2


def test_ut31_32_longKeywordAndIdentity(client):
    with client.session_transaction() as state:
        state.update(username='admin01', profileId=1)
    response = client.get(SEARCH_URL, query_string=dict(keyword='x'*5000))
    assert response.status_code == 200 and b'No matching IDPs found' in response.data
    assert b'Logged in as cust001 (Customer)' in response.data
