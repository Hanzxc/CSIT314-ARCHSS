# Unit tests for US19 Interior designer log out.
# conftest.py creates a fresh database for every test.
# Designer tests add designer13 / Design@123 (Tengku Uda Designer, profile 2).

from flask import session

from app import app
from database.db import getConnection
from entity.userAccount import UserAccount
from entity.companyProfile import CompanyProfile
from control.interiorDesignerLogoutController import InteriorDesignerLogoutController


def createDesigner13():
    UserAccount().createUserAccount(
        UserAccount(username="designer13", password="Design@123", fullName="Tengku Uda Designer", email="designer13@archss.com", phone="", profileId=2))
    return UserAccount().verifyCredentials("designer13", "Design@123").userId


def companyData():
    return {"companyName": "Uda Interiors", "description": "Interior design for homes.",
            "services": "Space planning, renovation", "email": "hello@udainteriors.com",
            "phone": "+65 6123 4567", "address": "10 Design Street"}


def createCompanyForDesigner13():
    userId = createDesigner13()
    # the entity takes a CompanyProfile object now, not a dict
    CompanyProfile().createCompanyProfile(CompanyProfile(designerId=userId, **companyData()))
    return userId


def loginAsDesigner13(client):
    return client.post("/designer/login", data={"username": "designer13", "password": "Design@123"})


def companyRows():
    conn = getConnection()
    rows = conn.execute("SELECT * FROM company_profile ORDER BY companyId").fetchall()
    conn.close()
    return [tuple(row) for row in rows]


# ---------- InteriorDesignerLogoutController.logout() ----------

def test_ut19_1_logout_loggedIn():
    with app.test_request_context():
        session["userId"] = 4
        session["profileId"] = 2
        session["username"] = "designer13"
        assert InteriorDesignerLogoutController().logout() is True
        assert dict(session) == {}


def test_ut19_2_logout_notLoggedIn():
    with app.test_request_context():
        assert InteriorDesignerLogoutController().logout() is False
        assert dict(session) == {}


def test_ut19_3_logout_twice():
    with app.test_request_context():
        session["userId"] = 4
        assert InteriorDesignerLogoutController().logout() is True
        assert InteriorDesignerLogoutController().logout() is False


def test_ut19_4_logout_clearsPendingDelete():
    with app.test_request_context():
        session["userId"] = 4
        session["companyDeleteConfirmation"] = {"companyId": 1, "token": "old-token"}
        assert InteriorDesignerLogoutController().logout() is True
        assert "companyDeleteConfirmation" not in session


def test_ut19_5_logout_clearsStaleAnonymousData():
    with app.test_request_context():
        session["username"] = "old-name"
        session["companyDeleteConfirmation"] = {"token": "old-token"}
        assert InteriorDesignerLogoutController().logout() is False
        assert dict(session) == {}


# ---------- whole page, through the browser (test client) ----------

def test_ut19_6_dashboard_showsLogoutButton():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/dashboard")
    assert b'action="/designer/logout"' in response.data
    assert b"Log out" in response.data


def test_ut19_7_allDesignerPages_showLogoutButton():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    for path in ["/designer/company", "/designer/company/create", "/designer/company/update",
                 "/designer/company/delete", "/designer/company/search"]:
        response = client.get(path)
        assert b'action="/designer/logout"' in response.data
        assert b"Log out" in response.data


def test_ut19_8_logout_redirectsToDesignerLogin():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.post("/designer/logout")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/designer/login")


