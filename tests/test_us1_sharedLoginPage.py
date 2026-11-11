# Unit tests for US1 Log in - the shared login page (UT1.13 - UT1.22). one /login page for US1, US13, US30 and US39.
# the "Log in as" box picks the role, and that role's own boundary + controller does the check
# test data (see conftest.py): admin01 / Admin@123, designer1 / Pass@123, cust001 / Cust@123,
# plus manager39 / Manager@123 made here

import pytest

from app import app
from entity.userAccount import UserAccount


@pytest.fixture
def client():
    UserAccount().createUserAccount(
        UserAccount(username="manager39", password="Manager@123", fullName="Daniel Tan",
                    email="manager39@archss.com", phone="", profileId=4))
    return app.test_client()


def logIn(client, role, username, password):
    return client.post("/login", data={"role": role, "username": username, "password": password})


# ---------- the page ----------

def test_ut1_13_pageShowsAllFourRoles(client):
    response = client.get("/login")
    assert response.status_code == 200
    for value in [b"admin", b"designer", b"customer", b"manager"]:
        assert b'<option value="' + value + b'"' in response.data
    # nothing picked in the URL = User Admin, same as /login always was
    assert b'value="admin" selected' in response.data


@pytest.mark.parametrize("role", ["admin", "designer", "customer", "manager"])
def test_ut1_14_roleInUrlIsPreselected(client, role):
    response = client.get(f"/login?role={role}")
    assert response.data.count(b"selected") == 1
    assert f'value="{role}" selected'.encode() in response.data


def test_ut1_15_unknownRoleInUrlFallsBackToAdmin(client):
    assert b'value="admin" selected' in client.get("/login?role=hacker").data


@pytest.mark.parametrize("oldUrl, role", [
    ("/designer/login", "designer"), ("/customer/login", "customer"), ("/manager/login", "manager")])
def test_ut1_16_oldAddressesRedirect(client, oldUrl, role):
    response = client.get(oldUrl)
    assert response.status_code == 302
    assert response.headers["Location"].endswith(f"/login?role={role}")


# ---------- logging in through the dropdown ----------

@pytest.mark.parametrize("role, username, password, dashboard", [
    ("admin", "admin01", "Admin@123", "/dashboard"),
    ("designer", "designer1", "Pass@123", "/designer/dashboard"),
    ("customer", "cust001", "Cust@123", "/customer/dashboard"),
    ("manager", "manager39", "Manager@123", "/manager/dashboard"),
])
def test_ut1_17_eachRoleGoesToItsDashboard(client, role, username, password, dashboard):
    response = logIn(client, role, username, password)
    assert response.status_code == 302
    assert response.headers["Location"].endswith(dashboard)
    with client.session_transaction() as session:
        assert session["username"] == username


@pytest.mark.parametrize("role, username, password", [
    ("admin", "cust001", "Cust@123"),        # customer picked User Admin by mistake
    ("customer", "admin01", "Admin@123"),
    ("designer", "cust001", "Cust@123"),
    ("manager", "designer1", "Pass@123"),
])
def test_ut1_18_wrongRoleIsRejected(client, role, username, password):
    response = logIn(client, role, username, password)
    assert response.status_code == 200
    assert b"Invalid login details" in response.data
    # the role they picked stays picked so they can see what went wrong
    assert f'value="{role}" selected'.encode() in response.data
    with client.session_transaction() as session:
        assert "userId" not in session


def test_ut1_19_noRoleSentMeansUserAdmin(client):
    # an old form with no role field still logs a User Admin in, like /login did before
    response = client.post("/login", data={"username": "admin01", "password": "Admin@123"})
    assert response.headers["Location"].endswith("/dashboard")


def test_ut1_20_madeUpRoleShowsChooseRoleMessage(client):
    response = logIn(client, "hacker", "admin01", "Admin@123")
    assert response.status_code == 200
    assert b"Please choose who you are logging in as" in response.data
    with client.session_transaction() as session:
        assert "userId" not in session


def test_ut1_21_emptyFieldsStillCaughtForEveryRole(client):
    for role in ["admin", "designer", "customer", "manager"]:
        response = logIn(client, role, "", "")
        assert b"Please enter your username and password" in response.data


@pytest.mark.parametrize("logoutUrl, role", [
    ("/designer/logout", "designer"), ("/customer/logout", "customer"), ("/manager/logout", "manager")])
def test_ut1_22_logoutGoesBackToSharedPageWithRolePicked(client, logoutUrl, role):
    # logout still sends you to the role's old address, which opens the shared page with the role picked
    response = client.post(logoutUrl, follow_redirects=True)
    assert response.request.path == "/login" and response.request.args["role"] == role
    assert f'value="{role}" selected'.encode() in response.data
    assert b"logged out" in response.data or b"session has already ended" in response.data
