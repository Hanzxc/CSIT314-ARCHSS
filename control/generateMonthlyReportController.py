# Control: GenerateMonthlyReportController - UC48 Generate monthly report (US48)

from entity.idpAnalytics import IDPAnalytics


class GenerateMonthlyReportController:
    # UC48 Generate monthly report
    # the entity works out the whole month, this returns its report unchanged
    def generateMonthlyReport(self, selectedDate):
        return IDPAnalytics().getMonthlyReport(selectedDate)
