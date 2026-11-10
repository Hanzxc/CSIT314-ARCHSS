# Unit tests for US29 Search past IDPs.
# conftest.py gives each test a fresh database. Helpers come from the US25 and US37 tests.

from app import app
from entity.idp import IDP
from control.searchPastIDPController import SearchPastIDPController
from boundary.pastIDPSearchPage import PastIDPSearchPage, MSG_NO_RESULTS, MSG_KEYWORD_TOO_LONG
from test_us37_viewIDPViewStatistics import createDesigner, createCategory, addIDP
from test_us25_addPastIDP import loggedInDesigner, addPast


def titles(idps):
    return sorted(idp.title for idp in idps)


# ---------- IDP.searchByKeywordAndDesigner() ----------

def test_ut29_1_search_titleDescriptionLocationOrCategory_anyCapitals():
    designer = createDesigner()
    kitchen = createCategory("Kitchen")
    bedroom = createCategory("Bedroom")
    addPast(designer, kitchen, "Modern Kitchen")
    addPast(designer, bedroom, "Cosy Loft")
    assert titles(IDP().searchByKeywordAndDesigner("MODERN", designer)) == ["Modern Kitchen"]
    assert titles(IDP().searchByKeywordAndDesigner("bedroom", designer)) == ["Cosy Loft"]       # category
    assert titles(IDP().searchByKeywordAndDesigner("test project", designer)) == ["Cosy Loft", "Modern Kitchen"]


def test_ut29_2_search_onlyOwnActivePastIDPs():
    designer = createDesigner()
    other = createDesigner("designer29b")
    kitchen = createCategory("Kitchen")
    addPast(designer, kitchen, "My Kitchen")
    addPast(designer, kitchen, "My Deleted Kitchen", status="Suspended")
    addIDP(designer, kitchen, "My Current Kitchen")
    addPast(other, kitchen, "Their Kitchen")
    assert titles(IDP().searchByKeywordAndDesigner("kitchen", designer)) == ["My Kitchen"]


def test_ut29_3_search_emptyKeywordGivesAll_noMatchGivesEmpty():
    designer = createDesigner()
    addPast(designer, createCategory("Kitchen"), "Modern Kitchen")
    assert titles(IDP().searchByKeywordAndDesigner("", designer)) == ["Modern Kitchen"]
    assert IDP().searchByKeywordAndDesigner("zzz", designer) == []


def test_ut29_10_search_percentAndUnderscoreAreJustText():
    designer = createDesigner()
    kitchen = createCategory("Kitchen")
    addPast(designer, kitchen, "Modern Kitchen")
    addPast(designer, kitchen, "100% Recycled_Wood Kitchen")
    # % and _ used to be LIKE wildcards that matched every row
    assert titles(IDP().searchByKeywordAndDesigner("%", designer)) == ["100% Recycled_Wood Kitchen"]
    assert titles(IDP().searchByKeywordAndDesigner("_", designer)) == ["100% Recycled_Wood Kitchen"]
    assert IDP().searchByKeywordAndDesigner("k%n", designer) == []


# ---------- SearchPastIDPController / PastIDPSearchPage.validateKeyword() ----------

def test_ut29_4_controller_passesThrough():
    designer = createDesigner()
    addPast(designer, createCategory("Kitchen"), "Modern Kitchen")
    assert titles(SearchPastIDPController().searchPastIDPs(designer, "modern")) == ["Modern Kitchen"]


def test_ut29_5_validateKeyword_lengthLimitOnly():
    page = PastIDPSearchPage()
    assert page.validateKeyword("") is None and page.validateKeyword("a" * 100) is None
    assert page.validateKeyword("a" * 101) == MSG_KEYWORD_TOO_LONG


# ---------- the page through the Flask route ----------

def test_ut29_6_page_showsMatchesAndKeepsKeyword():
    client, designer = loggedInDesigner()
    kitchen = createCategory("Kitchen")
    addPast(designer, kitchen, "Modern Kitchen")
    addPast(designer, kitchen, "Rustic Kitchen")
    html = client.get("/designer/past-idps/search?keyword=  modern ").get_data(as_text=True)
    assert "Modern Kitchen" in html and "Rustic Kitchen" not in html and 'value="modern"' in html


def test_ut29_7_page_noMatch_showsMessage():
    client, designer = loggedInDesigner()
    addPast(designer, createCategory("Kitchen"), "Modern Kitchen")
    html = client.get("/designer/past-idps/search?keyword=zzz").get_data(as_text=True)
    assert MSG_NO_RESULTS in html and "Modern Kitchen" not in html


def test_ut29_8_page_keywordTooLong_showsError():
    client, _ = loggedInDesigner()
    response = client.get("/designer/past-idps/search?keyword=" + "a" * 101)
    assert response.status_code == 400 and MSG_KEYWORD_TOO_LONG in response.get_data(as_text=True)


def test_ut29_9_page_notLoggedIn_redirectsToDesignerLogin():
    response = app.test_client().get("/designer/past-idps/search?keyword=x")
    assert response.status_code == 302 and "/designer/login" in response.headers["Location"]
