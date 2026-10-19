# Test data - the 4 default user profiles and the accounts from our test cases,
# plus ~100 sample records per table for the demo (project spec)
# run with:  python -m database.seedData
# (safe to run more than once - rows that already exist are skipped)

import json
import random
from datetime import date, timedelta

from database.db import getConnection, initDatabase
from entity.userAccount import hashPassword
from entity.userProfile import ALL_PERMISSIONS

# profileId 1-4
DEFAULT_PROFILES = [
    ("User Admin", "Manages user accounts and profiles",
     ["Manage user accounts", "Manage user profiles"]),
    ("Interior Designer", "Designers who show their company and IDPs",
     ["Manage company profile", "Manage own IDPs", "View IDP statistics"]),
    ("Customer", "Home owners who are renovating",
     ["Search, view and save IDPs"]),
    ("Platform Manager", "Manages IDP categories and reports",
     ["Manage IDP categories", "Generate reports"]),
]

# username, password, fullName, email, phone, profileId, status
TEST_ACCOUNTS = [
    ("admin01", "Admin@123", "Alice Tan", "admin01@archss.com", "91234567", 1, "Active"),
    ("admin02", "Admin@123", "Ben Lim", "admin02@archss.com", "92345678", 1, "Suspended"),
    ("cust001", "Cust@123", "Chloe Ng", "cust001@archss.com", "93456789", 3, "Active"),
]

# only insert a row if it isn't there already. we used INSERT OR IGNORE before, but sqlite
# still uses up an id for every row it skips, so every re-run left a gap in the ids
# (e.g. the next profile made in the app got id 201 instead of 101)
PROFILE_NOT_THERE_YET = "WHERE NOT EXISTS (SELECT 1 FROM user_profile WHERE profileName = ?)"
ACCOUNT_NOT_THERE_YET = "WHERE NOT EXISTS (SELECT 1 FROM user_account WHERE username = ?)"


def seedDefaultData(conn):
    for profileName, description, permissions in DEFAULT_PROFILES:
        conn.execute(
            "INSERT INTO user_profile (profileName, description, permissions, status) "
            "SELECT ?, ?, ?, 'Active' " + PROFILE_NOT_THERE_YET,
            (profileName, description, json.dumps(permissions), profileName),
        )
    for username, password, fullName, email, phone, profileId, status in TEST_ACCOUNTS:
        conn.execute(
            "INSERT INTO user_account (username, password, fullName, email, phone, profileId, status) "
            "SELECT ?, ?, ?, ?, ?, ?, ? " + ACCOUNT_NOT_THERE_YET,
            (username, hashPassword(password), fullName, email, phone, profileId, status, username),
        )
    conn.commit()


# ==============================================================
# Sample data for the demo - 96 more profiles + 97 more accounts,
# so with the defaults above that's 100 per table
# ==============================================================

SAMPLE_SEED = 314                  # fixed seed so everyone gets the exact same "random" data
SAMPLE_PASSWORD = "Pass@123"       # every sample account uses this, makes the demo easier
SUSPENDED_COUNT = 10               # how many sample profiles / accounts start off Suspended

# each kind of user only gets the permissions that make sense for them
FAMILY_PERMISSIONS = {
    "admin": ["Manage user accounts", "Manage user profiles"],
    "designer": ["Manage company profile", "Manage own IDPs", "View IDP statistics"],
    "customer": ["Search, view and save IDPs"],
    "manager": ["Manage IDP categories", "Generate reports"],
}

# which default profile is the "main" one for each family
FAMILY_DEFAULT_PROFILE = {
    "admin": "User Admin",
    "designer": "Interior Designer",
    "customer": "Customer",
    "manager": "Platform Manager",
}

DESIGNER_LEVELS = ["Junior", "Senior", "Lead", "Freelance"]
DESIGNER_STYLES = ["Kitchen", "Bathroom", "Bedroom", "Living Room", "Home Office", "Retail Space",
                   "Restaurant", "Hotel", "Minimalist", "Scandinavian", "Industrial", "Japandi"]

