# Control: GenerateWeeklyReportController - UC47 Generate weekly report (US47)

from entity.idpAnalytics import IDPAnalytics


class GenerateWeeklyReportController:
    # UC47 Generate weekly report
    # the entity works out the Monday-Sunday week, this returns its report unchanged
    def generateWeeklyReport(self, selectedDate):
        return IDPAnalytics().getWeeklyReport(selectedDate)
