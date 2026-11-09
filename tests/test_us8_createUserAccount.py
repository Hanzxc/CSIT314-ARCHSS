# Unit tests for US8 Create user account - written FIRST (TDD)
# profiles: 1 User Admin, 2 Interior Designer, 3 Customer, 4 Platform Manager
# accounts: admin01, admin02, cust001

from app import app
from database.db import getConnection
from entity.userAccount import UserAccount, hashPassword
from control.createUserAccountController import CreateUserAccountController
from control.interiorDesignerLoginController import REQUIRED_DESIGNER_PERMISSIONS
from boundary.createUserAccountPage import CreateUserAccountPage


def countAccounts():
    conn = getConnection()
    total = conn.execute("SELECT COUNT(*) FROM user_account").fetchone()[0]
    conn.close()
    return total


def getAccountRow(username):
    conn = getConnection()
    row = conn.execute("SELECT * FROM user_account WHERE username = ?", (username,)).fetchone()
    conn.close()
    return row


def suspendProfileInDb(profileId):
    # straight in the database so these tests don't depend on the US6 code
    conn = getConnection()
    conn.execute("UPDATE user_profile SET status = 'Suspended' WHERE profileId = ?", (profileId,))
    conn.commit()
    conn.close()


def makeAccount(username, password, fullName, email, phone, profileId):
    # the UserAccount the page builds after trimming the input
    return UserAccount(username=username, password=password, fullName=fullName,
                       email=email, phone=phone, profileId=profileId)


# ---------- CreateUserAccountController.createUserAccount() ----------

def test_ut8_1_createUserAccount_valid():
    created = CreateUserAccountController().createUserAccount(
        makeAccount("des001", "Des@123", "Daniel Koh", "des001@archss.com", "94567890", 2))
    assert created is True
    row = getAccountRow("des001")
    assert row["status"] == "Active"
    assert row["profileId"] == 2


def test_ut8_2_createUserAccount_usernameTaken():
    before = countAccounts()
    created = CreateUserAccountController().createUserAccount(
        makeAccount("cust001", "Cust@123", "Chris Ong", "", "", 3))
    assert created is False
    assert countAccounts() == before


def test_ut8_3_createUserAccount_suspendedProfile():
    suspendProfileInDb(4)
    created = CreateUserAccountController().createUserAccount(
        makeAccount("pm001", "Pm@123", "Paul Goh", "", "", 4))
    assert created is False
    assert getAccountRow("pm001") is None


def test_ut8_4_createUserAccount_noSuchProfile():
    created = CreateUserAccountController().createUserAccount(
        makeAccount("des001", "Des@123", "Daniel Koh", "des001@archss.com", "94567890", 9999))
    assert created is False


def test_ut8_4b_createUserAccount_optionalFieldsEmpty():
    # extra: TC8.3 - email and phone can be left empty
    assert CreateUserAccountController().createUserAccount(
        makeAccount("des002", "Des@123", "Dana Lee", "", "", 2)) is True


def test_ut8_4c_createPage_emptyRequired_nothingSaved():
    # extra: the page checks the input, so a missing password never reaches the controller
    client = app.test_client()
    client.post("/login", data={"username": "admin01", "password": "Admin@123"})
    client.post("/accounts/create", data={
        "username": "des001", "password": "", "fullName": "Daniel Koh",
        "email": "", "phone": "", "profileId": "2"})
    assert getAccountRow("des001") is None


def test_ut8_4d_createPage_trimsInput():
    # extra: spaces get trimmed by the page before it's saved
    client = app.test_client()
    client.post("/login", data={"username": "admin01", "password": "Admin@123"})
    client.post("/accounts/create", data={
        "username": "  des001  ", "password": "Des@123", "fullName": "  Daniel Koh ",
        "email": "", "phone": "", "profileId": "2"})
    assert getAccountRow("des001")["fullName"] == "Daniel Koh"


# ---------- UserAccount.isUsernameTaken() ----------

def test_ut8_5_isUsernameTaken_existing():
    assert UserAccount().isUsernameTaken("admin01") is True


def test_ut8_6_isUsernameTaken_new():
    assert UserAccount().isUsernameTaken("nobody99") is False


# ---------- CreateUserAccountPage.validateInput() ----------

def test_ut8_7_validateInput_emptyUsername():
    page = CreateUserAccountPage()
    account = makeAccount("", "Des@123", "Daniel Koh", "des001@archss.com", "94567890", 2)
    assert page.validateInput(account) is False
    assert "username" in page.fieldErrors


def test_ut8_7b_validateInput_allFilledIn():
    assert CreateUserAccountPage().validateInput(makeAccount("des001", "Des@123", "Daniel Koh", "", "", 2)) is True


def test_ut8_7c_validateInput_noProfilePicked():
    assert CreateUserAccountPage().validateInput(
        makeAccount("des001", "Des@123", "Daniel Koh", "", "", None)) is False


# ---------- UserAccount.createUserAccount() ----------

def test_ut8_8_createUserAccount_hashesPassword():
    UserAccount().createUserAccount(makeAccount("des001", "Des@123", "Daniel Koh", "des001@archss.com", "94567890", 2))
    row = getAccountRow("des001")
    assert row["password"] == hashPassword("Des@123")
    assert row["password"] != "Des@123"
    assert len(row["password"]) == 64


def test_ut8_9_newAccount_canLogIn():
    # extra: TC8.2 - the new user can log in straight away. des001 is an Interior Designer,
    # so it's checked with the designer permissions (they log in on /designer/login, US13)
    CreateUserAccountController().createUserAccount(
        makeAccount("des001", "Des@123", "Daniel Koh", "des001@archss.com", "94567890", 2))
    account = UserAccount().verifyCredentials("des001", "Des@123", REQUIRED_DESIGNER_PERMISSIONS)
    assert account is not None
    assert account.username == "des001"


# ---------- whole page, through the browser (test client) ----------

def loginAsAdmin01(client):
    return client.post("/login", data={"username": "admin01", "password": "Admin@123"})


def test_ut8_10_createPage_showsForm():
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.get("/accounts/create")
    assert b"Create user account" in response.data
    assert b"Interior Designer" in response.data       # profile drop-down


def test_ut8_11_createPage_success():
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.post("/accounts/create", data={
        "username": "des001", "password": "Des@123", "fullName": "Daniel Koh",
        "email": "des001@archss.com", "phone": "94567890", "profileId": "2"},
        follow_redirects=True)
    assert b"User account created successfully" in response.data
    assert b"des001" in response.data


def test_ut8_12_createPage_requiredMissing():
    client = app.test_client()
    loginAsAdmin01(client)
    before = countAccounts()
    response = client.post("/accounts/create", data={
        "username": "", "password": "Des@123", "fullName": "Daniel Koh",
        "email": "", "phone": "", "profileId": "2"})
    assert b"Please fill in all required fields" in response.data
    assert b"Daniel Koh" in response.data       # what was typed is kept
    assert countAccounts() == before


def test_ut8_13_createPage_usernameTaken():
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.post("/accounts/create", data={
        "username": "cust001", "password": "Cust@123", "fullName": "Chris Ong",
        "email": "", "phone": "", "profileId": "3"})
    assert b"Invalid profile or username already exists" in response.data


def test_ut8_14_createPage_keepsHeader():
    # extra: the typed username shouldn't replace "Logged in as admin01" in the header
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.post("/accounts/create", data={
        "username": "cust001", "password": "x", "fullName": "Chris Ong",
        "email": "", "phone": "", "profileId": "3"})
    assert b"Logged in as admin01" in response.data
