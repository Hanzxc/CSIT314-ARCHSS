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
        # returns the matching UserAccount, or None if the username/password is wrong
        if not username or not password:
            return None

        conn = getConnection()
        row = conn.execute(
            "SELECT * FROM user_account WHERE username = ? AND password = ?",
            (username, hashPassword(password)),
        ).fetchone()
        conn.close()

        if row is None:
            return None
        return UserAccount(row["userId"], row["username"], row["password"], row["fullName"],
                           row["email"], row["phone"], row["profileId"], row["status"],
                           row["createdDate"])

    # US1 - UT1.5
    def isActive(self):
        return self.status == "Active"
