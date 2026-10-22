# Boundary: UpdateCompanyProfilePage - UC16 Update company profile (US16)
# templates: updateCompanyProfile.html, companyProfileNotFound.html

from flask import flash, redirect, render_template, session, url_for

from control.updateCompanyProfileController import UpdateCompanyProfileController

MSG_UPDATED = "Company profile updated successfully"
MSG_FIX_FIELDS = "Please fix the highlighted fields"
MSG_NOT_FOUND = "You have not created a company profile yet"
MSG_FAILED = "Company profile could not be updated. Please try again"
FORM_FIELDS = ("companyName", "description", "services", "email", "phone", "address")


class UpdateCompanyProfilePage:
    def __init__(self):
        self.updateCompanyProfileController = UpdateCompanyProfileController()
        self.companyData = {}
        self.fieldErrors = {}

    def checkAccess(self):
        if "userId" not in session:
            return redirect(url_for("interiorDesignerLogin"))
        if not self.updateCompanyProfileController.canUpdateCompanyProfile(session["userId"]):
            return render_template("interiorDesignerAccessDenied.html"), 403
        return None

    def clickUpdate(self):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        profile = self.updateCompanyProfileController.getCompanyProfile(session["userId"])
        if profile is None:
            return self.displayNotFoundMessage()
        self.companyData = {field: getattr(profile, field) for field in FORM_FIELDS}
        return self.displayUpdateForm()

    def displayUpdateForm(self, msg=None):
        return render_template("updateCompanyProfile.html", companyData=self.companyData,
                               fieldErrors=self.fieldErrors, errorMessage=msg, activePage="company")

    def validateInput(self, companyData):
        self.fieldErrors = self.updateCompanyProfileController.getFieldErrors(companyData)
        return len(self.fieldErrors) == 0

    def submitUpdate(self, companyData):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        self.companyData = companyData
        if not self.validateInput(companyData):
            return self.displayErrorMessage(MSG_FIX_FIELDS)
        designerId = session["userId"]  # submitted owner IDs never control which profile changes
        if self.updateCompanyProfileController.updateCompanyProfile(designerId, companyData):
            return self.displaySuccessMessage(MSG_UPDATED)
        if self.updateCompanyProfileController.getCompanyProfile(designerId) is None:
            return self.displayNotFoundMessage()
        return self.displayErrorMessage(MSG_FAILED)

    def displaySuccessMessage(self, msg):
        flash(msg, "success")
        return redirect(url_for("viewCompanyProfile"))

    def displayErrorMessage(self, msg):
        return self.displayUpdateForm(msg)

    def displayNotFoundMessage(self):
        return render_template("companyProfileNotFound.html", errorMessage=MSG_NOT_FOUND,
                               activePage="company"), 404
