# Unit tests for US10 Update user account - written FIRST (TDD)
# cust001 = id 3, Chloe Ng, cust001@archss.com, 93456789, profile 3 (Customer)

from app import app
from database.db import getConnection
from entity.userAccount import UserAccount
from control.updateUserAccountController import UpdateUserAccountController
from control.loginController import LoginController
from boundary.updateUserAccountPage import UpdateUserAccountPage


def getAccountRow(userId):
    conn = getConnection()
    row = conn.execute("SELECT * FROM user_account WHERE userId = ?", (userId,)).fetchone()
    conn.close()
    return tuple(row) if row else None


def suspendProfileInDb(profileId):
    conn = getConnection()
    conn.execute("UPDATE user_profile SET status = 'Suspended' WHERE profileId = ?", (profileId,))
    conn.commit()
    conn.close()


# ---------- UpdateUserAccountController.updateUserAccount() ----------

def test_ut10_1_updateUserAccount_valid():
    success = UpdateUserAccountController().updateUserAccount(
        3, "cust001", "Chloe Ng Mei Ling", "cust001@archss.com", "98765432", 3)
    assert success is True
    account = UpdateUserAccountController().getUserAccount(3)
    assert account.fullName == "Chloe Ng Mei Ling"
    assert account.phone == "98765432"


def test_ut10_2_updateUserAccount_usernameTaken():
    before = getAccountRow(3)
    success = UpdateUserAccountController().updateUserAccount(
        3, "admin01", "Chloe Ng", "cust001@archss.com", "93456789", 3)
    assert success is False
    assert getAccountRow(3) == before


def test_ut10_3_updateUserAccount_suspendedProfile():
    suspendProfileInDb(4)
    success = UpdateUserAccountController().updateUserAccount(
        3, "cust001", "Chloe Ng", "cust001@archss.com", "93456789", 4)
    assert success is False
    assert UserAccount().getUserAccount(3).profileId == 3


def test_ut10_4_updateUserAccount_notFound():
    success = UpdateUserAccountController().updateUserAccount(
        9999, "nobody", "Nobody", "", "", 3)
    assert success is False


def test_ut10_4b_updateUserAccount_moveProfile():
    # extra: TC10.3 - move cust001 to Interior Designer
    assert UpdateUserAccountController().updateUserAccount(
        3, "cust001", "Chloe Ng", "cust001@archss.com", "93456789", 2) is True
    assert UserAccount().getUserAccount(3).profileId == 2


# ---------- UserAccount.isUsernameTaken() with a userId ----------

def test_ut10_5_isUsernameTaken_ownUsername():
    assert UserAccount().isUsernameTaken("cust001", 3) is False


def test_ut10_6_isUsernameTaken_someoneElses():
    assert UserAccount().isUsernameTaken("cust001", 1) is True


# ---------- UpdateUserAccountPage.validateInput() ----------

def test_ut10_7_validateInput_emptyFullName():
    page = UpdateUserAccountPage()
    assert page.validateInput("cust001", "", "cust001@archss.com", "93456789", 3) is False
    assert "fullName" in page.fieldErrors


# ---------- UserAccount.updateUserAccount() ----------

def test_ut10_8_updateUserAccount_keepsPasswordStatusDate():
    conn = getConnection()
    before = conn.execute("SELECT password, status, createdDate FROM user_account WHERE userId = 3").fetchone()
    UserAccount().updateUserAccount(3, "cust001", "Chloe Ng Mei Ling", "cust001@archss.com", "98765432", 3)
    after = conn.execute("SELECT password, status, createdDate FROM user_account WHERE userId = 3").fetchone()
    conn.close()
    assert tuple(before) == tuple(after)


def test_ut10_9_oldPasswordStillWorks():
    # extra: TC10.7
    UpdateUserAccountController().updateUserAccount(
        3, "cust001", "Chloe Ng Mei Ling", "cust001@archss.com", "98765432", 3)
    assert LoginController().login("cust001", "Cust@123") is not None


# ---------- whole page, through the browser (test client) ----------

def loginAsAdmin01(client):
    return client.post("/login", data={"username": "admin01", "password": "Admin@123"})


def test_ut10_10_updatePage_formFilledIn():
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.get("/accounts/3/update")
    assert b"Update user account" in response.data
    assert b"Chloe Ng" in response.data
    assert b"cust001@archss.com" in response.data


def test_ut10_11_updatePage_success():
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.post("/accounts/3/update", data={
        "username": "cust001", "fullName": "Chloe Ng Mei Ling",
        "email": "cust001@archss.com", "phone": "98765432", "profileId": "3"},
        follow_redirects=True)
    assert b"User account updated successfully" in response.data
    assert b"Chloe Ng Mei Ling" in response.data


def test_ut10_12_updatePage_requiredMissing():
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.post("/accounts/3/update", data={
        "username": "cust001", "fullName": "",
        "email": "typed@archss.com", "phone": "93456789", "profileId": "3"})
    assert b"Please fill in all required fields" in response.data
    assert b"typed@archss.com" in response.data
    assert UserAccount().getUserAccount(3).fullName == "Chloe Ng"


def test_ut10_13_updatePage_usernameTaken():
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.post("/accounts/3/update", data={
        "username": "admin01", "fullName": "Chloe Ng",
        "email": "cust001@archss.com", "phone": "93456789", "profileId": "3"})
    assert b"Invalid profile or username already exists" in response.data
    assert b"Logged in as admin01" in response.data


def test_ut10_14_updatePage_notFound():
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.get("/accounts/9999/update")
    assert b"Account not found" in response.data
