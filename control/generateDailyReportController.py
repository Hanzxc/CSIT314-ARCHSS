# Control: GenerateDailyReportController - UC46 Generate daily report (US46)

from entity.idpAnalytics import IDPAnalytics


class GenerateDailyReportController:
    # UC46 Generate daily report
    # the entity works out the period (just that day), this returns its report unchanged
    def generateDailyReport(self, selectedDate):
        return IDPAnalytics().getDailyReport(selectedDate)
