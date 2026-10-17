# Unit tests for US1 Log in - written FIRST (TDD), then code until they pass
# test data (see conftest.py): admin01 / Admin@123 (Active), admin02 (Suspended account),
# cust001 / Cust@123 (Customer, profile 3)

from database.db import getConnection
from entity.userAccount import UserAccount
from control.loginController import LoginController
from boundary.loginPage import LoginPage


def suspendProfileInDb(profileId):
    # set a profile to Suspended straight in the database (don't rely on US6 code here)
    conn = getConnection()
    conn.execute("UPDATE user_profile SET status = 'Suspended' WHERE profileId = ?", (profileId,))
    conn.commit()
    conn.close()


# ---------- UserAccount.verifyCredentials() ----------

def test_ut1_1_verifyCredentials_correct():
    account = UserAccount().verifyCredentials("admin01", "Admin@123")
    assert account is not None
    assert account.username == "admin01"
    assert account.profileId == 1


def test_ut1_1b_verifyCredentials_passwordIsHashed():
    # extra: the password we get back must be the hash, not the real password
    account = UserAccount().verifyCredentials("admin01", "Admin@123")
    assert account is not None
    assert account.password != "Admin@123"


def test_ut1_2_verifyCredentials_wrongPassword():
    assert UserAccount().verifyCredentials("admin01", "Wrong@999") is None


def test_ut1_3_verifyCredentials_noSuchUser():
    assert UserAccount().verifyCredentials("nobody99", "Admin@123") is None


def test_ut1_4_verifyCredentials_empty():
    # must return None, not throw an error
    assert UserAccount().verifyCredentials("", "") is None


# ---------- UserAccount.isActive() ----------

def test_ut1_5_isActive_suspendedAccount():
    account = UserAccount(username="admin02", status="Suspended")
    assert account.isActive() is False


def test_ut1_5b_isActive_activeAccount():
    # extra: the normal case
    account = UserAccount(username="admin01", status="Active")
    assert account.isActive() is True


# ---------- LoginController.login() ----------

def test_ut1_6_login_correct():
    account = LoginController().login("admin01", "Admin@123")
    assert account is not None
    assert account.username == "admin01"


def test_ut1_7_login_accountSuspended():
    assert LoginController().login("admin02", "Admin@123") is None


def test_ut1_8_login_profileSuspended():
    suspendProfileInDb(3)       # Customer profile
    assert LoginController().login("cust001", "Cust@123") is None


# ---------- LoginPage.validateInput() ----------

def test_ut1_9_validateInput_emptyPassword():
    assert LoginPage().validateInput("admin01", "") is False


def test_ut1_9b_validateInput_emptyUsername():
    # extra: the other empty field
    assert LoginPage().validateInput("", "Admin@123") is False


def test_ut1_10_validateInput_filledIn():
    assert LoginPage().validateInput("admin01", "Admin@123") is True
