# Entity: UserAccount (used by US1 Log in, US8 - US12)
# One row in the user_account table. Every account belongs to one UserProfile.

import hashlib
from datetime import datetime

from database.db import getConnection
from entity.userProfile import UserProfile


def hashPassword(password):
    # helper - passwords are only ever stored as a hash, never plain text
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def rowToAccount(row):
    # helper - turns a database row into a UserAccount (saves typing it out every time)
    return UserAccount(row["userId"], row["username"], row["password"], row["fullName"],
                       row["email"], row["phone"], row["profileId"], row["status"],
                       row["createdDate"])


class UserAccount:
    # used by UC1, UC8 - UC13, UC39
    # one user account = one row in the user_account table
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
        return rowToAccount(row)

    # US1 - UT1.5, US11 - UT11.5
    def isActive(self):
        return self.status == "Active"

    # US9, US10, US11 - UT9.5
    def getUserAccount(self, userId):
        # returns the UserAccount with this id, or None if there isn't one
        conn = getConnection()
        row = conn.execute("SELECT * FROM user_account WHERE userId = ?", (userId,)).fetchone()
        conn.close()

        if row is None:
            return None
        return rowToAccount(row)

    # US8 calls it with just the username, US10 also passes its own userId
    # UT8.5, UT8.6, UT10.5, UT10.6
    def isUsernameTaken(self, username, userId=None):
        # capitals don't matter, so you can't have "admin01" and "Admin01" as 2 different people
        sql = "SELECT userId FROM user_account WHERE LOWER(username) = LOWER(?)"
        params = [username]

        # for US10 - skip the account being edited, otherwise keeping its own name fails
        if userId is not None:
            sql += " AND userId != ?"
            params.append(userId)

        conn = getConnection()
        row = conn.execute(sql, params).fetchone()
        conn.close()
        return row is not None

    # US8 - UT8.8
    def createUserAccount(self, username, password, fullName, email, phone, profileId):
        # the page already checked + tidied the input, this only checks for duplicates:
        # the group has to exist and be active, and the username can't be taken
        profile = UserProfile().getUserProfile(profileId)
        if profile is None or not profile.isActive() or self.isUsernameTaken(username):
            return False

        # no duplicate -> save it. new accounts always start as Active
        createdDate = datetime.now().strftime("%Y-%m-%d %H:%M:%S")     # same format as the seed data
        conn = getConnection()
        conn.execute(
            "INSERT INTO user_account "
            "(username, password, fullName, email, phone, profileId, status, createdDate) "
            "VALUES (?, ?, ?, ?, ?, ?, 'Active', ?)",
            (username, hashPassword(password), fullName, email, phone, profileId, createdDate),
        )
        conn.commit()
        conn.close()
        return True

    # US10 - UT10.8
    def updateUserAccount(self, userId, username, fullName, email, phone, profileId):
        # same duplicate checks as create, but its OWN username is fine (pass userId in)
        profile = UserProfile().getUserProfile(profileId)
        if profile is None or not profile.isActive() or self.isUsernameTaken(username, userId):
            return False

        # password, status and createdDate are left alone on purpose (US10 assumptions)
        conn = getConnection()
        cursor = conn.execute(
            "UPDATE user_account SET username = ?, fullName = ?, email = ?, phone = ?, profileId = ? "
            "WHERE userId = ?",
            (username, fullName, email, phone, profileId, userId),
        )
        conn.commit()
        conn.close()
        return cursor.rowcount > 0      # 0 rows means that id doesn't exist

    # US11 - UT11.7
    def suspendUserAccount(self, userId):
        # just flips the status, nothing gets deleted. login (US1) checks isActive() so they're blocked.
        # only an Active one can be suspended - already suspended or no such id -> 0 rows -> False
        conn = getConnection()
        cursor = conn.execute(
            "UPDATE user_account SET status = 'Suspended' WHERE userId = ? AND status = 'Active'",
            (userId,))
        conn.commit()
        conn.close()
        return cursor.rowcount > 0

    # US12 - UT12.7
    def searchUserAccounts(self, keyword):
        # looks in username, full name and email, capitals don't matter.
        # empty keyword -> "%%" which matches everything (alt flow 1a)
        # suspended accounts are NOT filtered out, the admin might still need them
        pattern = "%" + keyword.lower() + "%"

        conn = getConnection()
        rows = conn.execute(
            "SELECT * FROM user_account "
            "WHERE LOWER(username) LIKE ? OR LOWER(fullName) LIKE ? OR LOWER(email) LIKE ? "
            "ORDER BY userId",
            (pattern, pattern, pattern),
        ).fetchall()
        conn.close()

        accounts = []
        for row in rows:
            accounts.append(rowToAccount(row))
        return accounts
