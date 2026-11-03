# Unit tests for US11 Suspend user account - written FIRST (TDD)
# admin01 = id 1 (the admin who is logged in), admin02 = id 2 (already Suspended), cust001 = id 3

from app import app
from database.db import getConnection
from entity.userAccount import UserAccount
from control.suspendUserAccountController import SuspendUserAccountController
from control.loginController import LoginController


def countAccounts():
    conn = getConnection()
    total = conn.execute("SELECT COUNT(*) FROM user_account").fetchone()[0]
    conn.close()
    return total


# ---------- SuspendUserAccountController.suspendUserAccount() ----------

def test_ut11_1_suspendUserAccount_valid():
    assert SuspendUserAccountController().suspendUserAccount(3) is True
    assert UserAccount().getUserAccount(3).status == "Suspended"


def test_ut11_2_suspendUserAccount_alreadySuspended():
    assert SuspendUserAccountController().suspendUserAccount(2) is False


def test_ut11_3_suspendPage_ownAccount():
    # admin can't lock themselves out - the page checks this before calling the controller
    client = app.test_client()
    client.post("/login", data={"username": "admin01", "password": "Admin@123"})
    response = client.post("/accounts/1/suspend", data={"choice": "suspend"}, follow_redirects=True)
    assert b"This user account cannot be suspended" in response.data
    assert UserAccount().getUserAccount(1).status == "Active"


def test_ut11_4_suspendUserAccount_notFound():
    assert SuspendUserAccountController().suspendUserAccount(9999) is False


# ---------- after suspending ----------

def test_ut11_5_isActive_afterSuspend():
    SuspendUserAccountController().suspendUserAccount(3)
    assert UserAccount().getUserAccount(3).isActive() is False


def test_ut11_6_login_afterSuspend():
    SuspendUserAccountController().suspendUserAccount(3)
    assert LoginController().login("cust001", "Cust@123") is None


def test_ut11_6b_otherUsersCanStillLogIn():
    # extra: TC11.3
    SuspendUserAccountController().suspendUserAccount(3)
    assert LoginController().login("admin01", "Admin@123") is not None


def test_ut11_7_suspend_deletesNothing():
    before = countAccounts()
    assert UserAccount().suspendUserAccount(3) is True
    assert countAccounts() == before


# ---------- whole page, through the browser (test client) ----------

def loginAsAdmin01(client):
    return client.post("/login", data={"username": "admin01", "password": "Admin@123"})


def test_ut11_8_suspendButton_showsConfirmation():
    # TC11.6 - the box names the account, and nothing is suspended yet
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.get("/accounts/3/suspend")
    assert b"Are you sure" in response.data
    assert b"cust001" in response.data
    assert b"Chloe Ng" in response.data
    assert UserAccount().getUserAccount(3).status == "Active"


def test_ut11_9_suspendPage_success():
    # TC11.1
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.post("/accounts/3/suspend", data={"choice": "ok"}, follow_redirects=True)
    assert b"User account suspended successfully" in response.data
    assert b"Suspended" in response.data


def test_ut11_10_confirmation_cancel():
    # TC11.5
    client = app.test_client()
    loginAsAdmin01(client)
    client.post("/accounts/3/suspend", data={"choice": "cancel"})
    assert UserAccount().getUserAccount(3).status == "Active"


def test_ut11_11_suspendPage_ownAccount():
    # alt flow 4a, e.g. someone types the URL in by hand
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.post("/accounts/1/suspend", data={"choice": "ok"}, follow_redirects=True)
    assert b"This user account cannot be suspended" in response.data
    assert UserAccount().getUserAccount(1).status == "Active"


def test_ut11_12_noSuspendButton_ownOrSuspended():
    # TC11.7, TC11.8
    client = app.test_client()
    loginAsAdmin01(client)
    assert b"/accounts/1/suspend" not in client.get("/accounts/1").data
    assert b"/accounts/2/suspend" not in client.get("/accounts/2").data
    assert b"/accounts/3/suspend" in client.get("/accounts/3").data
