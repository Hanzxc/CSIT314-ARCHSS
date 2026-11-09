# Entity: UserProfile (used by US3 - US10, US13, US30, US39)
# A user group e.g. User Admin, Interior Designer, Customer, Platform Manager.
# One row in the user_profile table.

import json

from database.db import getConnection

# the platform's fixed permission list (US3 assumptions) - don't rename these
ALL_PERMISSIONS = [
    "Manage user accounts",
    "Manage user profiles",
    "Manage company profile",
    "Manage own IDPs",
    "View IDP statistics",
    "Search, view and save IDPs",
    "Manage IDP categories",
    "Generate reports",
]


class UserProfile:
    # used by UC1, UC3 - UC13, UC39
    # one user profile (group) = one row in the user_profile table
    def __init__(self, profileId=None, profileName="", description="",
                 permissions=None, status="Active"):
        self.profileId = profileId
        self.profileName = profileName
        self.description = description
        self.permissions = permissions if permissions is not None else []   # list of strings
        self.status = status            # "Active" or "Suspended"

    # US4, US5, US6, US8, US9, US10 - UT4.1 to UT4.4
    def getUserProfile(self, profileId):
        # returns the UserProfile with this id, or None if there isn't one
        conn = getConnection()
        row = conn.execute("SELECT * FROM user_profile WHERE profileId = ?", (profileId,)).fetchone()
        conn.close()

        if row is None:
            return None

        # Safely parse JSON permissions with fallback
        raw_perms = row["permissions"] if hasattr(row, "keys") else row[3]
        try:
            permissions = json.loads(raw_perms) if raw_perms else []
        except (json.JSONDecodeError, TypeError):
            permissions = [raw_perms] if raw_perms else []

        return UserProfile(row["profileId"], row["profileName"], row["description"],
                           permissions, row["status"])

    # US6, US8, US10 - UT6.5
    def isActive(self):
        return self.status == "Active"

    # US3, US5 - UT3.1
    def getAllPermissions(self):
        # give back a copy so nobody accidentally changes the real list
        return list(ALL_PERMISSIONS)

    # US3 calls it with just the name, US5 also passes its own profileId
    # UT3.2 to UT3.4, UT5.1, UT5.2
    def isProfileNameTaken(self, profileName, profileId=None):
        # LOWER() on both sides so "cUSTOMER" still counts as "Customer"
        sql = "SELECT profileId FROM user_profile WHERE LOWER(profileName) = LOWER(?)"
        params = [profileName]

        # for US5 - skip the profile being edited, otherwise it clashes with its own name
        if profileId is not None:
            sql += " AND profileId != ?"
            params.append(profileId)

        conn = getConnection()
        row = conn.execute(sql, params).fetchone()
        conn.close()
        return row is not None

    # US3 - UT3.5, UT3.6
    def createUserProfile(self, profile):
        # the page already checked + tidied the input, this only checks for a duplicate name
        if self.isProfileNameTaken(profile.profileName):
            return False

        # no duplicate -> save it. new profiles always start as Active
        conn = getConnection()
        conn.execute(
            "INSERT INTO user_profile (profileName, description, permissions, status) "
            "VALUES (?, ?, ?, 'Active')",
            (profile.profileName, profile.description, json.dumps(profile.permissions)),
        )
        conn.commit()
        conn.close()
        return True

    # US5 - UT5.3 to UT5.5, UT5.8
    def updateUserProfile(self, profile):
        # pass profileId in so it doesn't count its OWN name as taken
        if self.isProfileNameTaken(profile.profileName, profile.profileId):
            return False

        # only an Active profile is changed - suspended or no such id -> 0 rows -> False.
        # the status itself is never changed here (US6 does that)
        conn = getConnection()
        cursor = conn.execute(
            "UPDATE user_profile SET profileName = ?, description = ?, permissions = ? "
            "WHERE profileId = ? AND status = 'Active'",
            (profile.profileName, profile.description, json.dumps(profile.permissions), profile.profileId),
        )
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    # US6 - UT6.7
    def suspendUserProfile(self, profileId):
        # only the profile row changes, the accounts in it stay where they are.
        # login (US1 verifyCredentials) already checks the profile status so they get blocked anyway.
        # only an Active one can be suspended - already suspended or no such id -> 0 rows -> False
        conn = getConnection()
        cursor = conn.execute(
            "UPDATE user_profile SET status = 'Suspended' WHERE profileId = ? AND status = 'Active'",
            (profileId,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    # US7 - UT7.1 to UT7.8
    def searchUserProfiles(self, keyword):
        # looks in the name and the description, capitals don't matter.
        # empty keyword -> "%%" which matches everything, so that's alt flow 1a sorted
        # suspended ones are NOT filtered out, the admin might still need them
        pattern = "%" + keyword.lower() + "%"

        conn = getConnection()
        rows = conn.execute(
            "SELECT * FROM user_profile "
            "WHERE LOWER(profileName) LIKE ? OR LOWER(description) LIKE ? "
            "ORDER BY profileId",
            (pattern, pattern),
        ).fetchall()
        conn.close()

        profiles = []
        for row in rows:
            profiles.append(UserProfile(row["profileId"], row["profileName"], row["description"],
                                        json.loads(row["permissions"]), row["status"]))
        return profiles
