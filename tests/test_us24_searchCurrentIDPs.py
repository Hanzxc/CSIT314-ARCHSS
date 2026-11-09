import pytest

from app import app
from control.searchCurrentIDPController import SearchCurrentIDPController
from control.updateCurrentIDPController import UpdateCurrentIDPController
from control.deleteCurrentIDPController import DeleteCurrentIDPController
from control.interiorDesignerLoginController import InteriorDesignerLoginController
from entity.idp import IDP
from test_us22_updateCurrentIDP import data, client, execute, snapshot, validIDP

SEARCH_URL='/designer/idps/current/search'


@pytest.fixture
def searchable(data):
    second=execute("INSERT INTO idp (designerId,categoryId,title,description,location) VALUES (?,?,?,?,?)",
                   (data['owner'],data['target'],'Kitchen 100%_Plan',"Straße carpentry O'Neil 客厅 Café C:\\plans",'Bedok'))
    return {**data,'second':second}


def ids(owner,keyword):
    return [p.idpId for p in IDP().searchCurrentIDPs(owner,keyword)]


def test_ut24_1_titleSearch(searchable):
    assert ids(searchable['owner'],'Own Current')==[searchable['own']]


def test_ut24_2_descriptionSearch(searchable):
    assert ids(searchable['owner'],'carpentry')==[searchable['second']]


def test_ut24_3_locationSearch(searchable):
    assert ids(searchable['owner'],'Bedok')==[searchable['second']]


def test_ut24_4_categorySearch(searchable):
    assert ids(searchable['owner'],'living room')==[searchable['own']]


@pytest.mark.parametrize('keyword',['KITCHEN','kItChEn','STRASSE','straße','CAFÉ','客厅'])
def test_ut24_5_unicodeAndCaseInsensitive(searchable,keyword):
    assert ids(searchable['owner'],keyword)==[searchable['second']]


@pytest.mark.parametrize('keyword',['',None,'   ','\t\n'])
def test_ut24_6_pageTrimsEmptyKeyword(searchable,client,monkeypatch,keyword):
    seen=[]
    original=IDP.searchCurrentIDPs
    monkeypatch.setattr(IDP,'searchCurrentIDPs',lambda self,owner,word:seen.append(word) or original(self,owner,word))
    # None = no keyword in the URL at all
    response=client.get(SEARCH_URL,query_string={} if keyword is None else {'keyword':keyword})
    assert response.status_code==200 and seen==['']
    assert response.data.index(b'Kitchen 100%_Plan')<response.data.index(b'Own Current Project')


def test_ut24_7_pageTrimsKeyword(searchable,client,monkeypatch):
    seen=[]
    original=IDP.searchCurrentIDPs
    monkeypatch.setattr(IDP,'searchCurrentIDPs',lambda self,owner,word:seen.append(word) or original(self,owner,word))
    response=client.get(SEARCH_URL,query_string={'keyword':'  Own Current  '})
    assert seen==['Own Current']
    assert b'Own Current Project' in response.data and b'Kitchen 100%_Plan' not in response.data


def test_ut24_8_newestFirst(searchable):
    assert ids(searchable['owner'],'')==[searchable['second'],searchable['own']]


def test_ut24_9_noMatch(searchable):
    assert ids(searchable['owner'],'unmatched-zebra')==[]


def test_ut24_10_ownerFilterCannotBeBypassed(searchable):
    result=IDP().searchCurrentIDPs(searchable['owner'],'Initial progress')
    assert [p.idpId for p in result]==[searchable['own']]
    assert all(p.designerId==searchable['owner'] for p in result)


@pytest.mark.parametrize('key',['foreign','past','suspended','hidden'])
def test_ut24_11_visibilityFilters(searchable,key):
    titles={'foreign':'Other Designer Project','past':'Own Past Project',
            'suspended':'Suspended Project','hidden':'Hidden Category Project'}
    assert ids(searchable['owner'],titles[key])==[]


@pytest.mark.parametrize('keyword',['%','_',"'",'\\'])
def test_ut24_12_metacharactersAreLiteral(searchable,keyword):
    assert ids(searchable['owner'],keyword)==[searchable['second']]


def test_ut24_13_sqlInjectionIsSearchText(searchable):
    before=snapshot()
    assert ids(searchable['owner'],"' OR 1=1 --")==[]
    assert snapshot()==before