def test_ut19_9_logout_showsSuccessMessage():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.post("/designer/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"You have logged out successfully" in response.data
    assert b"Interior Designer" in response.data
    assert b'name="username"' in response.data
    assert b"Logged in as designer13" not in response.data


def test_ut19_10_logout_clearsAuthenticationFields():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    client.post("/designer/logout", follow_redirects=True)
    with client.session_transaction() as currentSession:
        assert "userId" not in currentSession
        assert "profileId" not in currentSession
        assert "username" not in currentSession


def test_ut19_11_logout_sessionAlreadyEnded():
    client = app.test_client()
    response = client.post("/designer/logout", follow_redirects=True)
    assert b"Your session has already ended" in response.data
    assert b"You have logged out successfully" not in response.data


def test_ut19_12_logout_repeatedRequest():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    client.post("/designer/logout", follow_redirects=True)
    response = client.post("/designer/logout", follow_redirects=True)
    assert b"Your session has already ended" in response.data


def test_ut19_13_logout_GETNotAllowed():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    assert client.get("/designer/logout").status_code == 405
    assert client.get("/designer/dashboard").status_code == 200


def test_ut19_14_protectedPages_afterLogout():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    client.post("/designer/logout", follow_redirects=True)
    for path in ["/designer/dashboard", "/designer/company", "/designer/company/create",
                 "/designer/company/update", "/designer/company/delete", "/designer/company/search?keyword=design"]:
        response = client.get(path)
        assert response.status_code == 302
        assert response.headers["Location"].endswith("/designer/login")


def test_ut19_15_cannotCreateAfterLogout():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    client.post("/designer/logout")
    response = client.post("/designer/company/create", data=companyData())
    assert response.status_code == 302
    assert companyRows() == []


def test_ut19_16_cannotUpdateAfterLogout():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    before = companyRows()
    client.post("/designer/logout")
    data = companyData()
    data["companyName"] = "Unauthorised change"
    assert client.post("/designer/company/update", data=data).status_code == 302
    assert companyRows() == before


def test_ut19_17_cannotDeleteWithOldConfirmationAfterLogout():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    client.get("/designer/company/delete")
    with client.session_transaction() as currentSession:
        confirmation = dict(currentSession["companyDeleteConfirmation"])
    before = companyRows()
    client.post("/designer/logout")
    response = client.post("/designer/company/delete", data={"choice": "delete", "companyId": str(confirmation["companyId"]),
                           "confirmationToken": confirmation["token"]})
    assert response.status_code == 302
    assert companyRows() == before


def test_ut19_18_logout_doesNotChangeCompanyOrAccount():
    userId = createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    before = companyRows()
    client.post("/designer/logout")
    assert companyRows() == before
    assert UserAccount().getUserAccount(userId).status == "Active"


def test_ut19_19_canLoginAgainAfterLogout():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    client.post("/designer/logout", follow_redirects=True)
    response = loginAsDesigner13(client)
    assert response.headers["Location"].endswith("/designer/dashboard")
    assert b"Uda Interiors" in client.get("/designer/company").data


def test_ut19_20_logout_clearsOldDeleteConfirmationBeforeRelogin():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    client.get("/designer/company/delete")
    with client.session_transaction() as currentSession:
        confirmation = dict(currentSession["companyDeleteConfirmation"])
    client.post("/designer/logout", follow_redirects=True)
    loginAsDesigner13(client)
    response = client.post("/designer/company/delete", data={"choice": "delete", "companyId": str(confirmation["companyId"]),
                           "confirmationToken": confirmation["token"]})
    assert response.status_code == 400
    assert len(companyRows()) == 1


def test_ut19_21_logout_allowsSuspendedAccountToEndSession():
    userId = createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    conn = getConnection()
    conn.execute("UPDATE user_account SET status='Suspended' WHERE userId=?", (userId,))
    conn.commit()
    conn.close()
    response = client.post("/designer/logout", follow_redirects=True)
    assert b"You have logged out successfully" in response.data
    with client.session_transaction() as currentSession:
        assert "userId" not in currentSession


def test_ut19_22_logout_doesNotEndAnotherBrowserSession():
    createDesigner13()
    firstClient = app.test_client()
    secondClient = app.test_client()
    loginAsDesigner13(firstClient)
    loginAsDesigner13(secondClient)
    firstClient.post("/designer/logout")
    assert firstClient.get("/designer/dashboard").status_code == 302
    assert secondClient.get("/designer/dashboard").status_code == 200


def test_ut19_23_responses_noStore():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    assert client.get("/designer/dashboard").headers["Cache-Control"] == "no-store"
    response = client.post("/designer/logout", follow_redirects=True)
    assert response.headers["Cache-Control"] == "no-store"


def test_ut19_24_existingAdminLogout_stillWorks():
    client = app.test_client()
    client.post("/login", data={"username": "admin01", "password": "Admin@123"})
    response = client.post("/logout")
    assert b"You have logged out successfully" in response.data
    assert b'form method="POST" action="/login"' in response.data
    assert client.get("/dashboard").status_code == 302


def test_ut19_25_logout_successMessageDisplayedOnce():
    createDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.post("/designer/logout", follow_redirects=True)
    assert b"You have logged out successfully" in response.data
    assert b"You have logged out successfully" not in client.get("/designer/login").data


def test_ut19_26_header_companyViewStillReadOnly():
    createCompanyForDesigner13()
    client = app.test_client()
    loginAsDesigner13(client)
    response = client.get("/designer/company")
    assert b'action="/designer/logout"' in response.data
    companyContent = response.data.split(b'<main class="content">', 1)[1]
    assert b"<textarea" not in companyContent
    assert b'type="submit"' not in companyContent
