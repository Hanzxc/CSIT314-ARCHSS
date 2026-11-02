# Boundary: CreateCompanyProfilePage - UC14 Create company profile (US14)
# templates: createCompanyProfile.html, interiorDesignerBase.html

from flask import flash, redirect, render_template, session, url_for

from control.createCompanyProfileController import CreateCompanyProfileController

MSG_CREATED = "Company profile created successfully"
MSG_FIX_FIELDS = "Please fix the highlighted fields"
MSG_EXISTS = "You already have a company profile"
MSG_FAILED = "Company profile could not be created. Please try again"


class CreateCompanyProfilePage:
    # UC14 Create company profile
    # starts with an empty form and no errors
    def __init__(self):
        self.createCompanyProfileController = CreateCompanyProfileController()
        self.companyData = {}
        self.fieldErrors = {}

    # UC14 Create company profile
    # not logged in -> back to the designer login, not a designer -> access denied page
    def checkAccess(self):
        if "userId" not in session:
            return redirect(url_for("interiorDesignerLogin"))
        if not self.createCompanyProfileController.canCreateCompanyProfile(session["userId"]):
            return render_template("interiorDesignerAccessDenied.html"), 403
        return None

    # UC14 Create company profile
    # designer clicked Create - if they already have a company profile we show an error instead of the form
    def clickCreateCompanyProfile(self):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        if self.createCompanyProfileController.hasCompanyProfile(session["userId"]):
            return self.displayErrorMessage(MSG_EXISTS)
        return self.displayCreateForm()

    # UC14 Create company profile
    # shows the create form again, with whatever was typed and any errors
    def displayCreateForm(self, msg=None):
        return render_template("createCompanyProfile.html", companyData=self.companyData,
                               fieldErrors=self.fieldErrors, errorMessage=msg, activePage="company")

    # UC14 Create company profile
    # asks the controller which fields are wrong, true if there are none
    def validateInput(self, companyData):
        self.fieldErrors = self.createCompanyProfileController.getFieldErrors(companyData)
        return len(self.fieldErrors) == 0

    # UC14 Create company profile
    # designer pressed Save - check the input, then save it under the logged-in designer
    def submitCompanyProfile(self, companyData):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        self.companyData = companyData
        if not self.validateInput(companyData):
            return self.displayErrorMessage(MSG_FIX_FIELDS)
        designerId = session["userId"]  # never accept ownership from a posted form field
        if self.createCompanyProfileController.createCompanyProfile(designerId, companyData):
            return self.displaySuccessMessage(MSG_CREATED)
        if self.createCompanyProfileController.hasCompanyProfile(designerId):
            return self.displayErrorMessage(MSG_EXISTS)
        return self.displayErrorMessage(MSG_FAILED)

    # UC14 Create company profile
    # back to the dashboard with a green message
    def displaySuccessMessage(self, msg):
        flash(msg, "success")
        return redirect(url_for("interiorDesignerDashboard"))

    # UC14 Create company profile
    # stay on the form and show what went wrong
    def displayErrorMessage(self, msg):
        return self.displayCreateForm(msg)
