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
    # UC16 Update company profile
    # starts with an empty form and no errors
    def __init__(self):
        self.updateCompanyProfileController = UpdateCompanyProfileController()
        self.companyData = {}
        self.fieldErrors = {}

    # UC16 Update company profile
    # not logged in -> back to the designer login, not a designer -> access denied page
    def checkAccess(self):
        if "userId" not in session:
            return redirect(url_for("interiorDesignerLogin"))
        if not self.updateCompanyProfileController.canUpdateCompanyProfile(session["userId"]):
            return render_template("interiorDesignerAccessDenied.html"), 403
        return None

    # UC16 Update company profile
    # designer clicked Update - fill the form with their current company details
    def clickUpdate(self):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        profile = self.updateCompanyProfileController.getCompanyProfile(session["userId"])
        if profile is None:
            return self.displayNotFoundMessage()
        self.companyData = {field: getattr(profile, field) for field in FORM_FIELDS}
        return self.displayUpdateForm()

    # UC16 Update company profile
    # shows the update form, with what was typed and any errors
    def displayUpdateForm(self, msg=None):
        return render_template("updateCompanyProfile.html", companyData=self.companyData,
                               fieldErrors=self.fieldErrors, errorMessage=msg, activePage="company")

    # UC16 Update company profile
    # asks the controller which fields are wrong, true if there are none
    def validateInput(self, companyData):
        self.fieldErrors = self.updateCompanyProfileController.getFieldErrors(companyData)
        return len(self.fieldErrors) == 0

    # UC16 Update company profile
    # designer pressed Save - check the input, then save it for the logged-in designer only
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

    # UC16 Update company profile
    # back to the company profile with a green message
    def displaySuccessMessage(self, msg):
        flash(msg, "success")
        return redirect(url_for("viewCompanyProfile"))

    # UC16 Update company profile
    # stay on the form and show what went wrong
    def displayErrorMessage(self, msg):
        return self.displayUpdateForm(msg)

    # UC16 Update company profile
    # shows the "no company profile" page (404) when there's nothing to show
    def displayNotFoundMessage(self):
        return render_template("companyProfileNotFound.html", errorMessage=MSG_NOT_FOUND,
                               activePage="company"), 404
