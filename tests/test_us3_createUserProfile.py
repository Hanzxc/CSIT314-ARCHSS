# Unit tests for US3 Create user profile - written FIRST (TDD)
# test data (see conftest.py): the 4 default profiles, 1 User Admin, 2 Interior Designer,
# 3 Customer, 4 Platform Manager

from app import app
from database.db import getConnection
from entity.userProfile import UserProfile
from control.createUserProfileController import CreateUserProfileController
from boundary.createUserProfilePage import CreateUserProfilePage


def countProfiles():
    # how many rows are in user_profile right now
    conn = getConnection()
    total = conn.execute("SELECT COUNT(*) FROM user_profile").fetchone()[0]
    conn.close()
    return total


def getStatusByName(profileName):
    conn = getConnection()
    row = conn.execute("SELECT status FROM user_profile WHERE profileName = ?", (profileName,)).fetchone()
    conn.close()
    return row["status"] if row else None


# ---------- UserProfile.getAllPermissions() ----------

def test_ut3_1_getAllPermissions():
    permissionList = UserProfile().getAllPermissions()
    assert len(permissionList) == 8
    assert "Manage user accounts" in permissionList
    assert "Generate reports" in permissionList


# ---------- UserProfile.isProfileNameTaken() ----------

def test_ut3_2_isProfileNameTaken_existing():
    assert UserProfile().isProfileNameTaken("Customer") is True


def test_ut3_3_isProfileNameTaken_capitals():
    # capitals shouldn't matter
    assert UserProfile().isProfileNameTaken("cUSTOMER") is True


def test_ut3_4_isProfileNameTaken_new():
    assert UserProfile().isProfileNameTaken("Customer Support") is False


# ---------- CreateUserProfileController.createUserProfile() ----------

def test_ut3_5_createUserProfile_valid():
    success = CreateUserProfileController().createUserProfile(
        "Customer Support", "Staff who help customers with their problems", ["Manage user accounts"])
    assert success is True
    assert getStatusByName("Customer Support") == "Active"


def test_ut3_6_createUserProfile_nameTaken():
    before = countProfiles()
    success = CreateUserProfileController().createUserProfile("Customer", "", ["Search, view and save IDPs"])
    assert success is False
    assert countProfiles() == before       # nothing got added


def test_ut3_7_createUserProfile_emptyName():
    assert CreateUserProfileController().createUserProfile("", "", ["Manage user accounts"]) is False


def test_ut3_8_createUserProfile_noPermissions():
    assert CreateUserProfileController().createUserProfile("Guest", "", []) is False


# ---------- CreateUserProfilePage.validateInput() ----------

def test_ut3_9_validateInput_2chars():
    assert CreateUserProfilePage().validateInput("AB", ["Generate reports"]) is False


def test_ut3_10_validateInput_3chars():
    assert CreateUserProfilePage().validateInput("Ops", ["Generate reports"]) is True


def test_ut3_11_validateInput_50chars():
    assert CreateUserProfilePage().validateInput("A" * 50, ["Generate reports"]) is True


def test_ut3_12_validateInput_51chars():
    assert CreateUserProfilePage().validateInput("A" * 51, ["Generate reports"]) is False


def test_ut3_12b_validateInput_noPermission_setsFieldError():
    # extra: the page should know WHICH field is wrong so it can highlight it (wireframe 4c)
    page = CreateUserProfilePage()
    assert page.validateInput("Guest", []) is False
    assert "permissions" in page.fieldErrors


# ---------- whole page, through the browser (test client) ----------

def loginAsAdmin01(client):
    return client.post("/login", data={"username": "admin01", "password": "Admin@123"})


def test_ut3_13_createPage_success():
    # extra: wireframe 4d - goes back to the list with the green message
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.post("/profiles/create", data={
        "profileName": "Guest", "description": "",
        "permissions": ["Search, view and save IDPs"]}, follow_redirects=True)
    assert b"User profile created successfully" in response.data
    assert b"Guest" in response.data


def test_ut3_14_createPage_nameTaken_keepsWhatWasTyped():
    # extra: alt flow 5a - error shown and the typed description isn't lost
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.post("/profiles/create", data={
        "profileName": "cUSTOMER", "description": "typed this already",
        "permissions": ["Search, view and save IDPs"]})
    assert b"A user profile with this name already exists" in response.data
    assert b"typed this already" in response.data
