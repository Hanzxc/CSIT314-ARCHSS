# Boundary: ViewIDPViewStatisticsPage - UC37 View IDP view statistics (US37)
# templates: idpStatistics.html, interiorDesignerBase.html
# precondition: the designer is already logged in (US13), so there's no extra access check here

from flask import render_template, session

from control.viewIDPViewStatisticsController import ViewIDPViewStatisticsController

MSG_NO_IDPS = "You don't have any active IDPs yet, so there are no views to show"


class ViewIDPViewStatisticsPage:
    # UC37 View IDP view statistics
    def __init__(self):
        self.viewIDPViewStatisticsController = ViewIDPViewStatisticsController()

    # UC37 View IDP view statistics
    # designer clicked "IDP statistics" - get the view count of each of their own IDPs
    def clickViewIDPViews(self):
        # always the logged-in designer's IDPs, never someone else's
        statistics = self.viewIDPViewStatisticsController.getViewStatistics(session["userId"])
        if not statistics:
            return self.displayNoIDPsMessage(MSG_NO_IDPS)      # alt flow - no IDPs yet
        return self.displayStatistics(statistics)

    # UC37 View IDP view statistics
    # table of IDPs, most viewed first (wireframe 4a)
    def displayStatistics(self, statistics):
        return render_template("idpStatistics.html", metric="views", statistics=statistics,
                               infoMessage=None, activePage="statistics")

    # UC37 View IDP view statistics
    # no table, just the message (wireframe 4b)
    def displayNoIDPsMessage(self, msg):
        return render_template("idpStatistics.html", metric="views", statistics=[],
                               infoMessage=msg, activePage="statistics")
