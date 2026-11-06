# Control: GenerateDailyReportController - UC46 Generate daily report (US46)

from entity.idpAnalytics import IDPAnalytics


class GenerateDailyReportController:
    # UC46 Generate daily report
    # a daily report covers just the chosen day. returns the period + one row per category
    def generateDailyReport(self, selectedDate):
        startDate = selectedDate
        endDate = selectedDate
        categories = IDPAnalytics().getCategoryReport(startDate, endDate)
        return {"startDate": startDate, "endDate": endDate, "categories": categories}
