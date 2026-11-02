# Unit tests for US5 Update user profile - written FIRST (TDD)
# profile 2 = Interior Designer, 3 = Customer (see seedData.py)

from app import app
from database.db import getConnection
from entity.userProfile import UserProfile
from control.updateUserProfileController import UpdateUserProfileController
from boundary.updateUserProfilePage import UpdateUserProfilePage


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

def test_ut5_3_updateUserProfile_valid():
    newPermissions = ["Manage company profile", "Manage own IDPs", "View IDP statistics"]
    success = UpdateUserProfileController().updateUserProfile(
        2, "Interior Designer", "Designers who show their company, IDPs and statistics", newPermissions)
    assert success is True

    profile = UserProfile().getUserProfile(2)
    assert profile.description == "Designers who show their company, IDPs and statistics"
    assert profile.permissions == newPermissions


def test_ut5_4_updateUserProfile_nameTaken():
    before = UserProfile().getUserProfile(2)
    success = UpdateUserProfileController().updateUserProfile(2, "Customer", "", ["Manage own IDPs"])
    assert success is False

    after = UserProfile().getUserProfile(2)
    assert after.profileName == before.profileName
    assert after.description == before.description
    assert after.permissions == before.permissions


def test_ut5_5_updateUserProfile_notFound():
    assert UpdateUserProfileController().updateUserProfile(9999, "Ghost", "", ["Generate reports"]) is False


def test_ut5_6_updateUserProfile_emptyName():
    assert UpdateUserProfileController().updateUserProfile(2, "", "", ["Manage own IDPs"]) is False


def test_ut5_7_updateUserProfile_noPermissions():
    assert UpdateUserProfileController().updateUserProfile(2, "Interior Designer", "", []) is False


def test_ut5_8_updateUserProfile_keepsStatus():
    # updating a suspended profile shouldn't make it active again
    suspendProfileInDb(3)
    success = UpdateUserProfileController().updateUserProfile(
        3, "Customer", "Home owners who are renovating", ["Search, view and save IDPs"])
    assert success is True
    assert UserProfile().getUserProfile(3).status == "Suspended"


# ---------- UpdateUserProfilePage.validateInput() ----------

def test_ut5_9_validateInput_51chars():
    assert UpdateUserProfilePage().validateInput("A" * 51, ["Manage own IDPs"]) is False


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


def test_ut5_12_updatePage_nameTaken():
    # extra: wireframe 4c
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.post("/profiles/2/update", data={
        "profileName": "Customer", "description": "", "permissions": ["Manage own IDPs"]})
    assert b"A user profile with this name already exists" in response.data


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
