# Boundary: DeleteCurrentIDPPage - UC23 Delete current IDP (US23)
# templates: deleteCurrentIDP.html (the "are you sure?" box), currentIDPNotFound.html
# precondition: the designer is already logged in (US13), so there's no extra access check here.
# no token and nothing kept in the session - the entity only suspends the owner's Active Current IDP

from flask import flash, redirect, render_template, session, url_for

from control.deleteCurrentIDPController import DeleteCurrentIDPController

MSG_DELETED = "Current IDP deleted successfully"
MSG_NOT_FOUND = "Current IDP not found"


class DeleteCurrentIDPPage:
    # UC23 Delete current IDP
    # just sets up the controller
    def __init__(self):
        self.deleteCurrentIDPController = DeleteCurrentIDPController()

    # UC23 Delete current IDP
    # designer clicked "Delete current IDP" on the preview - show the box if it's still theirs
    def clickDelete(self, idpId):
        idp = self.deleteCurrentIDPController.getCurrentIDP(session["userId"], idpId)
        if idp is not None:
            return self.displayConfirmation(idp)
        return self.displayNotFoundMessage()

    # UC23 Delete current IDP
    # the box names the IDP, with Delete and Cancel - nothing is deleted yet
    def displayConfirmation(self, idp):
        return render_template("deleteCurrentIDP.html", idp=idp, activePage="currentIDPs")

    # UC23 Delete current IDP
    # works out if they clicked Delete or Cancel in the box. only "delete" deletes anything,
    # any other choice is treated like Cancel
    def submitDelete(self, idpId, choice):
        if choice == "delete":
            return self.confirmDelete(idpId)
        return self.cancelDelete(idpId)

    # UC23 Delete current IDP
    # the owner always comes from the session, never the form
    def confirmDelete(self, idpId):
        deleted = self.deleteCurrentIDPController.deleteCurrentIDP(session["userId"], idpId)
        if deleted:
            return self.displaySuccessMessage(MSG_DELETED)
        # already deleted, its category was suspended meanwhile, or it isn't this designer's
        return self.displayNotFoundMessage()

    # UC23 Delete current IDP
    # alt flow - nothing changes, back to the preview
    def cancelDelete(self, idpId):
        return redirect(url_for("viewCurrentIDP", idpId=idpId))

    # UC23 Delete current IDP
    # back to the Current IDPs list with a green message
    def displaySuccessMessage(self, msg):
        flash(msg, "success")
        return redirect(url_for("viewCurrentIDPs"))

    # UC23 Delete current IDP
    # HTTP 404 with no project details
    def displayNotFoundMessage(self):
        return render_template("currentIDPNotFound.html", errorMessage=MSG_NOT_FOUND,
                               activePage="currentIDPs"), 404
