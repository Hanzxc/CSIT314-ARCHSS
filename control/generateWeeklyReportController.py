# Control: GenerateWeeklyReportController - UC47 Generate weekly report (US47)

from datetime import timedelta

from entity.idpAnalytics import IDPAnalytics


class GenerateWeeklyReportController:
    # UC47 Generate weekly report
    # a week is Monday to Sunday, so any day picked gives the week it falls in
    def generateWeeklyReport(self, selectedDate):
        startDate = selectedDate - timedelta(days=selectedDate.weekday())
        endDate = startDate + timedelta(days=6)
        categories = IDPAnalytics().getCategoryReport(startDate, endDate)
        return {"startDate": startDate, "endDate": endDate, "categories": categories}
