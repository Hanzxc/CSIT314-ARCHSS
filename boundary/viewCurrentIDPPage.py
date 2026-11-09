# Boundary: ViewCurrentIDPPage - UC21 View current IDPs (US21)
# templates: currentIDPs.html, viewCurrentIDP.html, currentIDPNotFound.html
# precondition: the designer is already logged in (US13), so there's no extra access check here

from flask import render_template, session

from control.viewCurrentIDPController import ViewCurrentIDPController

MSG_NO_IDPS = "You have no current IDPs to display"
MSG_NOT_FOUND = "Current IDP not found"


class ViewCurrentIDPPage:
    # UC21 View current IDPs
    # just sets up the controller
    def __init__(self):
        self.viewCurrentIDPController = ViewCurrentIDPController()

    # UC21 View current IDPs
    # designer clicked "View current IDPs" - the owner is always the logged-in designer
    def clickViewCurrentIDPs(self):
        idps = self.viewCurrentIDPController.viewCurrentIDPs(session["userId"])
        if idps:
            return self.displayCurrentIDPs(idps)
        return self.displayNoIDPsMessage()

    # UC21 View current IDPs
    # designer clicked View on one IDP - someone else's / hidden / missing gives the not found page
    def selectCurrentIDP(self, idpId):
        idp = self.viewCurrentIDPController.viewCurrentIDP(session["userId"], idpId)
        if idp is not None:
            return self.displayCurrentIDP(idp)
        return self.displayNotFoundMessage()

    # UC21 View current IDPs
    # the list of project cards, newest first (wireframe 4a)
    def displayCurrentIDPs(self, idps):
        return render_template("currentIDPs.html", idps=idps, activePage="currentIDPs")

    # UC21 View current IDPs
    # what customers would see for this IDP (wireframe 4b)
    def displayCurrentIDP(self, idp):
        return render_template("viewCurrentIDP.html", idp=idp, activePage="currentIDPs")

    # UC21 View current IDPs
    # empty list is a normal page with a message (wireframe 4c)
    def displayNoIDPsMessage(self):
        return render_template("currentIDPs.html", idps=[], emptyMessage=MSG_NO_IDPS,
                               activePage="currentIDPs")

    # UC21 View current IDPs
    # HTTP 404 with no project details (wireframe 4d)
    def displayNotFoundMessage(self):
        return render_template("currentIDPNotFound.html", errorMessage=MSG_NOT_FOUND,
                               activePage="currentIDPs"), 404
