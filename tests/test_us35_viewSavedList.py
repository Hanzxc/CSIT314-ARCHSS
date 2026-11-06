# Unit tests for US35 View saved list.
# conftest.py gives each test a fresh database (cust001 / Cust@123 is the customer).
# Helpers come from the US33, US34 and US37 tests.

from app import app
from database.db import getConnection
from entity.savedIDP import SavedIDP
from control.viewSavedListController import ViewSavedListController
from boundary.savedListPage import MSG_NO_SAVED
from test_us37_viewIDPViewStatistics import createDesigner, customerId, createCategory, addIDP, addSave
from test_us33_saveIDP import loggedInCustomer
from test_us34_searchSavedList import savedProjects, titles


# ---------- SavedIDP.getSavedRecords() ----------

def test_ut35_1_getSavedRecords_onlySavedOnes():
    savedProjects()
    assert titles(SavedIDP().getSavedRecords(customerId())) == ["Cosy Loft", "Modern Kitchen"]


def test_ut35_2_getSavedRecords_mostRecentlySavedFirst():
    designer = createDesigner()
    kitchen = createCategory("Kitchen")
    first = addIDP(designer, kitchen, "Saved First")
    second = addIDP(designer, kitchen, "Saved Second")
    addSave(customerId(), first, "2026-11-01 12:00:00")
    addSave(customerId(), second, "2026-11-05 12:00:00")
    assert [idp.title for idp in SavedIDP().getSavedRecords(customerId())] == ["Saved Second", "Saved First"]


def test_ut35_3_getSavedRecords_hidesDeletedAndSuspendedCategory():
    savedProjects()
    conn = getConnection()
    conn.execute("UPDATE idp SET status = 'Suspended' WHERE title = 'Modern Kitchen'")
    conn.execute("UPDATE idp_category SET status = 'Suspended' WHERE categoryName = 'Bedroom'")
    conn.commit()
    conn.close()
    assert SavedIDP().getSavedRecords(customerId()) == []


def test_ut35_4_getSavedRecords_includesCategoryAndType():
    savedProjects()
    kitchen = [idp for idp in SavedIDP().getSavedRecords(customerId()) if idp.title == "Modern Kitchen"][0]
    assert kitchen.categoryName == "Kitchen" and kitchen.projectType == "Current"


# ---------- ViewSavedListController ----------

def test_ut35_5_controller_passesThrough():
    savedProjects()
    assert titles(ViewSavedListController().getSavedList(customerId())) == ["Cosy Loft", "Modern Kitchen"]


# ---------- SavedListPage through the Flask route ----------

def test_ut35_6_page_showsSavedIDPsWithViewLinks():
    savedProjects()
    html = loggedInCustomer().get("/customer/saved-list").get_data(as_text=True)
    assert "Saved IDPs" in html and "Modern Kitchen" in html and "Cosy Loft" in html
    assert "Not Saved Kitchen" not in html and 'href="/customer/idps/' in html


def test_ut35_7_page_nothingSaved_showsEmptyMessage():
    html = loggedInCustomer().get("/customer/saved-list").get_data(as_text=True)
    assert MSG_NO_SAVED in html


def test_ut35_8_page_notLoggedIn_redirectsToCustomerLogin():
    response = app.test_client().get("/customer/saved-list")
    assert response.status_code == 302 and response.headers["Location"].endswith("/customer/login")


def test_ut35_9_dashboardAndMenu_linkToSavedList():
    html = loggedInCustomer().get("/customer/dashboard").get_data(as_text=True)
    assert html.count('href="/customer/saved-list"') == 2
