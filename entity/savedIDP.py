# Entity: SavedIDP - a customer's saved list (used by US33, US34, US35, and read by US38)
# one row in saved_idp = one customer has one IDP in their saved list

from database.db import getConnection
from entity.idp import IDP

# the IDPs in a customer's saved list that customers can still see (Active IDP, Active category)
SAVED_IDPS_SQL = """
    SELECT idp.*, category.categoryName
    FROM saved_idp AS saved
    JOIN idp ON idp.idpId = saved.idpId
    JOIN idp_category AS category ON category.categoryId = idp.categoryId
    WHERE saved.customerId = ? AND idp.status = 'Active' AND category.status = 'Active'
"""


class SavedIDP:
    def __init__(self, savedId=None, customerId=None, idpId=None, savedDate=None):
        self.savedId = savedId
        self.customerId = customerId      # the logged-in customer's userId
        self.idpId = idpId                # the saved project
        self.savedDate = savedDate

    # UC33 Save IDP
    # adds the IDP to the saved list. the entity checks the rest: no duplicate (UNIQUE customerId + idpId),
    # and the IDP must be one customers can see. true if a row was added
    def createSavedRecord(self, customerId, idpId):
        conn = getConnection()
        cursor = conn.execute(
            "INSERT OR IGNORE INTO saved_idp (customerId, idpId) "
            "SELECT ?, idp.idpId FROM idp JOIN idp_category AS category ON category.categoryId = idp.categoryId "
            "WHERE idp.idpId = ? AND idp.status = 'Active' AND category.status = 'Active'",
            (customerId, idpId))
        conn.commit()
        added = cursor.rowcount == 1
        conn.close()
        return added

    # UC35 View saved list
    # the customer's saved IDPs, most recently saved first
    def getSavedRecords(self, customerId):
        conn = getConnection()
        rows = conn.execute(SAVED_IDPS_SQL + " ORDER BY saved.savedDate DESC, saved.savedId DESC",
                            (customerId,)).fetchall()
        conn.close()
        return [IDP(**dict(row)) for row in rows]

    # UC34 Search saved list
    # the customer's saved IDPs whose title, description, location or category contain the keyword
    def searchSavedRecords(self, customerId, keyword):
        pattern = "%" + keyword + "%"
        conn = getConnection()
        rows = conn.execute(
            SAVED_IDPS_SQL + " AND (idp.title LIKE ? OR idp.description LIKE ? OR idp.location LIKE ? "
            "OR category.categoryName LIKE ?) ORDER BY saved.savedDate DESC, saved.savedId DESC",
            (customerId, pattern, pattern, pattern, pattern)).fetchall()
        conn.close()
        return [IDP(**dict(row)) for row in rows]
