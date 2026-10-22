# Unit tests for US9 View user account - written FIRST (TDD)
# admin01 = id 1 (User Admin), admin02 = id 2 (Suspended), cust001 = id 3 (Customer)

from app import app
from database.db import getConnection
from entity.userAccount import UserAccount, hashPassword
from entity.userProfile import UserProfile
from control.viewUserAccountController import ViewUserAccountController


# ---------- ViewUserAccountController.viewUserAccount() ----------

def test_ut9_1_viewUserAccount_active():
    account = ViewUserAccountController().viewUserAccount(3)
    assert account is not None
    assert account.username == "cust001"


def test_ut9_2_viewUserAccount_suspended():
    account = ViewUserAccountController().viewUserAccount(2)
    assert account.username == "admin02"
    assert account.status == "Suspended"


def test_ut9_3_viewUserAccount_notFound():
    assert ViewUserAccountController().viewUserAccount(9999) is None


def test_ut9_4_viewUserAccount_zero():
    assert ViewUserAccountController().viewUserAccount(0) is None


def test_ut9_4b_viewUserAccount_alsoGetsProfile():
    # extra: seq diagram msgs 5-8 - the controller gets the account's profile too,
    # so the page can show the group name
    controller = ViewUserAccountController()
    controller.viewUserAccount(3)
    assert controller.profile.profileName == "Customer"


def test_ut9_4c_viewUserAccount_notFound_noProfile():
    controller = ViewUserAccountController()
    controller.viewUserAccount(9999)
    assert controller.profile is None


# ---------- entity methods ----------

def test_ut9_5_getUserAccount():
    account = UserAccount().getUserAccount(1)
    assert account.username == "admin01"
    assert account.profileId == 1


def test_ut9_6_getUserProfile_ofAccount():
    assert UserProfile().getUserProfile(3).profileName == "Customer"


# ---------- whole page, through the browser (test client) ----------

def loginAsAdmin01(client):
    return client.post("/login", data={"username": "admin01", "password": "Admin@123"})


def test_ut9_7_viewPage_showsDetails():
    # TC9.1
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.get("/accounts/3")
    for text in [b"cust001", b"Chloe Ng", b"cust001@archss.com", b"93456789", b"Customer", b"Active"]:
        assert text in response.data


def test_ut9_8_viewPage_noPassword():
    # TC9.2 - not the password and not the hash either
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.get("/accounts/3")
    assert b"Cust@123" not in response.data
    assert hashPassword("Cust@123").encode() not in response.data


def test_ut9_9_viewPage_suspended():
    # TC9.3
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.get("/accounts/2")
    assert b"Ben Lim" in response.data
    assert b"Suspended" in response.data


def test_ut9_10_viewPage_notFound():
    # TC9.4
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.get("/accounts/9999")
    assert b"Account not found" in response.data


def test_ut9_11_viewPage_changesNothing():
    # TC9.5
    conn = getConnection()
    before = tuple(conn.execute("SELECT * FROM user_account WHERE userId = 3").fetchone())
    client = app.test_client()
    loginAsAdmin01(client)
    client.get("/accounts/3")
    after = tuple(conn.execute("SELECT * FROM user_account WHERE userId = 3").fetchone())
    conn.close()
    assert before == after
