# Boundary: IDPDetailsPage - UC33 Save IDP (US33)
# the Save button on the IDP details page. showing the details themselves is US32 (ViewIDPPage),
# so after saving the customer goes back to that page (?saved=1, not counted as a view) with a message.
# precondition: the customer is already logged in (US30), so there's no extra access check here

from flask import flash, redirect, session, url_for

from control.saveIDPController import SaveIDPController

MSG_SAVED = "IDP saved to your saved list"
MSG_NOT_SAVED = "This IDP is already in your saved list or is no longer available"


class IDPDetailsPage:
    def __init__(self):
        self.saveIDPController = SaveIDPController()

    # UC33 Save IDP
    # customer clicked "Save IDP" on an IDP's details page. no check first - the entity refuses
    # a duplicate or an IDP customers can't see any more
    def clickSave(self, idpId):
        customerId = session["userId"]
        saved = self.saveIDPController.saveIDP(customerId, idpId)
        if saved:
            return self.displaySavedState(idpId, MSG_SAVED)
        return self.displayErrorMessage(idpId, MSG_NOT_SAVED)         # alt flow 3a

    # UC33 Save IDP
    # back to the IDP's details with a green message, the Save IDP button is still there (wireframe 4b)
    def displaySavedState(self, idpId, msg):
        flash(msg, "success")
        return redirect(url_for("viewIDP", idpId=idpId, saved=1))

    # UC33 Save IDP
    # already saved or no longer available - nothing added, back to the details (wireframe 4c)
    def displayErrorMessage(self, idpId, msg):
        flash(msg, "error")
        return redirect(url_for("viewIDP", idpId=idpId, saved=1))
