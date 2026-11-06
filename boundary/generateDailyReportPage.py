# Boundary: GenerateDailyReportPage - UC46 Generate daily report (US46)
# templates: idpCategoryReport.html, platformManagerBase.html
# precondition: the platform manager is already logged in (US39), so there's no extra access check here

from datetime import date

from flask import render_template

from control.generateDailyReportController import GenerateDailyReportController

MSG_INVALID_DATE = "Please choose a valid date"
MSG_FUTURE_DATE = "The date can't be in the future"
MSG_NO_ACTIVITY = "No IDPs were viewed or saved in this period"


class GenerateDailyReportPage:
    # UC46 Generate daily report
    # the date box starts on today
    def __init__(self):
        self.generateDailyReportController = GenerateDailyReportController()
        self.selectedDate = date.today().isoformat()

    # UC46 Generate daily report
    # manager clicked "Daily report" - just show the date box, no report yet (wireframe 4a)
    def clickGenerateDailyReport(self):
        return self.displayReportForm()

    # UC46 Generate daily report
    # the date box, plus the report or an error message when there is one
    def displayReportForm(self, report=None, errorMessage=None, infoMessage=None):
        return render_template("idpCategoryReport.html", period="daily", selectedDate=self.selectedDate,
                               report=report, errorMessage=errorMessage, infoMessage=infoMessage,
                               activePage="reports")

    # UC46 Generate daily report
    # the date has to be a real YYYY-MM-DD date and not after today. returns the error, or None if ok
    def validateDate(self, selectedDate):
        try:
            chosen = date.fromisoformat(selectedDate)
        except ValueError:
            return MSG_INVALID_DATE
        if chosen > date.today():
            return MSG_FUTURE_DATE
        return None

    # UC46 Generate daily report
    # manager picked a date and pressed "Generate report"
    def submitDate(self, selectedDate):
        self.selectedDate = selectedDate.strip()
        # bad date -> controller never gets called (outer alt in the seq diagram)
        error = self.validateDate(self.selectedDate)
        if error:
            return self.displayErrorMessage(error)
        report = self.generateDailyReportController.generateDailyReport(date.fromisoformat(self.selectedDate))
        return self.displayReport(report)

    # UC46 Generate daily report
    # categories ranked by views then saves (wireframe 4b), or a note if nothing happened (4c)
    def displayReport(self, report):
        if all(row["views"] == 0 and row["saves"] == 0 for row in report["categories"]):
            return self.displayReportForm(report, infoMessage=MSG_NO_ACTIVITY)
        return self.displayReportForm(report)

    # UC46 Generate daily report
    # same date box again with the message on top (wireframe 4d)
    def displayErrorMessage(self, msg):
        return self.displayReportForm(errorMessage=msg), 400