def test_ut24_14_resultsContainCustomerFields(searchable):
    result=IDP().searchCurrentIDPs(searchable['owner'],'carpentry')[0]
    assert result.title=='Kitchen 100%_Plan' and result.categoryName=='Kitchen'
    assert result.location=='Bedok' and result.projectType=='Current' and result.status=='Active'


def test_ut24_15_noDuplicatesForMultipleMatchingFields(searchable):
    assert ids(searchable['owner'],'kitchen')==[searchable['second']]


def test_ut24_16_controllerOnlyHasSearch():
    import control.searchCurrentIDPController as module
    methods={name for name in vars(SearchCurrentIDPController) if not name.startswith('_')}
    assert methods=={'searchCurrentIDPs'}
    assert not hasattr(module,'InteriorDesignerLoginController')


def test_ut24_17_noLoginControllerOneEntityCall(searchable,monkeypatch):
    monkeypatch.setattr(InteriorDesignerLoginController,'login',lambda self,username,password:None)
    calls=[]
    monkeypatch.setattr(IDP,'searchCurrentIDPs',lambda self,owner,keyword:calls.append(owner) or ['found'])
    assert SearchCurrentIDPController().searchCurrentIDPs(searchable['owner'],'x')==['found']
    assert calls==[searchable['owner']]


def test_ut24_18_controllerDoesNotTrim(searchable,monkeypatch):
    seen=[]
    monkeypatch.setattr(IDP,'searchCurrentIDPs',lambda self,owner,keyword:seen.append((owner,keyword)) or [])
    assert SearchCurrentIDPController().searchCurrentIDPs(searchable['owner'],'  Kitchen  ')==[]
    assert seen==[(searchable['owner'],'  Kitchen  ')]


def test_ut24_19_signedOutRedirect(searchable):
    result=app.test_client().get(SEARCH_URL,query_string={'keyword':'kitchen'})
    assert result.status_code==302 and result.headers['Location'].endswith('/designer/login')


# each role logs in on its own page (/login is only for User Admins, US1)
@pytest.mark.parametrize('loginUrl,username,password',[('/login','admin01','Admin@123'),('/customer/login','cust001','Cust@123')])
def test_ut24_20_roleNotCheckedAgain(searchable,loginUrl,username,password):
    # the role isn't checked again (precondition UC13) - these users just own no current IDPs
    browser=app.test_client();browser.post(loginUrl,data=dict(username=username,password=password))
    response=browser.get(SEARCH_URL)
    assert response.status_code==200 and b'You have no current IDPs to display' in response.data


def test_ut24_21_resultsAndKeywordRetained(searchable,client):
    response=client.get(SEARCH_URL,query_string={'keyword':'Kitchen'})
    assert response.status_code==200
    for text in [b'Kitchen 100%_Plan',b'value="Kitchen"',b'1 current IDP found',b'Designer navigation',
                 b'class="search-bar"',b'method="GET"',b'Search',b'Clear',b'Back to current IDPs']:
        assert text in response.data
    assert b'Own Current Project' not in response.data


def test_ut24_22_noResultsIsNormalPage(searchable,client):
    response=client.get(SEARCH_URL,query_string={'keyword':'unmatched-zebra'})
    assert response.status_code==200 and b'No matching current IDPs found' in response.data
    assert b'value="unmatched-zebra"' in response.data


def test_ut24_23_clearShowsAll(searchable,client):
    client.get(SEARCH_URL,query_string={'keyword':'kitchen'})
    response=client.get(SEARCH_URL)
    assert response.status_code==200 and b'2 current IDPs found' in response.data
    assert b'Own Current Project' in response.data and b'Kitchen 100%_Plan' in response.data


def test_ut24_24_noCurrentProjects(searchable,client):
    execute('DELETE FROM idp WHERE designerId=?',(searchable['owner'],))
    response=client.get(SEARCH_URL)
    assert response.status_code==200 and b'You have no current IDPs to display' in response.data
    assert b'Other Designer Project' not in response.data


def test_ut24_25_forgedOwnerIgnored(searchable,client):
    response=client.get(SEARCH_URL,query_string={'keyword':'','designerId':searchable['other'],'userId':searchable['other']})
    assert response.status_code==200 and b'Own Current Project' in response.data
    assert b'Other Designer Project' not in response.data


