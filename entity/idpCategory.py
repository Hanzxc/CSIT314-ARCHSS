# Entity: IDPCategory (used by US20, US41, US42, US43, US44, US45)
# A group of similar interior design projects e.g. Living Room, Kitchen.
# One row in the idp_category table.

from database.db import getConnection
from entity.idp import IDP


class IDPCategory:
    # UC41 - UC45
    # one IDP category, new ones start as Active
    def __init__(self, categoryId=None, categoryName="", description="", status="Active",
                 createdDate=None):
        self.categoryId = categoryId
        self.categoryName = categoryName
        self.description = description
        self.status = status            # "Active" or "Suspended"
        self.createdDate = createdDate

    # UC42 View IDP category, UC43 Update IDP category
    # returns the IDPCategory with this id, or None if there isn't one
    def getIDPCategory(self, categoryId):
        conn = getConnection()
        row = conn.execute("SELECT * FROM idp_category WHERE categoryId = ?", (categoryId,)).fetchone()
        conn.close()

        if row is None:
            return None
        return IDPCategory(**dict(row))

    # UC20 Add current IDP, UC44 Suspend IDP category
    # only Active categories can be chosen for new IDPs
    def isActive(self):
        return self.status == "Active"

    # UC41 Create IDP category, UC43 Update IDP category
    # the duplicate check - LOWER() on both sides so "kITCHEN" still counts as "Kitchen".
    # US43 passes its own categoryId so a category doesn't clash with its own name
    def isCategoryNameTaken(self, categoryName, categoryId=None):
        sql = "SELECT categoryId FROM idp_category WHERE LOWER(categoryName) = LOWER(?)"
        params = [categoryName]
        if categoryId is not None:
            sql += " AND categoryId != ?"
            params.append(categoryId)

        conn = getConnection()
        row = conn.execute(sql, params).fetchone()
        conn.close()
        return row is not None

    # UC41 Create IDP category
    # the page has already checked the input - the entity checks for a duplicate name,
    # then saves the category as Active
    def createIDPCategory(self, idpCategory):
        if self.isCategoryNameTaken(idpCategory.categoryName):
            return False

        conn = getConnection()
        conn.execute("INSERT INTO idp_category (categoryName, description, status) VALUES (?, ?, 'Active')",
                     (idpCategory.categoryName, idpCategory.description))
        conn.commit()
        conn.close()
        return True

    # UC43 Update IDP category
    # only an Active category can be updated, and only the name and description change -
    # the status is never touched. False if the name is taken, the category is suspended
    # or it doesn't exist
    def updateIDPCategory(self, idpCategory):
        if self.isCategoryNameTaken(idpCategory.categoryName, idpCategory.categoryId):
            return False

        conn = getConnection()
        cursor = conn.execute("UPDATE idp_category SET categoryName = ?, description = ? "
                              "WHERE categoryId = ? AND status = 'Active'",
                              (idpCategory.categoryName, idpCategory.description, idpCategory.categoryId))
        conn.commit()
        updated = cursor.rowcount == 1
        conn.close()
        return updated

    # UC44 Suspend IDP category
    # only an Active row changes, so a missing or already suspended category gives False.
    # the IDPs in the category are kept as they are
    def suspendIDPCategory(self, categoryId):
        conn = getConnection()
        cursor = conn.execute(
            "UPDATE idp_category SET status = 'Suspended' WHERE categoryId = ? AND status = 'Active'",
            (categoryId,))
        conn.commit()
        suspended = cursor.rowcount == 1
        conn.close()
        return suspended

    # UC45 Search IDP categories
    # looks in the name and the description, capitals don't matter.
    # empty keyword -> "%%" which matches everything (alt flow 1a).
    # suspended ones are NOT filtered out, the manager still needs to find them
    def searchIDPCategories(self, keyword):
        pattern = "%" + keyword.lower() + "%"

        conn = getConnection()
        rows = conn.execute(
            "SELECT * FROM idp_category "
            "WHERE LOWER(categoryName) LIKE ? OR LOWER(description) LIKE ? "
            "ORDER BY categoryId",
            (pattern, pattern),
        ).fetchall()
        conn.close()
        return [IDPCategory(**dict(row)) for row in rows]

    # UC42 View IDP category
    # the active IDPs grouped under this category, newest first
    def getIDPsInCategory(self, categoryId):
        conn = getConnection()
        rows = conn.execute(
            "SELECT * FROM idp WHERE categoryId = ? AND status = 'Active' ORDER BY idpId DESC",
            (categoryId,)).fetchall()
        conn.close()
        return [IDP(**dict(row)) for row in rows]


    def getActiveIDPCategories(self):
        conn = getConnection()
        try:
            rows = conn.execute("SELECT * FROM idp_category WHERE status='Active' ORDER BY categoryName").fetchall()
            return [IDPCategory(**dict(row)) for row in rows]
        finally:
            conn.close()
