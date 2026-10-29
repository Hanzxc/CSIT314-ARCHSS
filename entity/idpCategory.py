# Entity: IDPCategory (used by US20, US41, US42, US43, US44, US45)
# A group of similar interior design projects e.g. Living Room, Kitchen.
# One row in the idp_category table.

import sqlite3

from database.db import getConnection


class IDPCategory:
    def __init__(self, categoryId=None, categoryName="", description="", status="Active",
                 createdDate=None):
        self.categoryId = categoryId
        self.categoryName = categoryName
        self.description = description
        self.status = status            # "Active" or "Suspended"
        self.createdDate = createdDate

    # US20, US42, US43, US44 - UT42.1, UT42.2
    def getIDPCategory(self, categoryId):
        # returns the IDPCategory with this id, or None if there isn't one
        conn = getConnection()
        row = conn.execute("SELECT * FROM idp_category WHERE categoryId = ?", (categoryId,)).fetchone()
        conn.close()

        if row is None:
            return None
        return IDPCategory(**dict(row))

    # US20, US44 - UT44.5
    def isActive(self):
        return self.status == "Active"

    # US41 calls it with just the name, US43 also passes its own categoryId
    # UT41.2 to UT41.4, UT43.1, UT43.2
    def isCategoryNameTaken(self, categoryName, categoryId=None):
        # LOWER() on both sides so "kITCHEN" still counts as "Kitchen"
        sql = "SELECT categoryId FROM idp_category WHERE LOWER(categoryName) = LOWER(?)"
        params = [categoryName.strip()]

        # for US43 - skip the category being edited, otherwise it clashes with its own name
        if categoryId is not None:
            sql += " AND categoryId != ?"
            params.append(categoryId)

        conn = getConnection()
        row = conn.execute(sql, params).fetchone()
        conn.close()
        return row is not None

    # US41
    def createIDPCategory(self, categoryName, description):
        # new categories always start as Active
        conn = getConnection()
        try:
            conn.execute(
                "INSERT INTO idp_category (categoryName, description, status) VALUES (?, ?, 'Active')",
                (categoryName.strip(), description.strip()),
            )
            conn.commit()
            created = True
        except sqlite3.IntegrityError:
            # the UNIQUE on categoryName stopped it (backup in case the name check was skipped)
            created = False
        conn.close()
        return created

    # US43
    def updateIDPCategory(self, categoryId, categoryName, description):
        # status is left alone on purpose - updating shouldn't un-suspend a category (UT43.8)
        conn = getConnection()
        try:
            cursor = conn.execute(
                "UPDATE idp_category SET categoryName = ?, description = ? WHERE categoryId = ?",
                (categoryName.strip(), description.strip(), categoryId),
            )
            conn.commit()
            updated = cursor.rowcount > 0      # 0 rows means that id doesn't exist
        except sqlite3.IntegrityError:
            updated = False
        conn.close()
        return updated

    # US44 - UT44.6
    def suspendIDPCategory(self, categoryId):
        # only an Active row changes; the IDPs in the category are kept as they are
        conn = getConnection()
        cursor = conn.execute(
            "UPDATE idp_category SET status = 'Suspended' WHERE categoryId = ? AND status = 'Active'",
            (categoryId,))
        conn.commit()
        suspended = cursor.rowcount > 0
        conn.close()
        return suspended

    # US45 - UT45.1 to UT45.6
    def searchIDPCategories(self, keyword):
        # looks in the name and the description, capitals don't matter.
        # empty keyword -> "%%" which matches everything (alt flow 1a)
        # suspended ones are NOT filtered out, the manager still needs to find them
        pattern = "%" + keyword.strip().lower() + "%"

        conn = getConnection()
        rows = conn.execute(
            "SELECT * FROM idp_category "
            "WHERE LOWER(categoryName) LIKE ? OR LOWER(description) LIKE ? "
            "ORDER BY categoryId",
            (pattern, pattern),
        ).fetchall()
        conn.close()
        return [IDPCategory(**dict(row)) for row in rows]

    # US20 - the category drop-down only offers categories users can still select (US44)
    def getActiveIDPCategories(self):
        conn = getConnection()
        rows = conn.execute(
            "SELECT * FROM idp_category WHERE status = 'Active' ORDER BY categoryName").fetchall()
        conn.close()
        return [IDPCategory(**dict(row)) for row in rows]
