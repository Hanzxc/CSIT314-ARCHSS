# Boundary: GenerateMonthlyReportPage - UC48 Generate monthly report (US48)
# templates: idpCategoryReport.html, platformManagerBase.html
# precondition: the platform manager is already logged in (US39), so there's no extra access check here

from datetime import date, datetime

from flask import render_template

from control.generateMonthlyReportController import GenerateMonthlyReportController

MSG_INVALID_DATE = "Please choose a valid date"
MSG_FUTURE_DATE = "The date can't be in the future"
MSG_NO_ACTIVITY = "No IDPs were viewed or saved in this period"


class GenerateMonthlyReportPage:
    # UC48 Generate monthly report
    # the date box starts on today
    def __init__(self):
        self.generateMonthlyReportController = GenerateMonthlyReportController()
        self.selectedDate = date.today().isoformat()

    # UC48 Generate monthly report
    # manager clicked "Monthly report" - just show the date box, no report yet (wireframe 4a).
    # any day can be picked - the entity works out the whole month
    def clickGenerateMonthlyReport(self):
        return self.displayReportForm()

    # UC48 Generate monthly report
    # the date box, plus the report or an error message when there is one
    def displayReportForm(self, report=None, errorMessage=None, infoMessage=None):
        return render_template("idpCategoryReport.html", period="monthly", selectedDate=self.selectedDate,
                               report=report, errorMessage=errorMessage, infoMessage=infoMessage,
                               activePage="reports")

    # UC48 Generate monthly report
    # the date has to be a real YYYY-MM-DD date and not after today. returns the error, or None if ok
    def validateDate(self, selectedDate):
        try:
            chosen = datetime.strptime(selectedDate, "%Y-%m-%d").date()
        except ValueError:
            return MSG_INVALID_DATE
        if chosen > date.today():
            return MSG_FUTURE_DATE
        return None

    # UC48 Generate monthly report
    # manager picked a date and pressed "Generate report"
    def submitDate(self, selectedDate):
        self.selectedDate = selectedDate.strip()
        # bad date -> controller never gets called (outer alt in the seq diagram)
        error = self.validateDate(self.selectedDate)
        if error:
            return self.displayErrorMessage(error)
        selectedDate = datetime.strptime(self.selectedDate, "%Y-%m-%d").date()
        report = self.generateMonthlyReportController.generateMonthlyReport(selectedDate)
        # inner alt: the note only when no category was viewed or saved at all
        if any(row.views or row.saves for row in report.categories):
            return self.displayReport(report)
        return self.displayReport(report, MSG_NO_ACTIVITY)

    # UC48 Generate monthly report
    # categories ranked by views then saves (wireframe 4b), or with MSG_NO_ACTIVITY above them (4c)
    def displayReport(self, report, msg=None):
        return self.displayReportForm(report, infoMessage=msg)

    # UC48 Generate monthly report
    # same date box again with the message on top (wireframe 4d)
    def displayErrorMessage(self, msg):
        return self.displayReportForm(errorMessage=msg), 400
