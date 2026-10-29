# Entity: IDP - interior design project (used by US20, US42)
# A designer's project shown to customers. Current = still in progress, Past = completed.
# One row in the idp table.

import sqlite3

from database.db import getConnection


class IDP:
    def __init__(self, idpId=None, designerId=None, categoryId=None, title="", description="",
                 location="", projectType="Current", status="Active", createdDate=None):
        self.idpId = idpId
        self.designerId = designerId      # the owner's userId
        self.categoryId = categoryId
        self.title = title
        self.description = description
        self.location = location
        self.projectType = projectType    # "Current" or "Past"
        self.status = status              # "Active" or "Suspended"
        self.createdDate = createdDate

    # US20 - UT20.1. Ownership always comes from the caller (the session), never the form.
    def addCurrentIDP(self, designerId, idpData):
        conn = getConnection()
        try:
            # the category must still be Active at the moment of saving (US44)
            cursor = conn.execute(
                "INSERT INTO idp (designerId, categoryId, title, description, location, projectType) "
                "SELECT ?, categoryId, ?, ?, ?, 'Current' FROM idp_category "
                "WHERE categoryId = ? AND status = 'Active' "
                "AND EXISTS (SELECT 1 FROM user_account WHERE userId = ?)",
                (designerId, idpData.get("title", "").strip(), idpData.get("description", "").strip(),
                 idpData.get("location", "").strip(), idpData.get("categoryId"), designerId))
            conn.commit()
            added = cursor.rowcount == 1
        except sqlite3.IntegrityError:
            conn.rollback()
            added = False
        finally:
            conn.close()
        return added

    # US42 - UT42.3, UT42.4: every active IDP grouped under one category, newest first
    def getIDPsInCategory(self, categoryId):
        conn = getConnection()
        rows = conn.execute(
            "SELECT * FROM idp WHERE categoryId = ? AND status = 'Active' ORDER BY idpId DESC",
            (categoryId,)).fetchall()
        conn.close()
        return [IDP(**dict(row)) for row in rows]
