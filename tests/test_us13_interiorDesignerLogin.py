# Unit tests for US13 Interior designer log in.
# conftest.py creates a fresh database for every test.
# Existing data: admin01 / Admin@123 (User Admin), cust001 / Cust@123 (Customer).
# Designer tests add designer13 / Design@123 (Interior Designer, profile 2).

from app import app
from database.db import getConnection
from entity.userAccount import UserAccount
from control.interiorDesignerLoginController import InteriorDesignerLoginController
from boundary.interiorDesignerLoginPage import InteriorDesignerLoginPage


def createDesigner13():
    UserAccount().createUserAccount(
        "designer13", "Design@123", "Tengku Uda Designer", "designer13@archss.com", "", 2)


def loginAsDesigner13(client):
    return client.post("/designer/login", data={
        "username": "designer13", "password": "Design@123"})


def suspendAccountInDb():
    conn = getConnection()
    conn.execute("UPDATE user_account SET status = 'Suspended' WHERE username = ?", ("designer13",))
    conn.commit()
    conn.close()


def suspendProfileInDb():
    conn = getConnection()
    conn.execute("UPDATE user_profile SET status = 'Suspended' WHERE profileId = ?", (2,))
    conn.commit()
    conn.close()


# ---------- InteriorDesignerLoginController.login() ----------

def test_ut13_1_login_correct():
    createDesigner13()
    account = InteriorDesignerLoginController().login("designer13", "Design@123")
    assert account is not None
    assert account.username == "designer13"
    assert account.profileId == 2


def test_ut13_2_login_wrongPassword():
    createDesigner13()
    assert InteriorDesignerLoginController().login("designer13", "Wrong@123") is None


def test_ut13_3_login_noSuchUser():
    assert InteriorDesignerLoginController().login("nobody13", "Design@123") is None


def test_ut13_4_login_suspendedAccount():
    createDesigner13()
    suspendAccountInDb()
    assert InteriorDesignerLoginController().login("designer13", "Design@123") is None


def test_ut13_5_login_suspendedProfile():
    createDesigner13()
    suspendProfileInDb()
    assert InteriorDesignerLoginController().login("designer13", "Design@123") is None


def test_ut13_6_login_userAdminCannotUseDesignerLogin():
    assert InteriorDesignerLoginController().login("admin01", "Admin@123") is None


def test_ut13_7_login_customerCannotUseDesignerLogin():
    assert InteriorDesignerLoginController().login("cust001", "Cust@123") is None


def test_ut13_8_login_missingDesignerPermission():
    createDesigner13()
    conn = getConnection()
    conn.execute("UPDATE user_profile SET permissions = ? WHERE profileId = ?",
                 ('["Manage company profile"]', 2))
    conn.commit()
    conn.close()
    assert InteriorDesignerLoginController().login("designer13", "Design@123") is None


# ---------- UserAccount.verifyCredentials() (existing shared entity) ----------

def test_ut13_9_verifyCredentials_designer():
    createDesigner13()
    account = UserAccount().verifyCredentials("designer13", "Design@123")
    assert account is not None
    assert account.username == "designer13"
    assert account.password != "Design@123"


# ---------- InteriorDesignerLoginPage.validateInput() ----------

def test_ut13_10_validateInput_emptyUsername():
    assert InteriorDesignerLoginPage().validateInput("", "Design@123") is False


def test_ut13_11_validateInput_emptyPassword():
    assert InteriorDesignerLoginPage().validateInput("designer13", "") is False


def test_ut13_12_validateInput_spacesOnlyUsername():
    assert InteriorDesignerLoginPage().validateInput("   ", "Design@123") is False


def test_ut13_13_validateInput_filledIn():
    assert InteriorDesignerLoginPage().validateInput("designer13", "Design@123") is True


# ---------- whole page, through Flask's test client (no browser needed) ----------

def test_ut13_14_loginPage_showsForm():
    client = app.test_client()
    response = client.get("/designer/login")
    assert response.status_code == 200
    assert b"Interior Designer" in response.data
    assert b'name="username"' in response.data
    assert b'type="password"' in response.data


def test_ut13_15_loginPage_success():
    createDesigner13()
    client = app.test_client()
    response = loginAsDesigner13(client)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/designer/dashboard")
    with client.session_transaction() as session:
        assert session["username"] == "designer13"
        assert session["profileId"] == 2
        assert "userId" in session
        assert "password" not in session


def test_ut13_16_loginPage_wrongPassword():
    createDesigner13()
    client = app.test_client()
    response = client.post("/designer/login", data={
        "username": "designer13", "password": "Wrong@123"})
    assert b"Invalid login details or access unavailable" in response.data
    with client.session_transaction() as session:
        assert "userId" not in session


def test_ut13_17_loginPage_missingFields():
    client = app.test_client()
    response = client.post("/designer/login", data={"username": "", "password": ""})
    assert b"Please enter your username and password" in response.data


def test_ut13_18_loginPage_suspendedAccount():
    createDesigner13()
    suspendAccountInDb()
    client = app.test_client()
    response = loginAsDesigner13(client)
    assert b"Invalid login details or access unavailable" in response.data
    with client.session_transaction() as session:
        assert "userId" not in session


def test_ut13_19_dashboard_showsDesignerOptions():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/dashboard")
    assert response.status_code == 200
    assert b"Welcome back, designer13" in response.data
    assert b"Company Profile" in response.data
    assert b"Current IDPs" in response.data
    assert b"Past IDPs" in response.data
    assert b"User Accounts" not in response.data


def test_ut13_20_dashboard_notLoggedIn():
    client = app.test_client()
    response = client.get("/designer/dashboard")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/designer/login")


def test_ut13_21_dashboard_accessRemovedAfterLogin():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    suspendProfileInDb()
    assert client.get("/designer/dashboard").status_code == 403


def test_ut13_22_designer_cannotOpenAdminAccounts():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    assert client.get("/accounts").status_code == 403


def test_ut13_23_sharedLogin_redirectsDesigner():
    createDesigner13()
    client = app.test_client()
    response = client.post("/login", data={
        "username": "designer13", "password": "Design@123"})
    assert response.headers["Location"].endswith("/designer/dashboard")


def test_ut13_24_sharedLogin_stillWorksForAdmin():
    client = app.test_client()
    response = client.post("/login", data={
        "username": "admin01", "password": "Admin@123"})
    assert response.headers["Location"].endswith("/dashboard")
    assert client.get("/accounts").status_code == 200
