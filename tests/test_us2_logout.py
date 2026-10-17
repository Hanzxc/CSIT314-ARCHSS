# Unit tests for US2 Log out - written FIRST (TDD)
# logout() uses the flask session, so these run inside a fake request (app.test_request_context)

from flask import session

from app import app
from control.logoutController import LogoutController


# ---------- LogoutController.logout() ----------

def test_ut2_1_logout_loggedIn():
    with app.test_request_context():
        session["userId"] = 1           # pretend admin01 is logged in
        session["profileId"] = 1
        session["username"] = "admin01"

        assert LogoutController().logout() is True
        assert "userId" not in session  # session has no logged-in user afterwards


def test_ut2_2_logout_notLoggedIn():
    with app.test_request_context():
        # nobody logged in - must return False, not throw an error
        assert LogoutController().logout() is False


def test_ut2_3_logout_twice():
    with app.test_request_context():
        session["userId"] = 1
        session["profileId"] = 1

        assert LogoutController().logout() is True
        assert LogoutController().logout() is False


# ---------- whole page, through the browser (test client) ----------

def loginAsAdmin01(client):
    return client.post("/login", data={"username": "admin01", "password": "Admin@123"})


def test_ut2_4_logoutButton_showsLoggedOutMessage():
    # extra: wireframe 4b
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.post("/logout")
    assert b"You have logged out successfully" in response.data


def test_ut2_5_logoutButton_sessionAlreadyEnded():
    # extra: wireframe 4c - clicking Log out when the session is already gone
    client = app.test_client()
    response = client.post("/logout")
    assert b"Your session has already ended" in response.data


def test_ut2_6_adminPageAfterLogout_goesBackToLogin():
    # extra: wireframe 4b note 2 - Back / opening an admin link after logging out
    client = app.test_client()
    loginAsAdmin01(client)
    client.post("/logout")
    response = client.get("/dashboard")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
