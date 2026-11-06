# Entity: IDP - interior design project. Attribute names match the US20 model.
import sqlite3
import hashlib
import json

from database.db import getConnection


# A category suspension hides its IDPs without changing the project records.
VISIBLE_CURRENT_IDPS_SQL = """
    SELECT idp.*, category.categoryName
    FROM idp
    JOIN idp_category AS category ON category.categoryId = idp.categoryId
    WHERE idp.designerId = ? AND idp.projectType = 'Current'
      AND idp.status = 'Active' AND category.status = 'Active'
"""

# US25 - US29: the logged-in designer's own past IDPs that are still Active.
PAST_IDPS_SQL = """
    SELECT idp.*, category.categoryName
    FROM idp
    JOIN idp_category AS category ON category.categoryId = idp.categoryId
    WHERE idp.designerId = ? AND idp.projectType = 'Past' AND idp.status = 'Active'
"""

# US31 searches the customer catalogue across designers and project types.
VISIBLE_CUSTOMER_IDPS_SQL = """
    SELECT idp.*, category.categoryName
    FROM idp
    JOIN idp_category AS category ON category.categoryId = idp.categoryId
    WHERE idp.status = 'Active' AND category.status = 'Active'
"""


def _snapshotHash(*values):
    return hashlib.sha256(json.dumps(values, ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()


class IDP:
    def __init__(self, idpId=None, designerId=None, categoryId=None, title="", description="",
                 location="", projectType="Current", status="Active", createdDate=None,
                 categoryName=""):
        self.idpId = idpId
        self.designerId = designerId
        self.categoryId = categoryId
        self.title = title
        self.description = description
        self.location = location
        self.projectType = projectType
        self.status = status
        self.createdDate = createdDate
        self.categoryName = categoryName  # joined display value, not an idp table column

    def getCurrentIDPs(self, designerId):
        conn = getConnection()
        try:
            rows = conn.execute(VISIBLE_CURRENT_IDPS_SQL + " ORDER BY idp.idpId DESC",
                                (designerId,)).fetchall()
            return [IDP(**dict(row)) for row in rows]
        finally:
            conn.close()

    def getCurrentIDP(self, designerId, idpId):
        conn = getConnection()
        try:
            row = conn.execute(VISIBLE_CURRENT_IDPS_SQL + " AND idp.idpId = ?",
                               (designerId, idpId)).fetchone()
            return IDP(**dict(row)) if row is not None else None
        finally:
            conn.close()

    def searchCurrentIDPs(self, designerId, keyword):
        # Literal substring matching: %, _ and quotes are ordinary search characters.
        keyword = (keyword or "").strip().casefold()
        conn = getConnection()
        try:
            conn.create_function("casefold", 1, lambda text: (text or "").casefold(), deterministic=True)
            rows = conn.execute(
                VISIBLE_CURRENT_IDPS_SQL +
                " AND (instr(casefold(idp.title), ?) > 0 "
                "OR instr(casefold(idp.description), ?) > 0 "
                "OR instr(casefold(idp.location), ?) > 0 "
                "OR instr(casefold(category.categoryName), ?) > 0) ORDER BY idp.idpId DESC",
                (designerId, keyword, keyword, keyword, keyword)).fetchall()
            return [IDP(**dict(row)) for row in rows]
        finally:
            conn.close()

    def searchIDPs(self, keyword):
        keyword = (keyword or "").strip().casefold()
        conn = getConnection()
        try:
            conn.create_function("casefold", 1, lambda text: (text or "").casefold(), deterministic=True)
            rows = conn.execute(
                VISIBLE_CUSTOMER_IDPS_SQL +
                " AND (instr(casefold(idp.title), ?) > 0 "
                "OR instr(casefold(idp.description), ?) > 0 "
                "OR instr(casefold(idp.location), ?) > 0 "
                "OR instr(casefold(category.categoryName), ?) > 0) ORDER BY idp.idpId DESC",
                (keyword, keyword, keyword, keyword)).fetchall()
            return [IDP(**dict(row)) for row in rows]
        finally:
            conn.close()

    def getIDP(self, idpId):
        # US32 shares US31 catalogue visibility, including Current and Past IDPs.
        conn = getConnection()
        try:
            row = conn.execute(VISIBLE_CUSTOMER_IDPS_SQL + " AND idp.idpId = ?",
                               (idpId,)).fetchone()
            return IDP(**dict(row)) if row is not None else None
        finally:
            conn.close()

    def updateCurrentIDP(self, designerId, idpId, idpData):
        # Guard both the source project and destination category in the write itself.
        # Owner/type/status/creation date are never editable through this operation.
        conn = getConnection()
        try:
            cursor = conn.execute(
                "UPDATE idp SET title=?, categoryId=?, description=?, location=? "
                "WHERE idpId=? AND designerId=? AND projectType='Current' AND status='Active' "
                "AND EXISTS (SELECT 1 FROM idp_category AS source "
                "            WHERE source.categoryId=idp.categoryId AND source.status='Active') "
                "AND EXISTS (SELECT 1 FROM idp_category AS destination "
                "            WHERE destination.categoryId=? AND destination.status='Active')",
                (idpData["title"], idpData["categoryId"], idpData["description"], idpData["location"],
                 idpId, designerId, idpData["categoryId"]))
            conn.commit()
            return cursor.rowcount == 1
        except sqlite3.IntegrityError:
            conn.rollback()
            return False
        finally:
            conn.close()

    def getSnapshot(self):
        # Only the compact fingerprint is kept in the signed session cookie.
        return _snapshotHash(self.title, self.categoryId, self.description, self.location, self.createdDate)

    def suspendCurrentIDP(self, designerId, idpId, expectedSnapshot=None):
        # US23 Delete follows the company-profile convention: hide, preserve the record.
        sql = ("UPDATE idp SET status='Suspended' WHERE idpId=? AND designerId=? "
               "AND projectType='Current' AND status='Active' "
               "AND EXISTS (SELECT 1 FROM idp_category AS category "
               "WHERE category.categoryId=idp.categoryId AND category.status='Active')")
        values = [idpId, designerId]
        if expectedSnapshot is not None:
            # Compare exactly the content reviewed in the confirmation, in the same write.
            if not isinstance(expectedSnapshot, str) or len(expectedSnapshot) != 64:
                return False
            sql += " AND idpSnapshot(title, categoryId, description, location, createdDate) = ?"
            values.append(expectedSnapshot)
        conn = getConnection()
        try:
            conn.create_function("idpSnapshot", 5, _snapshotHash, deterministic=True)
            cursor = conn.execute(sql, values)
            conn.commit()
            return cursor.rowcount == 1
        finally:
            conn.close()


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

    # ---------- US25 - US29: past IDPs ----------
    # a past IDP is a row in the idp table with projectType 'Past' (same table as current IDPs).
    # the designer always only sees and changes their own, Active past IDPs

    # UC25 Add past IDP
    # the page has already checked the input - this only saves it if the category is still Active.
    # designerId comes from the session, never the form
    def createPastIDP(self, idp):
        conn = getConnection()
        cursor = conn.execute(
            "INSERT INTO idp (designerId, categoryId, title, description, location, projectType) "
            "SELECT ?, categoryId, ?, ?, ?, 'Past' FROM idp_category "
            "WHERE categoryId = ? AND status = 'Active'",
            (idp.designerId, idp.title, idp.description, idp.location, idp.categoryId))
        conn.commit()
        added = cursor.rowcount == 1
        conn.close()
        return added

    # UC26 View past IDPs
    # all of the designer's Active past IDPs, newest first
    def findPastIDPsByDesignerId(self, designerId):
        conn = getConnection()
        rows = conn.execute(PAST_IDPS_SQL + " ORDER BY idp.idpId DESC", (designerId,)).fetchall()
        conn.close()
        return [IDP(**dict(row)) for row in rows]

    # UC26 View past IDPs / UC27 Update past IDP / UC28 Delete past IDP
    # one past IDP, but only if it belongs to this designer and is still Active. None otherwise
    def getPastIDPDetails(self, designerId, idpId):
        conn = getConnection()
        row = conn.execute(PAST_IDPS_SQL + " AND idp.idpId = ?", (designerId, idpId)).fetchone()
        conn.close()
        return IDP(**dict(row)) if row is not None else None

    # UC27 Update past IDP
    # saves the new details - only the owner's Active past IDP, and only into an Active category
    def updatePastIDPDetails(self, idp):
        conn = getConnection()
        cursor = conn.execute(
            "UPDATE idp SET categoryId = ?, title = ?, description = ?, location = ? "
            "WHERE idpId = ? AND designerId = ? AND projectType = 'Past' AND status = 'Active' "
            "AND EXISTS (SELECT 1 FROM idp_category WHERE categoryId = ? AND status = 'Active')",
            (idp.categoryId, idp.title, idp.description, idp.location, idp.idpId, idp.designerId,
             idp.categoryId))
        conn.commit()
        updated = cursor.rowcount == 1
        conn.close()
        return updated

    # UC28 Delete past IDP
    # "delete" = mark it Suspended so it's no longer shown (the row and its views/saves are kept)
    def markPastIDPUnavailable(self, designerId, idpId):
        conn = getConnection()
        cursor = conn.execute(
            "UPDATE idp SET status = 'Suspended' "
            "WHERE idpId = ? AND designerId = ? AND projectType = 'Past' AND status = 'Active'",
            (idpId, designerId))
        conn.commit()
        deleted = cursor.rowcount == 1
        conn.close()
        return deleted

    # UC29 Search past IDPs
    # the designer's own Active past IDPs whose title, description, location or category contain the keyword
    def searchByKeywordAndDesigner(self, keyword, designerId):
        pattern = "%" + keyword + "%"
        conn = getConnection()
        rows = conn.execute(
            PAST_IDPS_SQL + " AND (idp.title LIKE ? OR idp.description LIKE ? OR idp.location LIKE ? "
            "OR category.categoryName LIKE ?) ORDER BY idp.idpId DESC",
            (designerId, pattern, pattern, pattern, pattern)).fetchall()
        conn.close()
        return [IDP(**dict(row)) for row in rows]
