# Unit tests for US39 Platform manager log in.
# conftest.py creates a fresh database for every test.
# Existing data: admin01 / Admin@123 (User Admin), cust001 / Cust@123 (Customer).
# Manager tests add manager39 / Manager@123 (Platform Manager, profile 4).

from app import app
from database.db import getConnection
from entity.userAccount import UserAccount
from control.platformManagerLoginController import PlatformManagerLoginController, REQUIRED_MANAGER_PERMISSIONS
from boundary.platformManagerLoginPage import PlatformManagerLoginPage


def createManager39():
    UserAccount().createUserAccount(
        UserAccount(username="manager39", password="Manager@123", fullName="Daniel Tan", email="manager39@archss.com", phone="", profileId=4))


def loginAsManager39(client):
    return client.post("/manager/login", data={
        "username": "manager39", "password": "Manager@123"})


def suspendAccountInDb():
    conn = getConnection()
    conn.execute("UPDATE user_account SET status = 'Suspended' WHERE username = ?", ("manager39",))
    conn.commit()
    conn.close()


def suspendProfileInDb():
    conn = getConnection()
    conn.execute("UPDATE user_profile SET status = 'Suspended' WHERE profileId = ?", (4,))
    conn.commit()
    conn.close()


# ---------- PlatformManagerLoginController.login() ----------

def test_ut39_1_login_correct():
    createManager39()
    account = PlatformManagerLoginController().login("manager39", "Manager@123")
    assert account is not None
    assert account.username == "manager39"
    assert account.profileId == 4


def test_ut39_2_login_wrongPassword():
    createManager39()
    assert PlatformManagerLoginController().login("manager39", "Wrong@123") is None


def test_ut39_3_login_noSuchUser():
    assert PlatformManagerLoginController().login("nobody13", "Manager@123") is None


def test_ut39_4_login_suspendedAccount():
    createManager39()
    suspendAccountInDb()
    assert PlatformManagerLoginController().login("manager39", "Manager@123") is None


def test_ut39_5_login_suspendedProfile():
    createManager39()
    suspendProfileInDb()
    assert PlatformManagerLoginController().login("manager39", "Manager@123") is None


def test_ut39_6_login_userAdminCannotUseManagerLogin():
    assert PlatformManagerLoginController().login("admin01", "Admin@123") is None


def test_ut39_7_login_customerCannotUseManagerLogin():
    assert PlatformManagerLoginController().login("cust001", "Cust@123") is None


def test_ut39_8_login_missingManagerPermission():
    createManager39()
    conn = getConnection()
    conn.execute("UPDATE user_profile SET permissions = ? WHERE profileId = ?",
                 ('["Manage IDP categories"]', 4))
    conn.commit()
    conn.close()
    assert PlatformManagerLoginController().login("manager39", "Manager@123") is None


# ---------- UserAccount.verifyCredentials() (existing shared entity) ----------

def test_ut39_9_verifyCredentials_manager():
    createManager39()
    account = UserAccount().verifyCredentials("manager39", "Manager@123", REQUIRED_MANAGER_PERMISSIONS)
    assert account is not None
    assert account.username == "manager39"
    assert account.password != "Manager@123"


# ---------- PlatformManagerLoginPage.validateInput() ----------

def test_ut39_10_validateInput_emptyUsername():
    assert PlatformManagerLoginPage().validateInput("", "Manager@123") is False


def test_ut39_11_validateInput_emptyPassword():
    assert PlatformManagerLoginPage().validateInput("manager39", "") is False


def test_ut39_12_validateInput_spacesOnlyUsername():
    assert PlatformManagerLoginPage().validateInput("   ", "Manager@123") is False


def test_ut39_13_validateInput_filledIn():
    assert PlatformManagerLoginPage().validateInput("manager39", "Manager@123") is True


# ---------- whole page, through Flask's test client (no browser needed) ----------

def test_ut39_14_loginPage_showsForm():
    client = app.test_client()
    response = client.get("/manager/login")
    assert response.status_code == 200
    assert b"Platform Manager" in response.data
    assert b'name="username"' in response.data
    assert b'type="password"' in response.data


def test_ut39_15_loginPage_success():
    createManager39()
    client = app.test_client()
    response = loginAsManager39(client)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/manager/dashboard")
    with client.session_transaction() as session:
        assert session["username"] == "manager39"
        assert session["profileId"] == 4
        assert "userId" in session
        assert "password" not in session


def test_ut39_16_loginPage_wrongPassword():
    createManager39()
    client = app.test_client()
    response = client.post("/manager/login", data={
        "username": "manager39", "password": "Wrong@123"})
    assert b"Invalid login details or access unavailable" in response.data
    with client.session_transaction() as session:
        assert "userId" not in session


