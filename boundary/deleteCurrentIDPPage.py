# Boundary: DeleteCurrentIDPPage - UC23 Delete current IDP.
from secrets import compare_digest, token_urlsafe

from flask import flash, redirect, render_template, session, url_for

from control.deleteCurrentIDPController import DeleteCurrentIDPController

MSG_DELETED = "Current IDP deleted successfully"
MSG_NOT_FOUND = "Current IDP not found"
MSG_CONFIRM_AGAIN = "Please reopen the delete confirmation and try again"
MSG_CHANGED = "This IDP changed after confirmation was opened. Please review it and confirm again"


class DeleteCurrentIDPPage:
    def __init__(self):
        self.deleteCurrentIDPController = DeleteCurrentIDPController()

    def checkAccess(self):
        if "userId" not in session:
            return redirect(url_for("interiorDesignerLogin"))
        if not self.deleteCurrentIDPController.canDeleteCurrentIDP(session["userId"]):
            return render_template("interiorDesignerAccessDenied.html"), 403
        return None

    def clickDelete(self, idpId):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        try:
            idp = self.deleteCurrentIDPController.getCurrentIDP(session["userId"], idpId)
            if idp is None:
                return self.displayNotFoundMessage()
            return self.displayConfirmation(idp)
        except PermissionError:
            return render_template("interiorDesignerAccessDenied.html"), 403

    def displayConfirmation(self, idp):
        token = token_urlsafe(32)
        session["currentIDPDeleteConfirmation"] = {
            "designerId": session["userId"], "idpId": idp.idpId, "token": token,
            "expectedSnapshot": self.deleteCurrentIDPController.getSnapshot(idp)}
        return render_template("deleteCurrentIDP.html", idp=idp, confirmationToken=token,
                               activePage="currentIDPs")

    def validateConfirmation(self, idpId, confirmationToken):
        confirmation = session.get("currentIDPDeleteConfirmation", {})
        return (confirmation.get("designerId") == session["userId"]
                and confirmation.get("idpId") == idpId
                and isinstance(confirmationToken, str) and bool(confirmationToken)
                and isinstance(confirmation.get("expectedSnapshot"), str)
                and len(confirmation["expectedSnapshot"]) == 64
                and compare_digest(confirmation.get("token", "").encode("utf-8"), confirmationToken.encode("utf-8")))

    def submitDelete(self, idpId, choice, confirmationToken):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        try:
            if self.deleteCurrentIDPController.getCurrentIDP(session["userId"], idpId) is None:
                return self.displayNotFoundMessage()
            if not self.validateConfirmation(idpId, confirmationToken):
                return self.displayErrorMessage(idpId, MSG_CONFIRM_AGAIN, 403)
            if choice == "cancel":
                return self.cancelDelete(idpId)
            if choice != "delete":
                return self.displayErrorMessage(idpId, MSG_CONFIRM_AGAIN, 400)
            return self.confirmDelete(idpId)
        except PermissionError:
            return render_template("interiorDesignerAccessDenied.html"), 403

    def confirmDelete(self, idpId):
        # Only called after submitDelete has validated access and the bound confirmation.
        confirmation = session.pop("currentIDPDeleteConfirmation")
        if self.deleteCurrentIDPController.deleteCurrentIDP(session["userId"], idpId, confirmation["expectedSnapshot"]):
            tokens = dict(session.get("currentIDPUpdateTokens", {}))
            tokens.pop(str(idpId), None)
            session["currentIDPUpdateTokens"] = tokens
            return self.displaySuccessMessage(MSG_DELETED)
        if self.deleteCurrentIDPController.getCurrentIDP(session["userId"], idpId) is None:
            return self.displayNotFoundMessage()
        return self.displayErrorMessage(idpId, MSG_CHANGED, 409)

    def cancelDelete(self, idpId):
        session.pop("currentIDPDeleteConfirmation", None)
        return self.closeConfirmation(idpId)

    def closeConfirmation(self, idpId):
        return redirect(url_for("viewCurrentIDP", idpId=idpId))

    def displaySuccessMessage(self, msg):
        flash(msg, "success")
        return redirect(url_for("viewCurrentIDPs"))

    def displayErrorMessage(self, idpId, msg, status=400):
        return render_template("currentIDPDeleteError.html", idpId=idpId, errorMessage=msg,
                               activePage="currentIDPs"), status

    def displayNotFoundMessage(self):
        return render_template("currentIDPNotFound.html", errorMessage=MSG_NOT_FOUND,
                               activePage="currentIDPs"), 404
