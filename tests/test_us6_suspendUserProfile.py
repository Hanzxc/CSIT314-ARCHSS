# Unit tests for US6 Suspend user profile - written FIRST (TDD)
# admin01 is in profile 1 (User Admin), cust001 is in profile 3 (Customer)

from app import app
from database.db import getConnection
from entity.userProfile import UserProfile
from control.suspendUserProfileController import SuspendUserProfileController
from control.viewUserProfileController import ViewUserProfileController
from control.customerLoginController import REQUIRED_CUSTOMER_PERMISSIONS
from entity.userAccount import UserAccount


def countAccountsInProfile(profileId):
    conn = getConnection()
    total = conn.execute("SELECT COUNT(*) FROM user_account WHERE profileId = ?", (profileId,)).fetchone()[0]
    conn.close()
    return total


# ---------- SuspendUserProfileController.suspendUserProfile() ----------

def test_ut6_1_suspendUserProfile_valid():
    assert SuspendUserProfileController().suspendUserProfile(3) is True
    assert UserProfile().getUserProfile(3).status == "Suspended"


def test_ut6_2_suspendUserProfile_alreadySuspended():
    SuspendUserProfileController().suspendUserProfile(3)
    # second time round it's already suspended so it should say no
    assert SuspendUserProfileController().suspendUserProfile(3) is False


def test_ut6_3_suspendPage_ownProfile():
    # admin can't lock themselves out - the page checks this before calling the controller
    client = app.test_client()
    client.post("/login", data={"username": "admin01", "password": "Admin@123"})
    response = client.post("/profiles/1/suspend", data={"choice": "ok"}, follow_redirects=True)
    assert b"This user profile cannot be suspended" in response.data
    assert UserProfile().getUserProfile(1).status == "Active"


def test_ut6_4_suspendUserProfile_notFound():
    assert SuspendUserProfileController().suspendUserProfile(9999) is False


# ---------- after suspending ----------

def test_ut6_5_isActive_afterSuspend():
    SuspendUserProfileController().suspendUserProfile(3)
    assert UserProfile().getUserProfile(3).isActive() is False


def test_ut6_6_verifyCredentials_afterSuspend():
    # cust001 itself is still Active, but its Customer profile isn't any more
    SuspendUserProfileController().suspendUserProfile(3)
    assert UserAccount().verifyCredentials("cust001", "Cust@123", REQUIRED_CUSTOMER_PERMISSIONS) is None


def test_ut6_7_suspend_keepsAccounts():
    # suspending the group shouldn't delete the accounts in it
    before = countAccountsInProfile(3)
    assert UserProfile().suspendUserProfile(3) is True
    assert countAccountsInProfile(3) == before


# ---------- whole page, through the browser (test client) ----------

def loginAsAdmin01(client):
    return client.post("/login", data={"username": "admin01", "password": "Admin@123"})


def test_ut6_8_clickSuspend_notFound(monkeypatch):
    # the page loads the profile for the box with US4's controller - no profile -> error, no box
    calls = []
    realGetUserProfile = ViewUserProfileController.getUserProfile

    def spyGetUserProfile(self, profileId):
        calls.append(profileId)
        return realGetUserProfile(self, profileId)

    monkeypatch.setattr(ViewUserProfileController, "getUserProfile", spyGetUserProfile)
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.get("/profiles/9999/suspend")
    assert calls == [9999]          # one borrowed call, then straight to the error
    response = client.get(response.headers["Location"])
    assert b"This user profile cannot be suspended" in response.data
    assert b"Are you sure" not in response.data


def test_ut6_12_suspendPage_success():
    # extra: wireframe 4c - details page now shows Suspended
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.post("/profiles/3/suspend", follow_redirects=True)
    assert b"User profile suspended successfully" in response.data
    assert b"Suspended" in response.data


def test_ut6_9_suspendPage_ownProfile():
    # extra: alt flow 4a
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.post("/profiles/1/suspend", follow_redirects=True)
    assert b"This user profile cannot be suspended" in response.data


def test_ut6_10_suspendButton_showsConfirmation():
    # extra: wireframe 4b - clicking Suspend only asks, doesn't suspend yet
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.get("/profiles/3/suspend")
    assert b"Are you sure" in response.data
    assert UserProfile().getUserProfile(3).status == "Active"


def test_ut6_11_confirmation_cancel():
    # extra: alt flow 3a - Cancel changes nothing
    client = app.test_client()
    loginAsAdmin01(client)
    client.post("/profiles/3/suspend", data={"choice": "cancel"})
    assert UserProfile().getUserProfile(3).status == "Active"