def test_ut39_17_loginPage_missingFields():
    client = app.test_client()
    response = client.post("/manager/login", data={"username": "", "password": ""})
    assert b"Please enter your username and password" in response.data


def test_ut39_18_loginPage_suspendedAccount():
    createManager39()
    suspendAccountInDb()
    client = app.test_client()
    response = loginAsManager39(client)
    assert b"Invalid login details or access unavailable" in response.data
    with client.session_transaction() as session:
        assert "userId" not in session


def test_ut39_19_dashboard_showsManagerOptions():
    createManager39()
    client = app.test_client()
    loginAsManager39(client)
    response = client.get("/manager/dashboard")
    assert response.status_code == 200
    assert b"Welcome back, manager39" in response.data
    assert b"IDP Categories" in response.data
    assert b"Reports" in response.data
    assert b"User Accounts" not in response.data


def test_ut39_20_dashboard_notLoggedIn():
    client = app.test_client()
    response = client.get("/manager/dashboard")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/manager/login")


def test_ut39_21_dashboard_notRecheckedAfterLogin():
    # being logged in is the precondition, so the dashboard doesn't check the role again -
    # the suspended profile is only stopped at the next login
    createManager39()
    client = app.test_client()
    loginAsManager39(client)
    suspendProfileInDb()
    assert client.get("/manager/dashboard").status_code == 200
    response = loginAsManager39(app.test_client())
    assert b"Invalid login details or access unavailable" in response.data


def test_ut39_22_manager_cannotOpenAdminAccounts():
    # /login is only for User Admins (US1), so a manager gets no session there and
    # loginRequired just sends them back to /login
    createManager39()
    client = app.test_client()
    client.post("/login", data={"username": "manager39", "password": "Manager@123"})
    response = client.get("/accounts")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_ut39_23_sharedLogin_rejectsManager():
    # platform managers log in on /manager/login - the shared /login gives them the US1 error
    createManager39()
    client = app.test_client()
    response = client.post("/login", data={
        "username": "manager39", "password": "Manager@123"})
    assert response.status_code == 200
    assert b"Invalid login details or account suspended" in response.data
    with client.session_transaction() as state:
        assert "userId" not in state


def test_ut39_24_sharedLogin_stillWorksForAdmin():
    client = app.test_client()
    response = client.post("/login", data={
        "username": "admin01", "password": "Admin@123"})
    assert response.headers["Location"].endswith("/dashboard")
    assert client.get("/accounts").status_code == 200


def test_ut39_25_sharedDashboard_noSession_goesToLogin():
    # the User Admin dashboard only checks there's a session (logged in as a User Admin is the
    # precondition) - a manager trying /login never gets one, so /dashboard goes back to /login
    createManager39()
    client = app.test_client()
    client.post("/login", data={"username": "manager39", "password": "Manager@123"})
    assert client.get("/dashboard").headers["Location"].endswith("/login")


def test_ut39_26_login_clearsOldSession():
    createManager39()
    client = app.test_client()
    with client.session_transaction() as session:
        session["oldData"] = {"companyId": 99}
    loginAsManager39(client)
    with client.session_transaction() as session:
        assert "oldData" not in session


def test_ut39_29_login_customProfileUsesPermissions():
    from entity.userProfile import UserProfile
    UserProfile().createUserProfile(UserProfile(profileName="Reporting team", description="", permissions=["Manage IDP categories", "Generate reports"]))
    conn = getConnection()
    profileId = conn.execute("SELECT profileId FROM user_profile WHERE profileName = ?", ("Reporting team",)).fetchone()[0]
    conn.close()
    UserAccount().createUserAccount(UserAccount(username="custom39", password="Manager@123", fullName="Daniel Tan", email="", phone="", profileId=profileId))
    assert PlatformManagerLoginController().login("custom39", "Manager@123") is not None


def test_ut39_30_designer_cannotUseManagerLogin():
    UserAccount().createUserAccount(UserAccount(username="designer39", password="Design@123", fullName="Designer", email="", phone="", profileId=2))
    assert PlatformManagerLoginController().login("designer39", "Design@123") is None


def test_ut39_31_verifyCredentials_userAdminHasNoManagerPermissions():
    assert UserAccount().verifyCredentials("admin01", "Admin@123", REQUIRED_MANAGER_PERMISSIONS) is None


def test_ut39_32_submitLogin_trimsUsername():
    createManager39()
    client = app.test_client()
    response = client.post("/manager/login", data={"username": "  manager39  ", "password": "Manager@123"})
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/manager/dashboard")


# ---------- system tests (TC) ----------

def test_tc39_9_spacesAroundUsername():
    createManager39()
    client = app.test_client()
    response = client.post("/manager/login", data={"username": "  manager39  ", "password": "Manager@123"},
                           follow_redirects=True)
    assert b"Welcome back, manager39" in response.data
    assert b"Logged in as manager39 (Platform Manager)" in response.data
