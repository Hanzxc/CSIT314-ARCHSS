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
