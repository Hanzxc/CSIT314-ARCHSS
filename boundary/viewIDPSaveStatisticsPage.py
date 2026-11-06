# Boundary: ViewIDPSaveStatisticsPage - UC38 View IDP save statistics (US38)
# templates: idpStatistics.html, interiorDesignerBase.html
# precondition: the designer is already logged in (US13), so there's no extra access check here

from flask import render_template, session

from control.viewIDPSaveStatisticsController import ViewIDPSaveStatisticsController

MSG_NO_IDPS = "You don't have any active IDPs yet, so there are no saves to show"


class ViewIDPSaveStatisticsPage:
    # UC38 View IDP save statistics
    def __init__(self):
        self.viewIDPSaveStatisticsController = ViewIDPSaveStatisticsController()

    # UC38 View IDP save statistics
    # designer clicked the "Saves" tab - get how many customers saved each of their own IDPs
    def clickViewIDPSaves(self):
        # always the logged-in designer's IDPs, never someone else's
        statistics = self.viewIDPSaveStatisticsController.getSaveStatistics(session["userId"])
        if not statistics:
            return self.displayNoIDPsMessage(MSG_NO_IDPS)      # alt flow - no IDPs yet
        return self.displayStatistics(statistics)

    # UC38 View IDP save statistics
    # table of IDPs, most saved first (wireframe 4a)
    def displayStatistics(self, statistics):
        return render_template("idpStatistics.html", metric="saves", statistics=statistics,
                               infoMessage=None, activePage="statistics")

    # UC38 View IDP save statistics
    # no table, just the message (wireframe 4b)
    def displayNoIDPsMessage(self, msg):
        return render_template("idpStatistics.html", metric="saves", statistics=[],
                               infoMessage=msg, activePage="statistics")
