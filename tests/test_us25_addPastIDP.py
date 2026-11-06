# Unit tests for US25 Add past IDP.
# conftest.py gives each test a fresh database. Designer + category helpers come from the US37 tests
# (designer37 / Design@123). These are shared with the US26 - US29 tests.

from app import app
from database.db import getConnection
from entity.idp import IDP
from control.addPastIDPController import AddPastIDPController
from boundary.addPastIDPPage import (AddPastIDPPage, MSG_ADDED, MSG_FIX_FIELDS, MSG_NO_CATEGORIES,
                                     MSG_TITLE_LENGTH, MSG_CHOOSE_CATEGORY)
from test_us37_viewIDPViewStatistics import createDesigner, loginAsDesigner, createCategory, addIDP


def loggedInDesigner():
    designerId = createDesigner()
    client = app.test_client()
    loginAsDesigner(client)
    return client, designerId


def addPast(designerId, categoryId, title="Completed Kitchen", status="Active"):
    return addIDP(designerId, categoryId, title, "Past", status)


def pastIDPRow(title):
    conn = getConnection()
    row = conn.execute("SELECT * FROM idp WHERE title = ?", (title,)).fetchone()
    conn.close()
    return row


def form(categoryId, title="Modern 4-Room HDB Resale", description="Open-concept layout", location="Tampines"):
    return {"title": title, "categoryId": categoryId, "description": description, "location": location}


# ---------- IDP.createPastIDP() ----------

def test_ut25_1_createPastIDP_savedAsPastAndActive():
    designer = createDesigner()
    kitchen = createCategory("Kitchen")
    assert IDP().createPastIDP(IDP(designerId=designer, categoryId=kitchen, title="Completed Kitchen",
                                   description="Done", location="Bedok")) is True
    row = pastIDPRow("Completed Kitchen")
    assert row["projectType"] == "Past" and row["status"] == "Active" and row["designerId"] == designer


def test_ut25_2_createPastIDP_suspendedCategoryRefused():
    designer = createDesigner()
    hidden = createCategory("Old Style", "Suspended")
    assert IDP().createPastIDP(IDP(designerId=designer, categoryId=hidden, title="Hidden",
                                   description="Done")) is False
    assert pastIDPRow("Hidden") is None


# ---------- AddPastIDPController.addPastIDP() ----------

def test_ut25_3_controller_passesTheIDPThrough():
    designer = createDesigner()
    idp = IDP(designerId=designer, categoryId=createCategory("Kitchen"), title="Via Controller", description="Done")
    assert AddPastIDPController().addPastIDP(idp) is True
    assert pastIDPRow("Via Controller") is not None


# ---------- AddPastIDPPage.validateInput() ----------

def test_ut25_4_validateInput_rules():
    with app.test_request_context():
        page = AddPastIDPPage()
        kitchen = createCategory("Kitchen")
        assert page.validateInput(IDP(categoryId=kitchen, title="Fine Title", description="Done")) is True
        assert page.validateInput(IDP(categoryId=kitchen, title="", description="")) is False
        assert set(page.fieldErrors) == {"title", "description"}
        assert page.validateInput(IDP(categoryId=kitchen, title="AB", description="Done")) is False
        assert page.fieldErrors["title"] == MSG_TITLE_LENGTH
        assert page.validateInput(IDP(categoryId=999, title="Fine Title", description="Done")) is False
        assert page.fieldErrors["categoryId"] == MSG_CHOOSE_CATEGORY


# ---------- the page through the Flask route ----------

def test_ut25_5_page_openForm_listsActiveCategoriesOnly():
    client, _ = loggedInDesigner()
    createCategory("Kitchen")
    createCategory("Old Style", "Suspended")
    html = client.get("/designer/past-idps/add").get_data(as_text=True)
    assert "Add past IDP" in html and "Kitchen" in html and "Old Style" not in html


def test_ut25_6_page_noCategories_showsMessageAndNoForm():
    client, _ = loggedInDesigner()
    html = client.get("/designer/past-idps/add").get_data(as_text=True)
    assert MSG_NO_CATEGORIES in html and "<form" not in html.split("Add past IDP</h1>")[1]


def test_ut25_7_page_submitValid_savesAndShowsSuccess():
    client, designer = loggedInDesigner()
    kitchen = createCategory("Kitchen")
    response = client.post("/designer/past-idps/add", data=form(kitchen), follow_redirects=True)
    html = response.get_data(as_text=True)
    assert MSG_ADDED in html and "Modern 4-Room HDB Resale" in html
    assert pastIDPRow("Modern 4-Room HDB Resale")["designerId"] == designer


def test_ut25_8_page_missingTitle_keepsTypedInputAndSavesNothing():
    client, _ = loggedInDesigner()
    kitchen = createCategory("Kitchen")
    response = client.post("/designer/past-idps/add", data=form(kitchen, title=""))
    html = response.get_data(as_text=True)
    assert MSG_FIX_FIELDS in html and "Open-concept layout" in html
    conn = getConnection()
    assert conn.execute("SELECT COUNT(*) FROM idp").fetchone()[0] == 0
    conn.close()


def test_ut25_9_page_ownerAlwaysTheLoggedInDesigner():
    client, designer = loggedInDesigner()
    other = createDesigner("designer25b")
    kitchen = createCategory("Kitchen")
    data = form(kitchen)
    data["designerId"] = other                     # forged form field is ignored
    client.post("/designer/past-idps/add", data=data)
    assert pastIDPRow("Modern 4-Room HDB Resale")["designerId"] == designer


def test_ut25_10_page_notLoggedIn_redirectsToDesignerLogin():
    response = app.test_client().get("/designer/past-idps/add")
    assert response.status_code == 302 and "/designer/login" in response.headers["Location"]