CUSTOMER_TYPES = ["HDB Owner", "Condo Owner", "Landed Home Owner", "First-time Home Buyer", "Tenant",
                  "Landlord", "Small Business", "Office Tenant", "Shop Owner", "Restaurant Owner",
                  "Premium", "Trial", "Overseas", "Corporate", "Student", "Retiree", "Young Couple",
                  "Family", "Investor", "Renovation Contractor"]

MANAGER_ROLES = ["IDP Category Manager", "Reports Manager", "Content Reviewer", "Quality Checker",
                 "Data Analyst", "Marketing Analyst", "Regional Manager North", "Regional Manager South",
                 "Regional Manager East", "Regional Manager West", "Regional Manager Central",
                 "Trends Analyst", "Partnerships Manager", "Operations Manager", "Finance Reporter",
                 "Audit Reviewer"]

ADMIN_ROLES = ["Support Admin", "Helpdesk Admin", "Account Reviewer", "Onboarding Admin",
               "Security Admin", "Junior User Admin", "Senior User Admin", "Profile Auditor",
               "Customer Service Admin", "Night Shift Admin", "Weekend Admin", "Backup User Admin"]

FIRST_NAMES = ["Aaron", "Aisha", "Bryan", "Cheryl", "Daniel", "Deepa", "Ethan", "Farah", "Gabriel",
               "Grace", "Hafiz", "Hui Min", "Isaac", "Jasmine", "Jun Wei", "Kavitha", "Kelvin", "Li Ting",
               "Marcus", "Mei Ling", "Nicholas", "Nur Aini", "Priya", "Rachel", "Rajesh", "Samuel",
               "Siti", "Terence", "Valerie", "Wei Jie", "Xin Yi", "Zachary"]
LAST_NAMES = ["Tan", "Lim", "Lee", "Ng", "Ong", "Wong", "Goh", "Chua", "Koh", "Teo", "Chan", "Yeo",
              "Ho", "Low", "Sim", "Kumar", "Pillai", "Rahman", "Ismail", "Hassan", "Fernandez", "Wee"]

# how many sample accounts of each kind (adds up to 97)
# username prefix, family, how many, number to start from (cust001 / admin01-02 are already taken)
ACCOUNT_GROUPS = [
    ("cust", "customer", 40, 2, 3),       # cust002 ...
    ("design", "designer", 35, 1, 3),     # design001 ...
    ("pm", "manager", 12, 1, 3),          # pm001 ...
    ("admin", "admin", 10, 3, 2),         # admin03 ... (2 digits to match admin01)
]


def pickPermissions(rng, family):
    # random 1+ permissions from the family's list, kept in the same order as ALL_PERMISSIONS
    pool = FAMILY_PERMISSIONS[family]
    chosen = rng.sample(pool, rng.randint(1, len(pool)))
    return [p for p in ALL_PERMISSIONS if p in chosen]


def makeSampleProfiles(rng):
    # every name is made up from the lists above so they're all different (and 3-50 chars)
    profiles = []   # (profileName, description, permissions, status, family)

    for level in DESIGNER_LEVELS:
        for style in DESIGNER_STYLES:
            profiles.append((level + " " + style + " Designer",
                             level + " designers who specialise in " + style.lower() + " interiors",
                             pickPermissions(rng, "designer"), "Active", "designer"))

    for customerType in CUSTOMER_TYPES:
        profiles.append((customerType + " Customer",
                         customerType + " users looking for renovation ideas",
                         pickPermissions(rng, "customer"), "Active", "customer"))

    for role in MANAGER_ROLES:
        profiles.append((role, "Platform staff - " + role.lower(),
                         pickPermissions(rng, "manager"), "Active", "manager"))

    for role in ADMIN_ROLES:
        profiles.append((role, "Admin staff - " + role.lower(),
                         pickPermissions(rng, "admin"), "Active", "admin"))

    # description is optional (US3) so leave a few of them empty
    for i in rng.sample(range(len(profiles)), 5):
        name, _, permissions, status, family = profiles[i]
        profiles[i] = (name, "", permissions, status, family)

    # and suspend a few, so there's something to show for US6 / US7
    for i in rng.sample(range(len(profiles)), SUSPENDED_COUNT):
        name, description, permissions, _, family = profiles[i]
        profiles[i] = (name, description, permissions, "Suspended", family)

    return profiles


