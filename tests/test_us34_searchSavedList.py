# Unit tests for US34 Search saved list.
# conftest.py gives each test a fresh database (cust001 / Cust@123 is the customer).
# Helpers come from the US33 and US37 tests.

from app import app
from entity.savedIDP import SavedIDP
from entity.userAccount import UserAccount
from control.searchSavedListController import SearchSavedListController
from boundary.savedListPage import SavedListPage, MSG_NO_RESULTS, MSG_KEYWORD_TOO_LONG
from test_us37_viewIDPViewStatistics import createDesigner, customerId, createCategory, addIDP
from test_us33_saveIDP import loggedInCustomer
from control.customerLoginController import REQUIRED_CUSTOMER_PERMISSIONS


def savedProjects():
    # two saved IDPs for cust001 and one IDP that is not saved
    designer = createDesigner()
    kitchen = createCategory("Kitchen")
    bedroom = createCategory("Bedroom")
    for title, category in (("Modern Kitchen", kitchen), ("Cosy Loft", bedroom)):
        SavedIDP().createSavedRecord(customerId(), addIDP(designer, category, title))
    addIDP(designer, kitchen, "Not Saved Kitchen")


def titles(idps):
    return sorted(idp.title for idp in idps)


# ---------- SavedIDP.searchSavedRecords() ----------

def test_ut34_1_search_onlyInTheSavedList_anyCapitals():
    savedProjects()
    assert titles(SavedIDP().searchSavedRecords(customerId(), "KITCHEN")) == ["Modern Kitchen"]
    assert titles(SavedIDP().searchSavedRecords(customerId(), "bedroom")) == ["Cosy Loft"]     # category


def test_ut34_2_search_otherCustomersListNotIncluded():
    savedProjects()
    UserAccount().createUserAccount(UserAccount(username="cust034", password="Cust@123", fullName="Other Customer", email="c34@archss.com", phone="", profileId=3))
    other = UserAccount().verifyCredentials("cust034", "Cust@123", REQUIRED_CUSTOMER_PERMISSIONS).userId
    assert SavedIDP().searchSavedRecords(other, "kitchen") == []


def test_ut34_3_search_emptyKeywordGivesWholeList_noMatchGivesEmpty():
    savedProjects()
    assert titles(SavedIDP().searchSavedRecords(customerId(), "")) == ["Cosy Loft", "Modern Kitchen"]
    assert SavedIDP().searchSavedRecords(customerId(), "zzz") == []


# ---------- SearchSavedListController / SavedListPage.validateKeyword() ----------

def test_ut34_4_controller_passesThrough():
    savedProjects()
    assert titles(SearchSavedListController().searchSavedList(customerId(), "loft")) == ["Cosy Loft"]


def test_ut34_5_validateKeyword_lengthLimitOnly():
    page = SavedListPage()
    assert page.validateKeyword("") is None
    assert page.validateKeyword("a" * 101) == MSG_KEYWORD_TOO_LONG


# ---------- the page through the Flask route ----------

def test_ut34_6_page_showsMatchesAndKeepsKeyword():
    savedProjects()
    html = loggedInCustomer().get("/customer/saved-list/search?keyword=kitchen").get_data(as_text=True)
    assert "Modern Kitchen" in html and "Cosy Loft" not in html and "Not Saved Kitchen" not in html
    assert 'value="kitchen"' in html


def test_ut34_7_page_noMatch_showsMessage():
    savedProjects()
    html = loggedInCustomer().get("/customer/saved-list/search?keyword=zzz").get_data(as_text=True)
    assert MSG_NO_RESULTS in html


def test_ut34_8_page_keywordTooLong_showsError():
    response = loggedInCustomer().get("/customer/saved-list/search?keyword=" + "a" * 101)
    assert response.status_code == 400 and MSG_KEYWORD_TOO_LONG in response.get_data(as_text=True)


def test_ut34_9_page_notLoggedIn_redirectsToCustomerLogin():
    response = app.test_client().get("/customer/saved-list/search?keyword=x")
    assert response.status_code == 302 and response.headers["Location"].endswith("/customer/login")
