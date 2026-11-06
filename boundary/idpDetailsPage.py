# Boundary: IDPDetailsPage - UC33 Save IDP (US33)
# the Save button on the IDP details page. showing the details themselves is US32 (ViewIDPPage),
# so after saving the customer goes back to that page with a message.
# precondition: the customer is already logged in (US30), so there's no extra access check here

from flask import flash, redirect, session, url_for

from control.saveIDPController import SaveIDPController

MSG_SAVED = "IDP saved to your saved list"
MSG_ALREADY_SAVED = "This IDP is already in your saved list"
MSG_UNAVAILABLE = "This IDP is no longer available to save"


class IDPDetailsPage:
    def __init__(self):
        self.saveIDPController = SaveIDPController()

    # UC33 Save IDP
    # customer clicked "Save IDP" on an IDP's details page
    def clickSave(self, idpId):
        customerId = session["userId"]
        if self.saveIDPController.checkAlreadySaved(customerId, idpId):
            return self.displayAlreadySavedMessage(idpId, MSG_ALREADY_SAVED)     # alt flow A1
        if self.saveIDPController.saveIDP(customerId, idpId):
            return self.displaySavedState(idpId, MSG_SAVED)
        return self.displayErrorMessage(idpId, MSG_UNAVAILABLE)                  # deleted / hidden meanwhile

    # UC33 Save IDP
    # back to the IDP's details, the button now shows "Saved" (wireframe 4b)
    def displaySavedState(self, idpId, msg):
        flash(msg, "success")
        return redirect(url_for("viewIDP", idpId=idpId))

    # UC33 Save IDP
    # nothing new is added, the customer is just told (wireframe 4c)
    def displayAlreadySavedMessage(self, idpId, msg):
        flash(msg, "info")
        return redirect(url_for("viewIDP", idpId=idpId))

    # UC33 Save IDP
    def displayErrorMessage(self, idpId, msg):
        flash(msg, "error")
        return redirect(url_for("viewIDP", idpId=idpId))
