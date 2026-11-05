# Entity: savedIDP - Customer saved list / favourites (used by US33, US34, US35)
# Tracks which customer accounts have bookmarked which interior design projects.

from database.db import getConnection


class SavedIDP:
    def __init__(self, savedId=None, customerId=None, idpId=None, savedDate=None):
        self.savedId = savedId
        self.customerId = customerId    # the logged-in customer's userId
        self.idpId = idpId              # the bookmarked project id
        self.savedDate = savedDate

    # UC33 Helper: Check if an IDP is already saved by customer
    def isSaved(self, customerId, idpId):
        conn = getConnection()
        cursor = conn.execute(
            "SELECT 1 FROM saved_idp WHERE customerId = ? AND idpId = ?",
            (customerId, idpId)
        )
        row = cursor.fetchone()
        conn.close()
        return row is not None

    # UC33 Save / Unsave IDP (Toggle action)
    def toggleSaveIDP(self, customerId, idpId):
        conn = getConnection()
        if self.isSaved(customerId, idpId):
            # Remove from saved list
            conn.execute(
                "DELETE FROM saved_idp WHERE customerId = ? AND idpId = ?",
                (customerId, idpId)
            )
            conn.commit()
            conn.close()
            return False  # Status: Unsaved
        else:
            # Add to saved list
            conn.execute(
                "INSERT INTO saved_idp (customerId, idpId, savedDate) "
                "VALUES (?, ?, DATETIME('now'))",
                (customerId, idpId)
            )
            conn.commit()
            conn.close()
            return True  # Status: Saved

    # UC35 View Saved List
    def getSavedListByCustomer(self, customerId):
        conn = getConnection()
        cursor = conn.execute(
            "SELECT s.*, i.title, i.description, i.location, i.projectType, c.categoryName, u.fullName as designerName "
            "FROM saved_idp s "
            "JOIN idp i ON s.idpId = i.idpId "
            "LEFT JOIN idp_category c ON i.categoryId = c.categoryId "
            "LEFT JOIN user_account u ON i.designerId = u.userId "
            "WHERE s.customerId = ? AND i.status = 'Active' "
            "ORDER BY s.savedDate DESC",
            (customerId,)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    # UC34 Search Saved List
    def searchSavedList(self, customerId, keyword):
        conn = getConnection()
        search_kw = f"%{keyword}%"
        cursor = conn.execute(
            "SELECT s.*, i.title, i.description, i.location, i.projectType, c.categoryName, u.fullName as designerName "
            "FROM saved_idp s "
            "JOIN idp i ON s.idpId = i.idpId "
            "LEFT JOIN idp_category c ON i.categoryId = c.categoryId "
            "LEFT JOIN user_account u ON i.designerId = u.userId "
            "WHERE s.customerId = ? AND i.status = 'Active' "
            "AND (i.title LIKE ? OR i.description LIKE ? OR c.categoryName LIKE ? OR u.fullName LIKE ?) "
            "ORDER BY s.savedDate DESC",
            (customerId, search_kw, search_kw, search_kw, search_kw)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows