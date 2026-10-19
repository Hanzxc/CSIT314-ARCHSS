# Unit tests for US7 Search user profiles - written FIRST (TDD)
# the Lab 2 doc doesn't have UT cases so I made these from the use case description:
#  - searches the name AND the description, capitals don't matter
#  - empty keyword -> every profile (alt flow 1a)
#  - nothing matches -> "No user profiles found" (alt flow 3a)
#  - suspended profiles still show up

from app import app
from database.db import getConnection
from entity.userProfile import UserProfile
from control.searchUserProfileController import SearchUserProfileController


def suspendProfileInDb(profileId):
    conn = getConnection()
    conn.execute("UPDATE user_profile SET status = 'Suspended' WHERE profileId = ?", (profileId,))
    conn.commit()
    conn.close()


def namesOf(profiles):
    return [p.profileName for p in profiles]


# ---------- UserProfile.searchUserProfiles() ----------

def test_ut7_1_search_byName():
    profiles = UserProfile().searchUserProfiles("Customer")
    assert namesOf(profiles) == ["Customer"]


def test_ut7_2_search_byDescription():
    # "renovating" is only in Customer's description, not in any name
    profiles = UserProfile().searchUserProfiles("renovating")
    assert namesOf(profiles) == ["Customer"]


def test_ut7_3_search_capitals():
    profiles = UserProfile().searchUserProfiles("dESIGNER")
    assert namesOf(profiles) == ["Interior Designer"]


def test_ut7_4_search_partialWord():
    # "Manage" is in the descriptions of User Admin and Platform Manager
    profiles = UserProfile().searchUserProfiles("Manage")
    assert sorted(namesOf(profiles)) == ["Platform Manager", "User Admin"]


def test_ut7_5_search_emptyKeyword_returnsAll():
    profiles = UserProfile().searchUserProfiles("")
    assert len(profiles) == 4


def test_ut7_6_search_noMatch():
    # empty list, not None
    assert UserProfile().searchUserProfiles("zzzzz") == []


def test_ut7_7_search_includesSuspended():
    suspendProfileInDb(3)
    profiles = UserProfile().searchUserProfiles("Customer")
    assert len(profiles) == 1
    assert profiles[0].status == "Suspended"


def test_ut7_8_search_doesNotChangeData():
    before = [(p.profileName, p.status) for p in UserProfile().searchUserProfiles("")]
    UserProfile().searchUserProfiles("Customer")
    after = [(p.profileName, p.status) for p in UserProfile().searchUserProfiles("")]
    assert before == after


# ---------- SearchUserProfileController.searchUserProfiles() ----------

def test_ut7_9_controller_search():
    assert namesOf(SearchUserProfileController().searchUserProfiles("Customer")) == ["Customer"]


def test_ut7_10_controller_search_spacesOnly():
    # someone just hitting space then Search should still see everything
    assert len(SearchUserProfileController().searchUserProfiles("   ")) == 4


def test_ut7_11_controller_search_trimsKeyword():
    assert namesOf(SearchUserProfileController().searchUserProfiles("  Customer  ")) == ["Customer"]


# ---------- whole page, through the browser (test client) ----------

def loginAsAdmin01(client):
    return client.post("/login", data={"username": "admin01", "password": "Admin@123"})


def test_ut7_12_searchPage_showsResults():
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.get("/profiles?keyword=designer")
    assert b"Interior Designer" in response.data
    assert b"Platform Manager" not in response.data


def test_ut7_13_searchPage_noResults():
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.get("/profiles?keyword=zzzzz")
    assert b"No user profiles found" in response.data


def test_ut7_14_searchPage_noKeyword_showsAll():
    client = app.test_client()
    loginAsAdmin01(client)
    response = client.get("/profiles")
    for name in [b"User Admin", b"Interior Designer", b"Customer", b"Platform Manager"]:
        assert name in response.data


def test_ut7_15_searchPage_notLoggedIn():
    client = app.test_client()
    response = client.get("/profiles?keyword=Customer")
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")
