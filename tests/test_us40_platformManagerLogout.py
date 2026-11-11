# Unit tests for US40 Platform manager log out.
# conftest.py creates a fresh database for every test.
# Manager tests add manager40 / Manager@123 (Platform Manager, profile 4).

from app import app
from database.db import getConnection
from entity.userAccount import UserAccount
from control.platformManagerLogoutController import PlatformManagerLogoutController


def createManager40():
    UserAccount().createUserAccount(
        UserAccount(username="manager40", password="Manager@123", fullName="Daniel Tan", email="manager40@archss.com", phone="", profileId=4))


def loginAsManager40(client):
    return client.post("/manager/login", data={"username": "manager40", "password": "Manager@123"})


# ---------- PlatformManagerLogoutController.logout() ----------

def test_ut40_1_logout_loggedIn():
    with app.test_request_context():
        from flask import session
        session["userId"] = 1
        assert PlatformManagerLogoutController().logout() is True
        assert "userId" not in session


def test_ut40_2_logout_notLoggedIn():
    with app.test_request_context():
        assert PlatformManagerLogoutController().logout() is False


def test_ut40_3_logout_twice():
    with app.test_request_context():
        from flask import session
        session["userId"] = 1
        assert PlatformManagerLogoutController().logout() is True
        assert PlatformManagerLogoutController().logout() is False


def test_ut40_4_logout_noUserIdButOtherData():
    # nobody is logged in, but old data is still cleared out
    with app.test_request_context():
        from flask import session
        session["username"] = "old-name"
        session["oldData"] = {"categoryId": 1}
        assert PlatformManagerLogoutController().logout() is False
        assert dict(session) == {}


# ---------- PlatformManagerLogoutPage via the /manager/logout route ----------

def test_ut40_5_dashboard_hasLogoutButton():
    createManager40()
    client = app.test_client()
    loginAsManager40(client)
    response = client.get("/manager/dashboard")
    assert b'action="/manager/logout"' in response.data
    assert b"Log out" in response.data


def test_ut40_6_categoryPages_haveLogoutButton():
    createManager40()
    client = app.test_client()
    loginAsManager40(client)
    response = client.get("/manager/categories")
    assert b'action="/manager/logout"' in response.data


def test_ut40_7_logout_redirectsToManagerLogin():
    createManager40()
    client = app.test_client()
    loginAsManager40(client)
    response = client.post("/manager/logout")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/manager/login")


def test_ut40_8_logout_showsSuccessMessage():
    createManager40()
    client = app.test_client()
    loginAsManager40(client)
    response = client.post("/manager/logout", follow_redirects=True)
    assert b"You have logged out successfully" in response.data
    assert b'name="username"' in response.data


def test_ut40_9_logout_clearsAuthenticationFields():
    createManager40()
    client = app.test_client()
    loginAsManager40(client)
    client.post("/manager/logout")
    with client.session_transaction() as sess:
        assert "userId" not in sess
        assert "profileId" not in sess
        assert "username" not in sess


def test_ut40_10_logout_sessionAlreadyEnded():
    client = app.test_client()
    response = client.post("/manager/logout", follow_redirects=True)
    assert b"Your session has already ended" in response.data


def test_ut40_11_logout_GETNotAllowed():
    createManager40()
    client = app.test_client()
    loginAsManager40(client)
    assert client.get("/manager/logout").status_code == 405
    with client.session_transaction() as sess:
        assert "userId" in sess


def test_ut40_12_afterLogout_dashboardRedirectsToLogin():
    createManager40()
    client = app.test_client()
    loginAsManager40(client)
    client.post("/manager/logout")
    response = client.get("/manager/dashboard")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/manager/login")


def test_ut40_13_afterLogout_categoryPagesRedirectToLogin():
    createManager40()
    client = app.test_client()
    loginAsManager40(client)
    client.post("/manager/logout")
    for url in ("/manager/categories", "/manager/categories/create"):
        response = client.get(url)
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/manager/login")


def test_ut40_14_logout_doesNotChangeAccount():
    createManager40()
    client = app.test_client()
    loginAsManager40(client)
    client.post("/manager/logout")
    conn = getConnection()
    row = conn.execute("SELECT status FROM user_account WHERE username = 'manager40'").fetchone()
    conn.close()
    assert row["status"] == "Active"


def test_ut40_15_canLogInAgainAfterLogout():
    createManager40()
    client = app.test_client()
    loginAsManager40(client)
    client.post("/manager/logout")
    response = loginAsManager40(client)
    assert response.headers["Location"].endswith("/manager/dashboard")


def test_ut40_16_successMessageDisplayedOnce():
    createManager40()
    client = app.test_client()
    loginAsManager40(client)
    client.post("/manager/logout", follow_redirects=True)
    response = client.get("/manager/login")
    assert b"You have logged out successfully" not in response.data


def test_ut40_17_adminLogoutUnchanged():
    client = app.test_client()
    client.post("/login", data={"username": "admin01", "password": "Admin@123"})
    response = client.post("/logout")
    # the US2 admin logout still renders the login page itself, with User Admin picked
    assert response.status_code == 200
    assert b"You have logged out successfully" in response.data
    assert b'value="admin" selected' in response.data
    assert b'value="manager" selected' not in response.data


def test_ut40_18_categoryPages_showLoggedInUsername():
    # the shared manager header (platformManagerBase.html) names who is logged in next to Log out
    createManager40()
    client = app.test_client()
    loginAsManager40(client)
    response = client.get("/manager/categories")
    assert b"Logged in as manager40 (Platform Manager)" in response.data
