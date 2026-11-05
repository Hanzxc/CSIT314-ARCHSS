# Entity: IDP - interior design project (used by US20, US42)
# A designer's project shown to customers. Current = still in progress, Past = completed.
# One row in the idp table.

from database.db import getConnection


class IDP:
    # UC20 Add current IDP
    # one IDP, new ones start as a Current, Active project
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

    # UC20 Add current IDP
    # the page has already checked the input - the entity only saves the IDP if its
    # category is still Active (it could have been suspended meanwhile, US44) and the
    # owner exists. designerId always comes from the session, never the form
    def addCurrentIDP(self, idp):
        conn = getConnection()
        cursor = conn.execute(
            "INSERT INTO idp (designerId, categoryId, title, description, location, projectType) "
            "SELECT ?, categoryId, ?, ?, ?, 'Current' FROM idp_category "
            "WHERE categoryId = ? AND status = 'Active' "
            "AND EXISTS (SELECT 1 FROM user_account WHERE userId = ?)",
            (idp.designerId, idp.title, idp.description, idp.location, idp.categoryId, idp.designerId))
        conn.commit()
        added = cursor.rowcount == 1
        conn.close()
        return added

    # UC25 Add past IDP
    # Saves a new project as 'Past' and 'Active'
    def addPastIDP(self, idp):
        conn = getConnection()
        cursor = conn.execute(
            "INSERT INTO idp (designerId, categoryId, title, description, location, projectType, status) "
            "SELECT ?, categoryId, ?, ?, ?, 'Past', 'Active' FROM idp_category "
            "WHERE categoryId = ? AND status = 'Active' "
            "AND EXISTS (SELECT 1 FROM user_account WHERE userId = ?)",
            (idp.designerId, idp.title, idp.description, idp.location, idp.categoryId, idp.designerId))
        conn.commit()
        added = cursor.rowcount == 1
        conn.close()
        return added

    # UC26 View past IDPs
    # Retrieves all Active past IDPs owned by the designer
    def getPastIDPsByDesigner(self, designerId):
        conn = getConnection()
        cursor = conn.execute(
            "SELECT i.*, c.categoryName FROM idp i "
            "LEFT JOIN idp_category c ON i.categoryId = c.categoryId "
            "WHERE i.designerId = ? AND i.projectType = 'Past' AND i.status = 'Active' "
            "ORDER BY i.createdDate DESC",
            (designerId,)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows

    # Helper method to get single IDP by ID
    def getIDPById(self, idpId):
        conn = getConnection()
        cursor = conn.execute(
            "SELECT i.*, c.categoryName FROM idp i "
            "LEFT JOIN idp_category c ON i.categoryId = c.categoryId "
            "WHERE i.idpId = ?",
            (idpId,)
        )
        row = cursor.fetchone()
        conn.close()
        return row

    # UC27 Update past IDP
    def updatePastIDP(self, idp):
        conn = getConnection()
        cursor = conn.execute(
            "UPDATE idp SET categoryId = ?, title = ?, description = ?, location = ? "
            "WHERE idpId = ? AND designerId = ? AND projectType = 'Past'",
            (idp.categoryId, idp.title, idp.description, idp.location, idp.idpId, idp.designerId)
        )
        conn.commit()
        updated = cursor.rowcount == 1
        conn.close()
        return updated

    # UC28 Delete past IDP (Soft-delete / set status to Suspended)
    def deletePastIDP(self, idpId, designerId):
        conn = getConnection()
        cursor = conn.execute(
            "UPDATE idp SET status = 'Suspended' "
            "WHERE idpId = ? AND designerId = ? AND projectType = 'Past'",
            (idpId, designerId)
        )
        conn.commit()
        deleted = cursor.rowcount == 1
        conn.close()
        return deleted

    # UC29 Search past IDPs
    def searchPastIDPs(self, designerId, keyword):
        conn = getConnection()
        search_kw = f"%{keyword}%"
        cursor = conn.execute(
            "SELECT i.*, c.categoryName FROM idp i "
            "LEFT JOIN idp_category c ON i.categoryId = c.categoryId "
            "WHERE i.designerId = ? AND i.projectType = 'Past' AND i.status = 'Active' "
            "AND (i.title LIKE ? OR i.description LIKE ? OR i.location LIKE ?) "
            "ORDER BY i.createdDate DESC",
            (designerId, search_kw, search_kw, search_kw)
        )
        rows = cursor.fetchall()
        conn.close()
        return rows
    
