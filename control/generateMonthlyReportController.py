# Control: GenerateMonthlyReportController - UC48 Generate monthly report (US48)

from datetime import timedelta

from entity.idpAnalytics import IDPAnalytics


class GenerateMonthlyReportController:
    # UC48 Generate monthly report
    # first to last day of the month the picked day is in (December rolls into next January)
    def generateMonthlyReport(self, selectedDate):
        startDate = selectedDate.replace(day=1)
        nextMonth = (startDate.replace(day=28) + timedelta(days=4)).replace(day=1)
        endDate = nextMonth - timedelta(days=1)
        categories = IDPAnalytics().getCategoryReport(startDate, endDate)
        return {"startDate": startDate, "endDate": endDate, "categories": categories}
