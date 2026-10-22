# Boundary: CreateCompanyProfilePage - UC14 Create company profile (US14)
# templates: createCompanyProfile.html, interiorDesignerBase.html

from flask import flash, redirect, render_template, session, url_for

from control.createCompanyProfileController import CreateCompanyProfileController

MSG_CREATED = "Company profile created successfully"
MSG_FIX_FIELDS = "Please fix the highlighted fields"
MSG_EXISTS = "You already have a company profile"
MSG_FAILED = "Company profile could not be created. Please try again"


class CreateCompanyProfilePage:
    def __init__(self):
        self.createCompanyProfileController = CreateCompanyProfileController()
        self.companyData = {}
        self.fieldErrors = {}

    def checkAccess(self):
        if "userId" not in session:
            return redirect(url_for("interiorDesignerLogin"))
        if not self.createCompanyProfileController.canCreateCompanyProfile(session["userId"]):
            return render_template("interiorDesignerAccessDenied.html"), 403
        return None

    def clickCreateCompanyProfile(self):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        if self.createCompanyProfileController.hasCompanyProfile(session["userId"]):
            return self.displayErrorMessage(MSG_EXISTS)
        return self.displayCreateForm()

    def displayCreateForm(self, msg=None):
        return render_template("createCompanyProfile.html", companyData=self.companyData,
                               fieldErrors=self.fieldErrors, errorMessage=msg, activePage="company")

    def validateInput(self, companyData):
        self.fieldErrors = self.createCompanyProfileController.getFieldErrors(companyData)
        return len(self.fieldErrors) == 0

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

    def displaySuccessMessage(self, msg):
        flash(msg, "success")
        return redirect(url_for("interiorDesignerDashboard"))

    def displayErrorMessage(self, msg):
        return self.displayCreateForm(msg)
