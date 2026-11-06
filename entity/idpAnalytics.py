# Entity: IDPAnalytics - IDP views and saves (used by US37, US38, US46, US47, US48)
# reads the idp, idp_category, idp_view and saved_idp tables.
# one row in idp_view = one time a customer opened an IDP (US32 View IDP records it)

from database.db import getConnection


class IDPAnalytics:
    # UC32 View IDP (records the view that US37 and US46 - US48 count)
    # only counts a view of an IDP customers can actually see (Active IDP + Active category).
    # true if a view was saved
    def recordView(self, idpId):
        conn = getConnection()
        cursor = conn.execute(
            "INSERT INTO idp_view (idpId) "
            "SELECT idp.idpId FROM idp JOIN idp_category c ON c.categoryId = idp.categoryId "
            "WHERE idp.idpId = ? AND idp.status = 'Active' AND c.status = 'Active'",
            (idpId,))
        conn.commit()
        recorded = cursor.rowcount == 1
        conn.close()
        return recorded

    # UC37 View IDP view statistics
    # each of the designer's Active IDPs with how many times it was viewed (0 if never)
    def getViewStatistics(self, designerId):
        conn = getConnection()
        rows = conn.execute(
            "SELECT idp.idpId, idp.title, idp.projectType, c.categoryName, "
            "(SELECT COUNT(*) FROM idp_view v WHERE v.idpId = idp.idpId) AS views "
            "FROM idp LEFT JOIN idp_category c ON c.categoryId = idp.categoryId "
            "WHERE idp.designerId = ? AND idp.status = 'Active' "
            "ORDER BY views DESC, idp.title COLLATE NOCASE",
            (designerId,)).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # UC38 View IDP save statistics
    # each of the designer's Active IDPs with how many different customers have it saved
    def getSaveStatistics(self, designerId):
        conn = getConnection()
        rows = conn.execute(
            "SELECT idp.idpId, idp.title, idp.projectType, c.categoryName, "
            "(SELECT COUNT(DISTINCT s.customerId) FROM saved_idp s WHERE s.idpId = idp.idpId) AS saves "
            "FROM idp LEFT JOIN idp_category c ON c.categoryId = idp.categoryId "
            "WHERE idp.designerId = ? AND idp.status = 'Active' "
            "ORDER BY saves DESC, idp.title COLLATE NOCASE",
            (designerId,)).fetchall()
        conn.close()
        return [dict(row) for row in rows]

    # UC46 / UC47 / UC48 Generate daily / weekly / monthly report
    # every category with its views and saves between startDate and endDate (both included).
    # the database stores UTC times, so they're turned into local time before comparing -
    # otherwise a Singapore "today" report would miss everything before 8am
    def getCategoryReport(self, startDate, endDate):
        conn = getConnection()
        rows = conn.execute(
            "SELECT c.categoryId, c.categoryName, c.status, "
            "(SELECT COUNT(*) FROM idp WHERE idp.categoryId = c.categoryId AND idp.status = 'Active') AS totalIDPs, "
            "(SELECT COUNT(*) FROM idp_view v JOIN idp ON idp.idpId = v.idpId "
            " WHERE idp.categoryId = c.categoryId "
            " AND date(v.viewedAt, 'localtime') BETWEEN ? AND ?) AS views, "
            "(SELECT COUNT(*) FROM saved_idp s JOIN idp ON idp.idpId = s.idpId "
            " WHERE idp.categoryId = c.categoryId "
            " AND date(s.savedDate, 'localtime') BETWEEN ? AND ?) AS saves "
            "FROM idp_category c "
            "ORDER BY views DESC, saves DESC, c.categoryName COLLATE NOCASE",
            (startDate.isoformat(), endDate.isoformat(),
             startDate.isoformat(), endDate.isoformat())).fetchall()
        conn.close()
        return [dict(row) for row in rows]
