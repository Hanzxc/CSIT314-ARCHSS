# Unit tests for US4 View user profile - written FIRST (TDD)

from app import app
from database.db import getConnection
from entity.userProfile import UserProfile
from control.viewUserProfileController import ViewUserProfileController


def suspendProfileInDb(profileId):
    # set it straight in the database so this test doesn't depend on the US6 code
    conn = getConnection()
    conn.execute("UPDATE user_profile SET status = 'Suspended' WHERE profileId = ?", (profileId,))
    conn.commit()
    conn.close()


# ---------- UserProfile.getUserProfile() ----------

def test_ut4_1_getUserProfile_userAdmin():
    profile = UserProfile().getUserProfile(1)
    assert profile is not None
    assert profile.profileName == "User Admin"
    assert len(profile.permissions) == 2


def test_ut4_2_getUserProfile_suspended():
    suspendProfileInDb(3)
    profile = UserProfile().getUserProfile(3)
    assert profile.profileName == "Customer"
    assert profile.status == "Suspended"


def test_ut4_3_getUserProfile_notFound():
    assert UserProfile().getUserProfile(9999) is None


def test_ut4_4_getUserProfile_negativeId():
    # should just give None back, not crash
    assert UserProfile().getUserProfile(-1) is None


# ---------- ViewUserProfileController.getUserProfile() ----------

def test_ut4_5_controller_getUserProfile():
    fromController = ViewUserProfileController().getUserProfile(3)
    fromEntity = UserProfile().getUserProfile(3)
    assert fromController is not None
    assert fromController.profileId == fromEntity.profileId
    assert fromController.profileName == fromEntity.profileName
    assert fromController.permissions == fromEntity.permissions
    assert fromController.status == fromEntity.status


def test_ut4_6_controller_getUserProfile_zero():
    assert ViewUserProfileController().getUserProfile(0) is None


# ---------- whole page, through the browser (test client) ----------

def loginAsAdmin01(client):
    return client.post("/login", data={"username": "admin01", "password": "Admin@123"})


def test_ut4_7_viewPage_showsDetails():
    # extra: wireframe 4b, TC4.1
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.get("/profiles/3")
    assert b"Customer" in response.data
    assert b"Search, view and save IDPs" in response.data
    assert b"Active" in response.data


def test_ut4_8_viewPage_notFound():
    # extra: wireframe 4c
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.get("/profiles/9999")
    assert b"User profile not found" in response.data


def test_ut4_9_viewPage_notLoggedIn():
    # extra: can't see profiles without logging in first
    client = app.test_client()
    response = client.get("/profiles/3")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
