# Boundary: ViewCurrentIDPPage - UC21 View current IDPs.
from flask import redirect, render_template, session, url_for

from control.viewCurrentIDPController import ViewCurrentIDPController

MSG_NO_IDPS = "You have no current IDPs to display"
MSG_NOT_FOUND = "Current IDP not found"


class ViewCurrentIDPPage:
    def __init__(self):
        self.viewCurrentIDPController = ViewCurrentIDPController()

    def checkAccess(self):
        if "userId" not in session:
            return redirect(url_for("interiorDesignerLogin"))
        if not self.viewCurrentIDPController.canViewCurrentIDPs(session["userId"]):
            return render_template("interiorDesignerAccessDenied.html"), 403
        return None

    def clickViewCurrentIDPs(self):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        try:
            idps = self.viewCurrentIDPController.viewCurrentIDPs(session["userId"])
        except PermissionError:
            return render_template("interiorDesignerAccessDenied.html"), 403
        if not idps:
            return self.displayNoIDPsMessage()
        return self.displayCurrentIDPs(idps)

    def selectCurrentIDP(self, idpId):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        try:
            idp = self.viewCurrentIDPController.viewCurrentIDP(session["userId"], idpId)
        except PermissionError:
            return render_template("interiorDesignerAccessDenied.html"), 403
        if idp is None:
            return self.displayErrorMessage(MSG_NOT_FOUND)
        return self.displayCurrentIDP(idp)

    def displayCurrentIDPs(self, idps):
        return render_template("currentIDPs.html", idps=idps, activePage="currentIDPs")

    def displayCurrentIDP(self, idp):
        return render_template("viewCurrentIDP.html", idp=idp, activePage="currentIDPs")

    def displayNoIDPsMessage(self):
        return render_template("currentIDPs.html", idps=[], emptyMessage=MSG_NO_IDPS,
                               activePage="currentIDPs")

    def displayErrorMessage(self, msg):
        return render_template("currentIDPNotFound.html", errorMessage=msg,
                               activePage="currentIDPs"), 404
