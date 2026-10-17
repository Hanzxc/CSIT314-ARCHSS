# Test data - the 4 default user profiles and the accounts from our test cases
# run with:  python -m database.seedData
# (safe to run more than once - rows that already exist are skipped)
# TODO: add ~100 records per table for the demo (project spec)

import json

from database.db import getConnection, initDatabase
from entity.userAccount import hashPassword

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


def seedDefaultData(conn):
    for profileName, description, permissions in DEFAULT_PROFILES:
        conn.execute(
            "INSERT OR IGNORE INTO user_profile (profileName, description, permissions, status) "
            "VALUES (?, ?, ?, 'Active')",
            (profileName, description, json.dumps(permissions)),
        )
    for username, password, fullName, email, phone, profileId, status in TEST_ACCOUNTS:
        conn.execute(
            "INSERT OR IGNORE INTO user_account (username, password, fullName, email, phone, profileId, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (username, hashPassword(password), fullName, email, phone, profileId, status),
        )
    conn.commit()


if __name__ == "__main__":
    initDatabase()
    conn = getConnection()
    seedDefaultData(conn)
    conn.close()
    print("Test data added. Log in with admin01 / Admin@123")
