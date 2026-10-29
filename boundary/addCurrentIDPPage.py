# Boundary: AddCurrentIDPPage - UC20 Add current IDP (US20)
# templates: addCurrentIDP.html, interiorDesignerBase.html

from flask import flash, redirect, render_template, session, url_for

from control.addCurrentIDPController import AddCurrentIDPController

MSG_ADDED = "Current IDP added successfully"
MSG_FIX_FIELDS = "Please fix the highlighted fields"
MSG_NO_CATEGORIES = "No IDP categories are available yet. Please try again later"
MSG_FAILED = "Current IDP could not be added. Please try again"


class AddCurrentIDPPage:
    def __init__(self):
        self.addCurrentIDPController = AddCurrentIDPController()
        self.idpData = {}
        self.fieldErrors = {}

    def checkAccess(self):
        if "userId" not in session:
            return redirect(url_for("interiorDesignerLogin"))
        if not self.addCurrentIDPController.canAddCurrentIDP(session["userId"]):
            return render_template("interiorDesignerAccessDenied.html"), 403
        return None

    def clickAddCurrentIDP(self):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        return self.displayAddForm()

    def displayAddForm(self, msg=None):
        categories = self.addCurrentIDPController.getActiveIDPCategories()
        if not categories and msg is None:
            msg = MSG_NO_CATEGORIES      # alt flow 2a - nothing to choose from yet (wireframe 4e)
        return render_template("addCurrentIDP.html", idpData=self.idpData, categories=categories,
                               fieldErrors=self.fieldErrors, errorMessage=msg, activePage="idps")

    def validateInput(self, idpData):
        self.fieldErrors = self.addCurrentIDPController.getFieldErrors(idpData)
        return len(self.fieldErrors) == 0

    def submitCurrentIDP(self, idpData):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        self.idpData = idpData
        if not self.validateInput(idpData):
            return self.displayErrorMessage(MSG_FIX_FIELDS)
        designerId = session["userId"]  # never accept ownership from a posted form field
        if self.addCurrentIDPController.addCurrentIDP(designerId, idpData):
            return self.displaySuccessMessage(MSG_ADDED)
        return self.displayErrorMessage(MSG_FAILED)

    def displaySuccessMessage(self, msg):
        flash(msg, "success")
        return redirect(url_for("interiorDesignerDashboard"))

    def displayErrorMessage(self, msg):
        return self.displayAddForm(msg)