def makeSampleAccounts(rng, profiles):
    # sample profile names grouped by family, so an account goes into a profile that fits it
    namesByFamily = {}
    for name, _, _, _, family in profiles:
        namesByFamily.setdefault(family, []).append(name)

    accounts = []   # (username, fullName, email, phone, profileName, status, createdDate)
    for prefix, family, howMany, startFrom, digits in ACCOUNT_GROUPS:
        for n in range(startFrom, startFrom + howMany):
            username = prefix + str(n).zfill(digits)
            fullName = rng.choice(FIRST_NAMES) + " " + rng.choice(LAST_NAMES)
            phone = rng.choice("89") + str(rng.randint(0, 9999999)).zfill(7)   # SG mobile, 8 digits

            # about half go in the main default profile, the rest in one of the sample ones
            if rng.random() < 0.5:
                profileName = FAMILY_DEFAULT_PROFILE[family]
            else:
                profileName = rng.choice(namesByFamily[family])

            # joined some time this year
            createdDate = (date(2026, 1, 1) + timedelta(days=rng.randint(0, 270))).isoformat() + " 09:00:00"

            accounts.append((username, fullName, username + "@archss.com", phone,
                             profileName, "Active", createdDate))

    for i in rng.sample(range(len(accounts)), SUSPENDED_COUNT):
        account = list(accounts[i])
        account[5] = "Suspended"
        accounts[i] = tuple(account)

    return accounts


def makeSampleData():
    # builds the lists only, doesn't touch the database (so it's easy to test)
    rng = random.Random(SAMPLE_SEED)
    profiles = makeSampleProfiles(rng)
    accounts = makeSampleAccounts(rng, profiles)
    return profiles, accounts


def seedSampleData(conn):
    profiles, accounts = makeSampleData()

    for profileName, description, permissions, status, _ in profiles:
        conn.execute(
            "INSERT INTO user_profile (profileName, description, permissions, status) "
            "SELECT ?, ?, ?, ? " + PROFILE_NOT_THERE_YET,
            (profileName, description, json.dumps(permissions), status, profileName),
        )

    # look the profileId up by name instead of guessing it, in case someone already
    # made extra profiles in their own database and the ids are shifted
    passwordHash = hashPassword(SAMPLE_PASSWORD)
    for username, fullName, email, phone, profileName, status, createdDate in accounts:
        row = conn.execute("SELECT profileId FROM user_profile WHERE profileName = ?",
                           (profileName,)).fetchone()
        conn.execute(
            "INSERT INTO user_account "
            "(username, password, fullName, email, phone, profileId, status, createdDate) "
            "SELECT ?, ?, ?, ?, ?, ?, ?, ? " + ACCOUNT_NOT_THERE_YET,
            (username, passwordHash, fullName, email, phone, row["profileId"], status, createdDate, username),
        )
    conn.commit()


if __name__ == "__main__":
    initDatabase()
    conn = getConnection()
    seedDefaultData(conn)
    seedSampleData(conn)
    profileCount = conn.execute("SELECT COUNT(*) FROM user_profile").fetchone()[0]
    accountCount = conn.execute("SELECT COUNT(*) FROM user_account").fetchone()[0]
    conn.close()
    print("Test data added -", profileCount, "user profiles,", accountCount, "user accounts")
    print("Log in with admin01 / Admin@123  (sample accounts use " + SAMPLE_PASSWORD + ")")
