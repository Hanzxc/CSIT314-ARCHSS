# Boundary: UpdateCurrentIDPPage - UC22 Update a current IDP.
import secrets

from flask import flash, redirect, render_template, session, url_for

from control.updateCurrentIDPController import UpdateCurrentIDPController

FORM_FIELDS = ("title", "categoryId", "description", "location")
MSG_UPDATED = "Current IDP updated successfully"
MSG_FIX_FIELDS = "Please fix the highlighted fields"
MSG_NOT_FOUND = "Current IDP not found"
MSG_FAILED = "Current IDP could not be updated. Please try again"
MSG_INVALID_FORM = "This update form is no longer valid. Reopen it and try again"


class UpdateCurrentIDPPage:
    def __init__(self):
        self.updateCurrentIDPController = UpdateCurrentIDPController()
        self.idpId = None
        self.idpData = {}
        self.fieldErrors = {}

    def checkAccess(self):
        if "userId" not in session:
            return redirect(url_for("interiorDesignerLogin"))
        if not self.updateCurrentIDPController.canUpdateCurrentIDP(session["userId"]):
            return render_template("interiorDesignerAccessDenied.html"), 403
        return None

    def prepareUpdateToken(self):
        tokens = dict(session.get("currentIDPUpdateTokens", {}))
        token = secrets.token_urlsafe(32)
        tokens[str(self.idpId)] = {"token": token, "designerId": session["userId"]}
        # Keep the signed session cookie small when several projects are open.
        while len(tokens) > 8:
            del tokens[next(iter(tokens))]
        session["currentIDPUpdateTokens"] = tokens
        return token

    def validateUpdateToken(self, updateToken):
        expected = session.get("currentIDPUpdateTokens", {}).get(str(self.idpId), {})
        return (expected.get("designerId") == session["userId"]
                and isinstance(updateToken, str)
                and bool(expected.get("token"))
                and secrets.compare_digest(updateToken.encode("utf-8"), expected["token"].encode("utf-8")))

    def clickUpdate(self, idpId):
        self.idpId = idpId
        denied = self.checkAccess()
        if denied is not None:
            return denied
        try:
            idp = self.updateCurrentIDPController.getCurrentIDP(session["userId"], idpId)
            if idp is None:
                return self.displayNotFoundMessage()
            self.idpData = {field: getattr(idp, field) for field in FORM_FIELDS}
            return self.displayUpdateForm()
        except PermissionError:
            return render_template("interiorDesignerAccessDenied.html"), 403

    def displayUpdateForm(self, msg=None):
        categories = self.updateCurrentIDPController.getActiveIDPCategories(session["userId"])
        return render_template("updateCurrentIDP.html", idpId=self.idpId, idpData=self.idpData,
                               categories=categories, fieldErrors=self.fieldErrors, errorMessage=msg,
                               updateToken=self.prepareUpdateToken(), activePage="currentIDPs")

    def validateInput(self, idpData):
        self.fieldErrors = self.updateCurrentIDPController.getFieldErrors(idpData)
        return not self.fieldErrors

    def submitUpdate(self, idpId, idpData, updateToken):
        self.idpId = idpId
        self.idpData = idpData
        denied = self.checkAccess()
        if denied is not None:
            return denied
        designerId = session["userId"]
        try:
            if self.updateCurrentIDPController.getCurrentIDP(designerId, idpId) is None:
                return self.displayNotFoundMessage()
            if not self.validateUpdateToken(updateToken):
                return render_template("currentIDPUpdateError.html", errorMessage=MSG_INVALID_FORM,
                                       idpId=idpId, activePage="currentIDPs"), 403
            if not self.validateInput(idpData):
                return self.displayErrorMessage(MSG_FIX_FIELDS)
            if self.updateCurrentIDPController.updateCurrentIDP(designerId, idpId, idpData):
                return self.displaySuccessMessage(MSG_UPDATED)
            if self.updateCurrentIDPController.getCurrentIDP(designerId, idpId) is None:
                return self.displayNotFoundMessage()
            # A destination category may have been suspended after input validation.
            self.validateInput(idpData)
            return self.displayErrorMessage(MSG_FIX_FIELDS if self.fieldErrors else MSG_FAILED)
        except PermissionError:
            return render_template("interiorDesignerAccessDenied.html"), 403

    def displaySuccessMessage(self, msg):
        tokens = dict(session.get("currentIDPUpdateTokens", {}))
        tokens.pop(str(self.idpId), None)
        session["currentIDPUpdateTokens"] = tokens
        flash(msg, "success")
        return redirect(url_for("viewCurrentIDP", idpId=self.idpId))

    def displayErrorMessage(self, msg):
        return self.displayUpdateForm(msg)

    def displayNotFoundMessage(self):
        return render_template("currentIDPNotFound.html", errorMessage=MSG_NOT_FOUND,
                               activePage="currentIDPs"), 404
