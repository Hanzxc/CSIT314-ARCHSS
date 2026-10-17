# Entity: UserAccount (used by US1 Log in, shown in US6)
# One row in the user_account table. Every account belongs to one UserProfile.

import hashlib

from database.db import getConnection


def hashPassword(password):
    # helper - passwords are only ever stored as a hash, never plain text
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class UserAccount:
    def __init__(self, userId=None, username="", password="", fullName="",
                 email="", phone="", profileId=None, status="Active", createdDate=None):
        self.userId = userId
        self.username = username
        self.password = password        # this is the HASH, not the real password
        self.fullName = fullName
        self.email = email
        self.phone = phone
        self.profileId = profileId
        self.status = status            # "Active" or "Suspended"
        self.createdDate = createdDate

    # US1 - UT1.1 to UT1.4
    def verifyCredentials(self, username, password):
        # TODO:
        # - hash the typed password with hashPassword()
        # - look for a row in user_account with this username AND that hash
        # - found -> return a UserAccount filled in from the row
        # - not found (or empty username/password) -> return None, don't throw an error
        pass

    # US1 - UT1.5
    def isActive(self):
        # TODO: return True if self.status == "Active", else False
        pass
