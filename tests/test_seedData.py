# Tests for the sample data in database/seedData.py - written FIRST (TDD)
# project spec wants about 100 records per table for the demo.
# conftest.py only adds the 4 default profiles + 3 accounts, so each test
# adds the sample data on top of that itself

from database.db import getConnection
from database.seedData import seedSampleData, makeSampleData, SAMPLE_PASSWORD
from entity.userProfile import ALL_PERMISSIONS
from control.loginController import LoginController
from entity.userAccount import UserAccount
import json


def addSampleData():
    conn = getConnection()
    seedSampleData(conn)
    conn.close()


def getAll(sql):
    conn = getConnection()
    rows = conn.execute(sql).fetchall()
    conn.close()
    return rows


def test_seed_1_atLeast100Profiles():
    addSampleData()
    assert len(getAll("SELECT * FROM user_profile")) >= 100


def test_seed_2_atLeast100Accounts():
    addSampleData()
    assert len(getAll("SELECT * FROM user_account")) >= 100


def test_seed_3_profileNames_uniqueAndRightLength():
    # same rules as US3 - 3-50 chars and no repeats (capitals don't matter)
    addSampleData()
    names = [row["profileName"] for row in getAll("SELECT profileName FROM user_profile")]
    assert len(set(n.lower() for n in names)) == len(names)
    for name in names:
        assert 3 <= len(name) <= 50


def test_seed_4_permissions_areFromTheFixedList():
    addSampleData()
    for row in getAll("SELECT permissions FROM user_profile"):
        permissions = json.loads(row["permissions"])
        assert len(permissions) >= 1             # every profile needs at least one (US3 rule)
        for permission in permissions:
            assert permission in ALL_PERMISSIONS


def test_seed_5_passwords_areHashed():
    addSampleData()
    for row in getAll("SELECT password FROM user_account"):
        assert row["password"] != SAMPLE_PASSWORD
        assert len(row["password"]) == 64        # sha256 hash is always 64 characters


def test_seed_6_everyAccount_hasARealProfile():
    addSampleData()
    orphans = getAll("SELECT * FROM user_account WHERE profileId NOT IN (SELECT profileId FROM user_profile)")
    assert orphans == []


def test_seed_7_status_onlyActiveOrSuspended():
    addSampleData()
    for table in ["user_profile", "user_account"]:
        for row in getAll("SELECT status FROM " + table):
            assert row["status"] in ("Active", "Suspended")


def test_seed_8_someAreSuspended():
    # need a few suspended ones so we can demo US1 / US6 / US7 properly
    addSampleData()
    assert len(getAll("SELECT * FROM user_profile WHERE status = 'Suspended'")) > 0
    assert len(getAll("SELECT * FROM user_account WHERE status = 'Suspended'")) > 0


def test_seed_9_runTwice_noDuplicates():
    addSampleData()
    profilesBefore = len(getAll("SELECT * FROM user_profile"))
    accountsBefore = len(getAll("SELECT * FROM user_account"))
    addSampleData()
    assert len(getAll("SELECT * FROM user_profile")) == profilesBefore
    assert len(getAll("SELECT * FROM user_account")) == accountsBefore


def test_seed_10_sameDataEveryTime():
    # fixed random seed -> everyone in the team gets the exact same data
    assert makeSampleData() == makeSampleData()


def test_seed_11_sampleAccount_canLogIn():
    # pick any active sample account that's in an active profile and check its password works.
    # each role logs in on its own page, so check it with its own profile's permissions
    addSampleData()
    row = getAll("SELECT a.username, p.permissions FROM user_account a JOIN user_profile p ON a.profileId = p.profileId "
                 "WHERE a.status = 'Active' AND p.status = 'Active' AND a.username NOT IN ('admin01', 'cust001')")[0]
    permissions = set(json.loads(row["permissions"]))
    assert UserAccount().verifyCredentials(row["username"], SAMPLE_PASSWORD, permissions) is not None


def test_seed_12_defaultTestData_notChanged():
    # sample data must not mess with the accounts the other tests use
    addSampleData()
    assert LoginController().login("admin01", "Admin@123") is not None
    assert LoginController().login("admin02", "Admin@123") is None
    assert getAll("SELECT profileName FROM user_profile WHERE profileId = 1")[0]["profileName"] == "User Admin"


def test_seed_13_runTwice_idsDontJump():
    # found this while testing - INSERT OR IGNORE still uses up an id for every row it skips,
    # so after running the seed twice the next new profile got id 201 instead of 101
    addSampleData()
    addSampleData()
    from entity.userProfile import UserProfile
    UserProfile().createUserProfile(UserProfile(profileName="Brand New Group", description="", permissions=["Generate reports"]))
    newId = getAll("SELECT profileId FROM user_profile WHERE profileName = 'Brand New Group'")[0]["profileId"]
    assert newId == 101


# ---------- database/seedAnalyticsData.py (demo views + saves for US37/38, US46-48) ----------

def test_seed_14_analyticsData_addsViewsAndSaves_onlyOnce():
    from database.seedCurrentIDPData import seedCurrentIDPData
    from database.seedAnalyticsData import seedAnalyticsData
    addSampleData()                  # sample customers to save IDPs
    seedCurrentIDPData()             # 4 demo IDPs
    views, saves = seedAnalyticsData()
    assert views > 0 and saves > 0
    assert len(getAll("SELECT * FROM idp_view")) == views
    assert len(getAll("SELECT * FROM saved_idp")) == saves
    # nothing in the future, and only customers save
    assert not getAll("SELECT * FROM idp_view WHERE viewedAt > CURRENT_TIMESTAMP")
    assert not getAll("SELECT * FROM saved_idp s JOIN user_account a ON a.userId = s.customerId "
                      "JOIN user_profile p ON p.profileId = a.profileId WHERE p.profileName <> 'Customer'")
    # running it again adds nothing
    assert seedAnalyticsData() == (0, 0)


def test_seed_15_analyticsData_rerunAddsNothing_inReadmeOrder():
    # the README order makes 8 IDPs, so some IDP can get 0 views on the first run -
    # a re-run still mustn't add any views or saves
    from database.seedCompanyData import seedCompanyData
    from database.seedIDPCategoryData import seedIDPCategoryData
    from database.seedCurrentIDPData import seedCurrentIDPData
    from database.seedAnalyticsData import seedAnalyticsData
    addSampleData()
    seedCompanyData()
    seedIDPCategoryData()
    seedCurrentIDPData()
    seedAnalyticsData()
    viewCount = len(getAll("SELECT * FROM idp_view"))
    saveCount = len(getAll("SELECT * FROM saved_idp"))
    assert seedAnalyticsData() == (0, 0)
    assert len(getAll("SELECT * FROM idp_view")) == viewCount
    assert len(getAll("SELECT * FROM saved_idp")) == saveCount
