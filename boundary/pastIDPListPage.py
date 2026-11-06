# Boundary: PastIDPListPage - UC26 View past IDPs (US26) and UC28 Delete past IDP (US28)
# the designer's list of past IDPs, the details of one, and the Delete button with its "are you sure?" box.
# US26 and US28 each have their own controller.
# templates: pastIDPs.html, viewPastIDP.html, deletePastIDP.html, pastIDPNotFound.html
# precondition: the designer is already logged in (US13), so there's no extra access check here

from flask import flash, redirect, render_template, session, url_for

from control.viewPastIDPController import ViewPastIDPController
from control.deletePastIDPController import DeletePastIDPController

MSG_NO_PAST_IDPS = "You have no past IDPs yet"
MSG_NOT_FOUND = "Past IDP not found"
MSG_DELETED = "Past IDP deleted successfully"
MSG_NOT_DELETED = "Past IDP could not be deleted. Please try again"


class PastIDPListPage:
    def __init__(self):
        self.viewPastIDPController = ViewPastIDPController()
        self.deletePastIDPController = DeletePastIDPController()

    # ---------- UC26 View past IDPs ----------

    # UC26 View past IDPs
    # designer clicked "Past IDPs" - list their own past IDPs, newest first (wireframe 4a)
    def openPastIDPs(self):
        pastIDPs = self.viewPastIDPController.getPastIDPs(session["userId"])
        if not pastIDPs:
            return self.displayEmptyMessage(MSG_NO_PAST_IDPS)     # alt flow - nothing added yet (4c)
        return self.displayPastIDPList(pastIDPs)

    # UC26 View past IDPs
    def displayPastIDPList(self, pastIDPs):
        return render_template("pastIDPs.html", idps=pastIDPs, keyword="", activePage="pastIDPs")

    # UC26 View past IDPs
    def displayEmptyMessage(self, msg):
        return render_template("pastIDPs.html", idps=[], keyword="", infoMessage=msg, activePage="pastIDPs")

    # UC26 View past IDPs
    # designer clicked View on one past IDP (wireframe 4b)
    def selectPastIDP(self, idpId):
        idp = self.viewPastIDPController.getPastIDPDetails(session["userId"], idpId)
        if idp is None:
            return self.displayNotFoundMessage(MSG_NOT_FOUND)     # not theirs / deleted (4d)
        return self.displayPastIDPDetails(idp)

    # UC26 View past IDPs
    def displayPastIDPDetails(self, idp):
        return render_template("viewPastIDP.html", idp=idp, activePage="pastIDPs")

    # UC26 View past IDPs / UC28 Delete past IDP
    def displayNotFoundMessage(self, msg):
        return render_template("pastIDPNotFound.html", errorMessage=msg, activePage="pastIDPs"), 404

    # ---------- UC28 Delete past IDP ----------

    # UC28 Delete past IDP
    # designer clicked Delete - show the "are you sure?" box over the IDP (wireframe 4a)
    def clickDelete(self, idpId):
        idp = self.deletePastIDPController.getPastIDP(session["userId"], idpId)
        if idp is None:
            return self.displayNotFoundMessage(MSG_NOT_FOUND)
        return self.displayDeleteConfirmation(idp)

    # UC28 Delete past IDP
    def displayDeleteConfirmation(self, idp):
        return render_template("deletePastIDP.html", idp=idp, activePage="pastIDPs")

    # UC28 Delete past IDP
    # designer pressed "Delete past IDP" in the box
    def confirmDeletion(self, idpId):
        if self.deletePastIDPController.deletePastIDP(session["userId"], idpId):
            return self.refreshPastIDPList(MSG_DELETED)
        if self.deletePastIDPController.getPastIDP(session["userId"], idpId) is None:
            return self.displayNotFoundMessage(MSG_NOT_FOUND)
        flash(MSG_NOT_DELETED, "error")
        return redirect(url_for("viewPastIDP", idpId=idpId))

    # UC28 Delete past IDP
    # designer pressed Cancel - nothing is deleted, back to the IDP's details (alt flow)
    def cancelDeletion(self, idpId):
        return redirect(url_for("viewPastIDP", idpId=idpId))

    # UC28 Delete past IDP
    # back to the list (the deleted IDP is gone from it) with a green message (wireframe 4b)
    def refreshPastIDPList(self, msg):
        flash(msg, "success")
        return redirect(url_for("pastIDPs"))
