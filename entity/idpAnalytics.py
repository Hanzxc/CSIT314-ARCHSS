# Entity: IDPAnalytics - IDP views and saves (used by US37, US38, US46, US47, US48)
# reads the idp, idp_category, idp_view and saved_idp tables.
# one row in idp_view = one time a customer opened an IDP (UC32 View IDP adds it in IDP.viewIDP),
# one row in saved_idp = one customer saved an IDP (UC33 Save IDP).
# a statistics row (US37/38), a category row and a whole report (US46 - US48) are all IDPAnalytics objects

from datetime import timedelta

from database.db import getConnection


class IDPAnalytics:
    def __init__(self, idpId=None, title=None, projectType=None, categoryId=None, categoryName=None,
                 status=None, views=0, saves=0, totalIDPs=0, startDate=None, endDate=None, categories=None):
        self.idpId = idpId
        self.title = title
        self.projectType = projectType
        self.categoryId = categoryId
        self.categoryName = categoryName
        self.status = status
        self.views = views
        self.saves = saves
        self.totalIDPs = totalIDPs
        self.startDate = startDate
        self.endDate = endDate
        self.categories = categories or []

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
        return [IDPAnalytics(**dict(row)) for row in rows]

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
        return [IDPAnalytics(**dict(row)) for row in rows]

    # UC46 Generate daily report
    # a daily report covers just the chosen day
    def getDailyReport(self, selectedDate):
        startDate = selectedDate
        endDate = selectedDate
        return IDPAnalytics(startDate=startDate, endDate=endDate,
                            categories=self.getCategoryReport(startDate, endDate))

    # UC47 Generate weekly report
    # a week is Monday to Sunday, so any day picked gives the week it falls in
    def getWeeklyReport(self, selectedDate):
        startDate = selectedDate - timedelta(days=selectedDate.weekday())
        endDate = startDate + timedelta(days=6)
        return IDPAnalytics(startDate=startDate, endDate=endDate,
                            categories=self.getCategoryReport(startDate, endDate))

    # UC48 Generate monthly report
    # first to last day of the month the picked day is in (December rolls into next January)
    def getMonthlyReport(self, selectedDate):
        startDate = selectedDate.replace(day=1)
        nextMonth = (startDate.replace(day=28) + timedelta(days=4)).replace(day=1)
        endDate = nextMonth - timedelta(days=1)
        return IDPAnalytics(startDate=startDate, endDate=endDate,
                            categories=self.getCategoryReport(startDate, endDate))

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
        return [IDPAnalytics(**dict(row)) for row in rows]
