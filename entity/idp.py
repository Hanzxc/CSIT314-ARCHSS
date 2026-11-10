# Entity: IDP - interior design project. Attribute names match the US20 model.
import sqlite3

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
# the category's status isn't checked on purpose: past IDPs are the designer's finished work history
PAST_IDPS_SQL = """
    SELECT idp.*, category.categoryName
    FROM idp
    JOIN idp_category AS category ON category.categoryId = idp.categoryId
    WHERE idp.designerId = ? AND idp.projectType = 'Past' AND idp.status = 'Active'
"""

# US31 / US32: the customer catalogue across designers and project types.
VISIBLE_CUSTOMER_IDPS_SQL = """
    SELECT idp.*, category.categoryName
    FROM idp
    JOIN idp_category AS category ON category.categoryId = idp.categoryId
    WHERE idp.status = 'Active' AND category.status = 'Active'
"""


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

    # UC21 View current IDPs
    # the owner's Active Current IDPs whose category is Active (US44), newest first
    def getCurrentIDPs(self, designerId):
        conn = getConnection()
        try:
            rows = conn.execute(VISIBLE_CURRENT_IDPS_SQL + " ORDER BY idp.idpId DESC",
                                (designerId,)).fetchall()
            return [IDP(**dict(row)) for row in rows]
        finally:
            conn.close()

    # UC21 View current IDPs (also the US22 / US23 loaders)
    # one of the owner's Active Current IDPs in an Active category, or None
    def getCurrentIDP(self, designerId, idpId):
        conn = getConnection()
        try:
            row = conn.execute(VISIBLE_CURRENT_IDPS_SQL + " AND idp.idpId = ?",
                               (designerId, idpId)).fetchone()
            return IDP(**dict(row)) if row is not None else None
        finally:
            conn.close()

    # UC24 Search current IDPs
    # literal, any-case match (%, _ and quotes are just text). the page already trimmed the keyword,
    # an empty one returns all of the owner's current IDPs
    def searchCurrentIDPs(self, designerId, keyword):
        keyword = keyword.casefold()
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

    # UC31 Search IDPs
    # every designer's Active IDPs (Current and Past) in Active categories, any-case match, newest
    # first. the page already trimmed the keyword
    def searchIDPs(self, keyword):
        keyword = keyword.casefold()
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

    # UC32 View IDP
    # the IDP if a customer can see it (it and its category are Active, Current or Past, any
    # designer), else None. when it's found and countView is True it also adds one idp_view row,
    # which the view statistics count (US37, US46 - US48)
    def viewIDP(self, idpId, countView):
        conn = getConnection()
        try:
            row = conn.execute(VISIBLE_CUSTOMER_IDPS_SQL + " AND idp.idpId = ?",
                               (idpId,)).fetchone()
            if row is None:
                return None
            if countView:
                conn.execute("INSERT INTO idp_view (idpId) VALUES (?)", (row["idpId"],))
                conn.commit()
            return IDP(**dict(row))
        finally:
            conn.close()

    # UC22 Update current IDP
    # only title, categoryId, description and location change, and only for the owner's Active
    # Current IDP whose old and new category are both Active. no row changed -> False
    def updateCurrentIDP(self, idp):
        conn = getConnection()
        try:
            cursor = conn.execute(
                "UPDATE idp SET title=?, categoryId=?, description=?, location=? "
                "WHERE idpId=? AND designerId=? AND projectType='Current' AND status='Active' "
                "AND EXISTS (SELECT 1 FROM idp_category AS source "
                "            WHERE source.categoryId=idp.categoryId AND source.status='Active') "
                "AND EXISTS (SELECT 1 FROM idp_category AS destination "
                "            WHERE destination.categoryId=? AND destination.status='Active')",
                (idp.title, idp.categoryId, idp.description, idp.location,
                 idp.idpId, idp.designerId, idp.categoryId))
            conn.commit()
            return cursor.rowcount == 1
        except sqlite3.IntegrityError:
            # the table's own CHECKs (e.g. title length) - nothing is saved
            conn.rollback()
            return False
        finally:
            conn.close()

    # UC23 Delete current IDP
    # soft delete - only the owner's Active Current IDP in an Active category becomes Suspended,
    # the row and its details are kept. no row changed -> False
    def suspendCurrentIDP(self, designerId, idpId):
        conn = getConnection()
        try:
            cursor = conn.execute(
                "UPDATE idp SET status='Suspended' WHERE idpId=? AND designerId=? "
                "AND projectType='Current' AND status='Active' "
                "AND EXISTS (SELECT 1 FROM idp_category AS category "
                "WHERE category.categoryId=idp.categoryId AND category.status='Active')",
                (idpId, designerId))
            conn.commit()
            return cursor.rowcount == 1
        finally:
            conn.close()


    def addCurrentIDP(self, idp):
        conn = getConnection()
        try:
            cursor = conn.execute(
                "INSERT INTO idp (designerId, categoryId, title, description, location, projectType) "
                "SELECT ?, categoryId, ?, ?, ?, 'Current' FROM idp_category "
                "WHERE categoryId = ? AND status = 'Active' "
                "AND EXISTS (SELECT 1 FROM user_account WHERE userId = ?)",
                (idp.designerId, idp.title, idp.description, idp.location, idp.categoryId, idp.designerId))
            conn.commit()
            return cursor.rowcount == 1
        finally:
            conn.close()

    # ---------- US25 - US29: past IDPs ----------
    # a past IDP is a row in the idp table with projectType 'Past' (same table as current IDPs).
    # the designer always only sees and changes their own, Active past IDPs

    # UC25 Add past IDP
    # the page has already checked the input - this only saves it if the category is still Active.
    # designerId comes from the session, never the form
    def createPastIDP(self, idp):
        conn = getConnection()
        try:
            cursor = conn.execute(
                "INSERT INTO idp (designerId, categoryId, title, description, location, projectType) "
                "SELECT ?, categoryId, ?, ?, ?, 'Past' FROM idp_category "
                "WHERE categoryId = ? AND status = 'Active'",
                (idp.designerId, idp.title, idp.description, idp.location, idp.categoryId))
            conn.commit()
            return cursor.rowcount == 1
        finally:
            conn.close()

    # UC26 View past IDPs
    # all of the designer's Active past IDPs, newest first
    def findPastIDPsByDesignerId(self, designerId):
        conn = getConnection()
        try:
            rows = conn.execute(PAST_IDPS_SQL + " ORDER BY idp.idpId DESC", (designerId,)).fetchall()
            return [IDP(**dict(row)) for row in rows]
        finally:
            conn.close()

    # UC26 View past IDPs / UC27 Update past IDP / UC28 Delete past IDP
    # one past IDP, but only if it belongs to this designer and is still Active. None otherwise
    def getPastIDPDetails(self, designerId, idpId):
        conn = getConnection()
        try:
            row = conn.execute(PAST_IDPS_SQL + " AND idp.idpId = ?", (designerId, idpId)).fetchone()
            return IDP(**dict(row)) if row is not None else None
        finally:
            conn.close()

    # UC27 Update past IDP
    # saves the new details - only the owner's Active past IDP, and only into an Active category
    def updatePastIDPDetails(self, idp):
        conn = getConnection()
        try:
            cursor = conn.execute(
                "UPDATE idp SET categoryId = ?, title = ?, description = ?, location = ? "
                "WHERE idpId = ? AND designerId = ? AND projectType = 'Past' AND status = 'Active' "
                "AND EXISTS (SELECT 1 FROM idp_category WHERE categoryId = ? AND status = 'Active')",
                (idp.categoryId, idp.title, idp.description, idp.location, idp.idpId, idp.designerId,
                 idp.categoryId))
            conn.commit()
            return cursor.rowcount == 1
        finally:
            conn.close()

    # UC28 Delete past IDP
    # "delete" = mark it Suspended so it's no longer shown (the row and its views/saves are kept)
    def markPastIDPUnavailable(self, designerId, idpId):
        conn = getConnection()
        try:
            cursor = conn.execute(
                "UPDATE idp SET status = 'Suspended' "
                "WHERE idpId = ? AND designerId = ? AND projectType = 'Past' AND status = 'Active'",
                (idpId, designerId))
            conn.commit()
            return cursor.rowcount == 1
        finally:
            conn.close()

    # UC29 Search past IDPs
    # the designer's own Active past IDPs whose title, description, location or category contain the keyword.
    # literal, any-case match like US24 (% and _ are just text). the page already trimmed the keyword
    def searchByKeywordAndDesigner(self, keyword, designerId):
        keyword = keyword.casefold()
        conn = getConnection()
        try:
            conn.create_function("casefold", 1, lambda text: (text or "").casefold(), deterministic=True)
            rows = conn.execute(
                PAST_IDPS_SQL +
                " AND (instr(casefold(idp.title), ?) > 0 "
                "OR instr(casefold(idp.description), ?) > 0 "
                "OR instr(casefold(idp.location), ?) > 0 "
                "OR instr(casefold(category.categoryName), ?) > 0) ORDER BY idp.idpId DESC",
                (designerId, keyword, keyword, keyword, keyword)).fetchall()
            return [IDP(**dict(row)) for row in rows]
        finally:
            conn.close()
