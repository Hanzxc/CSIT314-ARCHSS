# Unit tests for US12 Search user account - written FIRST (TDD)
# test data (see conftest.py): admin01 (Alice Tan, Active), admin02 (Ben Lim, Suspended),
# cust001 (Chloe Ng, Active)

from app import app
from database.db import getConnection
from entity.userAccount import UserAccount
from control.searchUserAccountController import SearchUserAccountController


def usernamesOf(accounts):
    return [a.username for a in accounts]


# ---------- SearchUserAccountController.searchUserAccounts() ----------

def test_ut12_1_search_partOfUsername():
    accounts = SearchUserAccountController().searchUserAccounts("admin0")
    assert usernamesOf(accounts) == ["admin01", "admin02"]


def test_ut12_2_search_capitals():
    accounts = SearchUserAccountController().searchUserAccounts("CHLOE")
    assert usernamesOf(accounts) == ["cust001"]


def test_ut12_3_search_emptyKeyword_returnsAll():
    assert len(SearchUserAccountController().searchUserAccounts("")) == 3


def test_ut12_4_search_noMatch():
    # empty list, not None
    assert SearchUserAccountController().searchUserAccounts("zzzz") == []


def test_ut12_5_search_includesSuspended():
    accounts = SearchUserAccountController().searchUserAccounts("Ben")
    assert usernamesOf(accounts) == ["admin02"]
    assert accounts[0].status == "Suspended"


def test_ut12_6_searchPage_trimsKeyword():
    # the page trims the keyword now, not the controller
    client = app.test_client()
    client.post("/login", data={"username": "admin01", "password": "Admin@123"})
    response = client.get("/accounts?keyword=%20%20chloe%20%20")
    assert b"cust001" in response.data
    assert b"admin02" not in response.data


# ---------- UserAccount.searchUserAccounts() ----------

def test_ut12_7_search_byEmail():
    accounts = UserAccount().searchUserAccounts("cust001@archss")
    assert usernamesOf(accounts) == ["cust001"]


def test_ut12_8_search_doesNotChangeData():
    # extra: postcondition - nothing in the system is changed
    conn = getConnection()
    before = conn.execute("SELECT * FROM user_account ORDER BY userId").fetchall()
    UserAccount().searchUserAccounts("admin")
    after = conn.execute("SELECT * FROM user_account ORDER BY userId").fetchall()
    conn.close()
    assert [tuple(r) for r in before] == [tuple(r) for r in after]


def test_ut12_9_searchPage_spacesOnly_returnsAll():
    # extra: just hitting space then Search should still show everything
    client = app.test_client()
    client.post("/login", data={"username": "admin01", "password": "Admin@123"})
    response = client.get("/accounts?keyword=%20%20%20")
    assert b"admin02" in response.data
    assert b"cust001" in response.data


# ---------- whole page, through the browser (test client) ----------

def loginAsAdmin01(client):
    return client.post("/login", data={"username": "admin01", "password": "Admin@123"})


def test_ut12_10_searchPage_showsResults():
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.get("/accounts?keyword=chloe")
    assert b"cust001" in response.data
    assert b"Chloe Ng" in response.data
    assert b"admin02" not in response.data


def test_ut12_11_searchPage_noResults():
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.get("/accounts?keyword=zzzz")
    assert b"No user accounts found" in response.data


def test_ut12_12_searchPage_noKeyword_showsAll():
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.get("/accounts")
    for username in [b"admin01", b"admin02", b"cust001"]:
        assert username in response.data


def test_ut12_13_searchPage_notLoggedIn():
    client = app.test_client()
    response = client.get("/accounts?keyword=chloe")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
