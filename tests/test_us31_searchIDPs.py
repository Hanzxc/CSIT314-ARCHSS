"""US31 customer catalogue search; isolated DB and existing US22 fixtures."""
import pytest
from flask import session

from app import app
from boundary.searchIDPPage import SearchIDPPage
from control.customerLoginController import CustomerLoginController
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
def test_ut31_6_pageTrimsEmptyKeyword(catalogue, monkeypatch, keyword):
    seen = []
    original = SearchIDPController.searchIDPs
    monkeypatch.setattr(SearchIDPController, 'searchIDPs', lambda self, word: seen.append(word) or original(self, word))
    with app.test_request_context():
        session.update(userId=3, profileId=3, username='cust001')
        html = SearchIDPPage().searchIDPs(keyword)
    assert seen == ['']
    for title in ('Kitchen 100%_Plan', 'Own Past Project', 'Other Designer Project', 'Own Current Project'):
        assert title in html


def test_ut31_7_entityDoesNotTrim(catalogue):
    # the spaces are part of the search here - the page trims first (UT31.18)
    assert ids('  Bedok  ') == []
    assert ids('Bedok') == [catalogue['second']]


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


def test_ut31_16_controllerOneEntityCall(catalogue, monkeypatch):
    calls = []
    monkeypatch.setattr(IDP, 'searchIDPs', lambda self, keyword: calls.append(keyword) or ['found'])
    assert SearchIDPController().searchIDPs('kitchen') == ['found']
    assert calls == ['kitchen']


def test_ut31_17_controllerDoesNotTrim(catalogue, monkeypatch):
    seen = []
    monkeypatch.setattr(IDP, 'searchIDPs', lambda self, keyword: seen.append(keyword) or [])
    assert SearchIDPController().searchIDPs('  kitchen  ') == []
    assert seen == ['  kitchen  ']


def test_ut31_18_pageTrimsKeyword(client, monkeypatch):
    seen = []
    original = SearchIDPController.searchIDPs
    monkeypatch.setattr(SearchIDPController, 'searchIDPs', lambda self, word: seen.append(word) or original(self, word))
    response = client.get(SEARCH_URL, query_string=dict(keyword='  kitchen  '))
    assert response.status_code == 200 and seen == ['kitchen']


def test_ut31_19_noSession(catalogue):
    response = app.test_client().get(SEARCH_URL)
    assert response.status_code == 302 and response.headers['Location'].endswith('/customer/login')


@pytest.mark.parametrize('profileId', [1, 2, 4])
def test_ut31_20_roleNotCheckedAgain(catalogue, profileId):
    # being a customer is the precondition (customerLoginRequired only checks there's a session)
    client = app.test_client()
    with client.session_transaction() as state:
        state.update(userId=1, profileId=profileId, username='other31')
    response = client.get(SEARCH_URL)
    assert response.status_code == 200 and b'Own Current Project' in response.data


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
def test_ut31_25_notCheckedAgainAfterLogin(client, sql):
    execute(sql)
    assert client.get(SEARCH_URL).status_code == 200
    # the next customer login is refused
    client.post('/customer/logout')
    response = client.post('/customer/login', data=dict(username='cust001', password='Cust@123'))
    assert b'Invalid login details or access unavailable' in response.data


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


def test_ut31_31_pageCallsControllerWithKeywordOnly(client, monkeypatch):
    def refused(*args):
        pytest.fail('the page must not check the customer again')
    monkeypatch.setattr(CustomerLoginController, 'login', refused)
    calls = []
    monkeypatch.setattr(SearchIDPController, 'searchIDPs', lambda *args: calls.append(args[1:]) or [])
    response = client.get(SEARCH_URL, query_string=dict(keyword='kitchen'))
    assert response.status_code == 200 and calls == [('kitchen',)]


def test_ut31_32_longKeyword(client):
    response = client.get(SEARCH_URL, query_string=dict(keyword='x'*5000))
    assert response.status_code == 200 and b'No matching IDPs found' in response.data
