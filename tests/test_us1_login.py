# Unit tests for US1 Log in - written FIRST (TDD), then code until they pass
# test data (see conftest.py): admin01 / Admin@123 (Active), admin02 (Suspended account),
# cust001 / Cust@123 (Customer, profile 3)

from app import app
from database.db import getConnection
from entity.userAccount import UserAccount
from control.loginController import LoginController, REQUIRED_ADMIN_PERMISSIONS
from boundary.loginPage import LoginPage


def suspendProfileInDb(profileId):
    # set a profile to Suspended straight in the database (don't rely on US6 code here)
    conn = getConnection()
    conn.execute("UPDATE user_profile SET status = 'Suspended' WHERE profileId = ?", (profileId,))
    conn.commit()
    conn.close()


# ---------- UserAccount.verifyCredentials() ----------

def test_ut1_1_verifyCredentials_correct():
    account = UserAccount().verifyCredentials("admin01", "Admin@123", REQUIRED_ADMIN_PERMISSIONS)
    assert account is not None
    assert account.username == "admin01"
    assert account.profileId == 1


def test_ut1_1b_verifyCredentials_passwordIsHashed():
    # extra: the password we get back must be the hash, not the real password
    account = UserAccount().verifyCredentials("admin01", "Admin@123", REQUIRED_ADMIN_PERMISSIONS)
    assert account is not None
    assert account.password != "Admin@123"


def test_ut1_2_verifyCredentials_wrongPassword():
    assert UserAccount().verifyCredentials("admin01", "Wrong@999", REQUIRED_ADMIN_PERMISSIONS) is None


def test_ut1_3_verifyCredentials_noSuchUser():
    assert UserAccount().verifyCredentials("nobody99", "Admin@123", REQUIRED_ADMIN_PERMISSIONS) is None


def test_ut1_4_verifyCredentials_empty():
    # must return None, not throw an error
    assert UserAccount().verifyCredentials("", "", REQUIRED_ADMIN_PERMISSIONS) is None


def test_ut1_5_verifyCredentials_accountSuspended():
    # admin02 has the right password but the account is Suspended
    assert UserAccount().verifyCredentials("admin02", "Admin@123", REQUIRED_ADMIN_PERMISSIONS) is None


# ---------- UserAccount.isActive() ----------

def test_ut1_5b_isActive():
    # extra: the status check the entity uses
    assert UserAccount(username="admin01", status="Active").isActive() is True
    assert UserAccount(username="admin02", status="Suspended").isActive() is False


# ---------- LoginController.login() ----------

def test_ut1_6_login_correct():
    account = LoginController().login("admin01", "Admin@123")
    assert account is not None
    assert account.username == "admin01"


def test_ut1_7_login_accountSuspended():
    assert LoginController().login("admin02", "Admin@123") is None


def test_ut1_8_login_profileSuspended():
    suspendProfileInDb(1)       # User Admin profile - admin01 itself is still Active
    assert LoginController().login("admin01", "Admin@123") is None


# ---------- LoginPage.validateInput() ----------

def test_ut1_9_validateInput_emptyPassword():
    assert LoginPage().validateInput("admin01", "") is False


def test_ut1_9b_validateInput_emptyUsername():
    # extra: the other empty field
    assert LoginPage().validateInput("", "Admin@123") is False


def test_ut1_10_validateInput_filledIn():
    assert LoginPage().validateInput("admin01", "Admin@123") is True


# ---------- not a User Admin ----------

def test_ut1_11_login_notUserAdmin():
    # cust001 and its Customer profile are Active, but /login is only for User Admins
    assert LoginController().login("cust001", "Cust@123") is None


# ---------- LoginPage.submitLogin() through the browser (test client) ----------

def test_ut1_12_submitLogin_trimsUsername():
    client = app.test_client()
    response = client.post("/login", data={"username": "  admin01  ", "password": "Admin@123"})
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/dashboard")
    with client.session_transaction() as state:
        assert state["username"] == "admin01"


def test_ut1_12b_loginFailed_keepsUsername():
    # extra: wireframe 4b - the username stays in the box, the password box is cleared
    client = app.test_client()
    response = client.post("/login", data={"username": "admin01", "password": "Wrong@999"})
    assert b"Invalid login details or account suspended" in response.data
    assert b'value="admin01"' in response.data
    assert b"Wrong@999" not in response.data


# ---------- system tests (TC) ----------

def test_tc1_9_notUserAdmin_cannotLogIn():
    client = app.test_client()
    response = client.post("/login", data={"username": "cust001", "password": "Cust@123"})
    assert response.status_code == 200
    assert b"Invalid login details or account suspended" in response.data
    with client.session_transaction() as state:
        assert "userId" not in state
    # not logged in, so the admin pages send them back to /login
    assert client.get("/dashboard").headers["Location"].endswith("/login")


def test_tc1_10_spacesAroundUsername():
    client = app.test_client()
    response = client.post("/login", data={"username": "  admin01  ", "password": "Admin@123"},
                           follow_redirects=True)
    assert b"Logged in as admin01 (User Admin)" in response.data