def test_ut24_26_readOnlyAndGetOnly(searchable,client):
    before=snapshot()
    for term in ['','Kitchen','no match','%']:
        assert client.get(SEARCH_URL,query_string={'keyword':term}).status_code==200
    for method in ['post','put','patch','delete']:
        assert getattr(client,method)(SEARCH_URL).status_code==405
    assert snapshot()==before


def test_ut24_27_navigationAndFreshDetailCheck(searchable,client):
    listing=client.get('/designer/idps/current')
    assert SEARCH_URL.encode() in listing.data
    result=client.get(SEARCH_URL,query_string={'keyword':'Kitchen'})
    detail=f'/designer/idps/current/{searchable["second"]}'
    assert detail.encode() in result.data
    assert client.get(detail).status_code==200
    execute("UPDATE idp SET status='Suspended' WHERE idpId=?",(searchable['second'],))
    assert client.get(detail).status_code==404
    assert b'No matching current IDPs found' in client.get(SEARCH_URL,query_string={'keyword':'Kitchen'}).data


@pytest.mark.parametrize('condition',['account','profile','permissions'])
def test_ut24_28_notCheckedAgainAfterLogin(searchable,client,condition):
    assert client.get(SEARCH_URL).status_code==200
    if condition=='account':execute("UPDATE user_account SET status='Suspended' WHERE userId=?",(searchable['owner'],))
    elif condition=='profile':execute("UPDATE user_profile SET status='Suspended' WHERE profileId=2")
    else:execute("UPDATE user_profile SET permissions='[]' WHERE profileId=2")
    response=client.get(SEARCH_URL)
    assert response.status_code==200 and b'Own Current Project' in response.data


def test_ut24_29_searchReflectsUpdateAndDeletion(searchable,client):
    assert UpdateCurrentIDPController().updateCurrentIDP(validIDP(searchable,title='Fresh Progress Project'))
    assert ids(searchable['owner'],'Fresh Progress Project')==[searchable['own']]
    assert ids(searchable['owner'],'Own Current Project')==[]
    assert DeleteCurrentIDPController().deleteCurrentIDP(searchable['owner'],searchable['own'])
    assert ids(searchable['owner'],'Fresh Progress Project')==[]


def test_ut24_30_keywordAndStoredTextEscaped(searchable,client):
    attack='<script>alert("test")</script>'
    execute('UPDATE idp SET title=? WHERE idpId=?',(attack,searchable['own']))
    response=client.get(SEARCH_URL,query_string={'keyword':attack})
    assert response.status_code==200 and b'&lt;script&gt;' in response.data
    assert b'<script>' not in response.data


def test_ut24_31_pageSearchesStraightAway(searchable,client,monkeypatch):
    def refused(*args):pytest.fail('the page must not check the designer again')
    monkeypatch.setattr(InteriorDesignerLoginController,'login',refused)
    seen=[]
    original=SearchCurrentIDPController.searchCurrentIDPs
    monkeypatch.setattr(SearchCurrentIDPController,'searchCurrentIDPs',
                        lambda self,owner,keyword:seen.append((owner,keyword)) or original(self,owner,keyword))
    response=client.get(SEARCH_URL,query_string={'keyword':'Kitchen'})
    assert response.status_code==200 and seen==[(searchable['owner'],'Kitchen')]


def test_ut24_32_longKeywordSafe(searchable,client):
    before=snapshot()
    response=client.get(SEARCH_URL,query_string={'keyword':'x'*5000})
    assert response.status_code==200 and b'No matching current IDPs found' in response.data
    assert snapshot()==before


# ---------- system test (Flask test client) ----------

def test_tc24_9_notLoggedInOrProfileChanged(searchable,client):
    result=app.test_client().get(SEARCH_URL)
    assert result.status_code==302 and result.headers['Location'].endswith('/designer/login')
    execute("UPDATE user_profile SET status='Suspended' WHERE profileId=2")
    # being logged in is the precondition (UC13), so the search still works for this session
    response=client.get(SEARCH_URL,query_string={'keyword':'Plan'})
    assert response.status_code==200 and b'Kitchen 100%_Plan' in response.data
