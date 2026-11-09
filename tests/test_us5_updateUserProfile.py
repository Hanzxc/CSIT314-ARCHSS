# Unit tests for US5 Update user profile - written FIRST (TDD)
# profile 2 = Interior Designer, 3 = Customer (see seedData.py)

from app import app
from database.db import getConnection
from entity.userProfile import UserProfile
from control.updateUserProfileController import UpdateUserProfileController
from boundary.updateUserProfilePage import UpdateUserProfilePage, MSG_CANNOT_UPDATE


def suspendProfileInDb(profileId):
    conn = getConnection()
    conn.execute("UPDATE user_profile SET status = 'Suspended' WHERE profileId = ?", (profileId,))
    conn.commit()
    conn.close()


# ---------- UserProfile.isProfileNameTaken(name, id) ----------

def test_ut5_1_isProfileNameTaken_ownName():
    # keeping your own name is fine
    assert UserProfile().isProfileNameTaken("Interior Designer", 2) is False


def test_ut5_2_isProfileNameTaken_otherName():
    assert UserProfile().isProfileNameTaken("Customer", 2) is True


# ---------- UpdateUserProfileController.updateUserProfile() ----------

def makeProfile(profileId, profileName, description, permissions):
    # the UserProfile the page builds (keyword args - the 1st parameter is profileId)
    return UserProfile(profileId=profileId, profileName=profileName, description=description,
                       permissions=permissions)


def test_ut5_3_updateUserProfile_valid():
    newPermissions = ["Manage company profile", "Manage own IDPs", "View IDP statistics"]
    updated = UpdateUserProfileController().updateUserProfile(makeProfile(
        2, "Interior Designer", "Designers who show their company, IDPs and statistics", newPermissions))
    assert updated is True

    profile = UserProfile().getUserProfile(2)
    assert profile.description == "Designers who show their company, IDPs and statistics"
    assert profile.permissions == newPermissions


def test_ut5_4_updateUserProfile_nameTaken():
    before = UserProfile().getUserProfile(2)
    updated = UpdateUserProfileController().updateUserProfile(makeProfile(2, "Customer", "", ["Manage own IDPs"]))
    assert updated is False

    after = UserProfile().getUserProfile(2)
    assert after.profileName == before.profileName
    assert after.description == before.description
    assert after.permissions == before.permissions


def test_ut5_5_updateUserProfile_notFound():
    profile = makeProfile(9999, "Ghost", "", ["Generate reports"])
    assert UpdateUserProfileController().updateUserProfile(profile) is False


def test_ut5_6_updatePage_emptyName_nothingChanged():
    # the page checks the input now, so bad input never reaches the controller
    client = app.test_client()
    client.post("/login", data={"username": "admin01", "password": "Admin@123"})
    client.post("/profiles/2/update", data={"profileName": "", "description": "",
                                            "permissions": ["Manage own IDPs"]})
    assert UserProfile().getUserProfile(2).profileName == "Interior Designer"


def test_ut5_7_updatePage_noPermissions_nothingChanged():
    client = app.test_client()
    client.post("/login", data={"username": "admin01", "password": "Admin@123"})
    client.post("/profiles/2/update", data={"profileName": "Designer", "description": ""})
    assert UserProfile().getUserProfile(2).profileName == "Interior Designer"


def test_ut5_8_updateUserProfile_suspended():
    # a suspended profile can't be updated - nothing changes and it stays Suspended
    suspendProfileInDb(3)
    before = UserProfile().getUserProfile(3)
    updated = UpdateUserProfileController().updateUserProfile(makeProfile(
        3, "Customer", "Home owners who are renovating", ["Search, view and save IDPs"]))
    assert updated is False

    after = UserProfile().getUserProfile(3)
    assert after.status == "Suspended"
    assert after.description == before.description


# ---------- UpdateUserProfilePage.validateInput() ----------

def test_ut5_9_validateInput_51chars():
    assert UpdateUserProfilePage().validateInput(makeProfile(2, "A" * 51, "", ["Manage own IDPs"])) is False


# ---------- whole page, through the browser (test client) ----------

def loginAsAdmin01(client):
    return client.post("/login", data={"username": "admin01", "password": "Admin@123"})


def test_ut5_10_updatePage_formIsPrefilled():
    # extra: wireframe 4b - current details already filled in
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.get("/profiles/2/update")
    assert b"Interior Designer" in response.data
    assert b"Designers who show their company and IDPs" in response.data


def test_ut5_11_updatePage_success():
    # extra: wireframe 4d - back on the details page with the message
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.post("/profiles/2/update", data={
        "profileName": "Interior Designer", "description": "new description here",
        "permissions": ["Manage own IDPs"]}, follow_redirects=True)
    assert b"User profile updated successfully" in response.data
    assert b"new description here" in response.data


def test_ut5_12_updatePage_cannotUpdate():
    # extra: wireframe 4c - the one message for a name that's used or a suspended profile,
    # and the form keeps what was typed
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.post("/profiles/2/update", data={
        "profileName": "Customer", "description": "typed this", "permissions": ["Manage own IDPs"]})
    assert MSG_CANNOT_UPDATE.encode() in response.data
    assert b"typed this" in response.data


def test_ut5_13_updatePage_notFound():
    # extra: opening the update form for a profile that doesn't exist
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.get("/profiles/9999/update")
    assert b"User profile not found" in response.data


def test_ut5_14_updatePage_keepsHeader():
    # bug fix: the profile being edited used to show up as the admin's own group in the header
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.get("/profiles/3/update")
    assert b"Logged in as admin01 (User Admin)" in response.data


# ---------- system tests (TC) ----------

def test_tc5_6_renameToUsedName():
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.post("/profiles/2/update", data={
        "profileName": "Customer", "description": "Designers who show their company and IDPs",
        "permissions": ["Manage company profile", "Manage own IDPs"]})
    assert b"This user profile could not be updated - the name is already used or the profile is suspended"         in response.data
    assert UserProfile().getUserProfile(2).profileName == "Interior Designer"


def test_tc5_11_updateSuspendedProfile():
    suspendProfileInDb(3)
    before = UserProfile().getUserProfile(3)
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.post("/profiles/3/update", data={
        "profileName": "Customer", "description": "Home owners who are renovating",
        "permissions": before.permissions})
    assert b"This user profile could not be updated - the name is already used or the profile is suspended"         in response.data
    assert b"Suspended" in response.data       # the status badge is loaded again
    after = UserProfile().getUserProfile(3)
    assert after.description == before.description
    assert after.status == "Suspended"
