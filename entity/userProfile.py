# Entity: UserProfile (used by US1, US3, US4, US5, US6)
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
    def __init__(self, profileId=None, profileName="", description="",
                 permissions=None, status="Active"):
        self.profileId = profileId
        self.profileName = profileName
        self.description = description
        self.permissions = permissions if permissions is not None else []   # list of strings
        self.status = status            # "Active" or "Suspended"

    # US1, US4, US5, US6 - UT4.1 to UT4.4
    def getUserProfile(self, profileId):
        # returns the UserProfile with this id, or None if there isn't one
        conn = getConnection()
        row = conn.execute("SELECT * FROM user_profile WHERE profileId = ?", (profileId,)).fetchone()
        conn.close()

        if row is None:
            return None
        return UserProfile(row["profileId"], row["profileName"], row["description"],
                           json.loads(row["permissions"]), row["status"])

    # US1, US6 - UT6.5
    def isActive(self):
        return self.status == "Active"

    # US3, US5 - UT3.1
    def getAllPermissions(self):
        # TODO: return ALL_PERMISSIONS (8 permissions)
        pass

    # US3 calls it with just the name, US5 also passes its own profileId
    # UT3.2 to UT3.4, UT5.1, UT5.2
    def isProfileNameTaken(self, profileName, profileId=None):
        # TODO:
        # - capitals don't matter ("cUSTOMER" == "Customer") -> compare with LOWER()
        # - if profileId is given, ignore that profile (so US5 can keep its own name)
        # - return True if another profile already has this name, else False
        pass

    # US3
    def createUserProfile(self, profileName, description, permissions):
        # TODO:
        # - insert a new row, status is always "Active"
        # - save permissions with json.dumps(permissions)
        # - return True if saved, False if not
        pass

    # US5
    def updateUserProfile(self, profileId, profileName, description, permissions):
        # TODO:
        # - update name, description and permissions of this profileId
        # - never change the status here
        # - return True if a row was updated, False if the id doesn't exist
        pass

    # US6 - UT6.7
    def suspendUserProfile(self, profileId):
        # TODO:
        # - set status = "Suspended" for this profileId
        # - don't touch the user accounts in this profile
        # - return True if a row was updated, else False
        pass
