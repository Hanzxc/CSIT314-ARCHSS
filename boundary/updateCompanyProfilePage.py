# Boundary: UpdateCompanyProfilePage - UC16 Update company profile (US16)
# templates: updateCompanyProfile.html, companyProfileNotFound.html
# precondition: the designer is already logged in (US13), so there's no extra access check here

from flask import flash, redirect, render_template, session, url_for

from boundary.createCompanyProfilePage import getFieldErrors
from control.updateCompanyProfileController import UpdateCompanyProfileController
from entity.companyProfile import CompanyProfile

MSG_UPDATED = "Company profile updated successfully"
MSG_FIX_FIELDS = "Please fix the highlighted fields"
MSG_NOT_FOUND = "You have not created a company profile yet"


class UpdateCompanyProfilePage:
    # UC16 Update company profile
    # starts with an empty form and no errors
    def __init__(self):
        self.updateCompanyProfileController = UpdateCompanyProfileController()
        self.companyProfile = CompanyProfile()      # what's in the form
        self.fieldErrors = {}

    # UC16 Update company profile
    # designer clicked Update - fill the form with their current company details
    def clickUpdate(self):
        profile = self.updateCompanyProfileController.getCompanyProfile(session["userId"])
        if profile is None:
            return self.displayNotFoundMessage()
        self.companyProfile = profile
        return self.displayUpdateForm()

    # UC16 Update company profile
    # shows the update form, with what was typed and any errors
    def displayUpdateForm(self, msg=None):
        return render_template("updateCompanyProfile.html", company=self.companyProfile,
                               fieldErrors=self.fieldErrors, errorMessage=msg, activePage="company")

    # UC16 Update company profile
    # same field rules as US14, true if there's nothing wrong
    def validateInput(self, companyProfile):
        self.fieldErrors = getFieldErrors(companyProfile)
        return len(self.fieldErrors) == 0

    # UC16 Update company profile
    # designer pressed Save - put the form into a CompanyProfile, check it, then just call update
    def submitUpdate(self, companyName, description, services, email, phone, address):
        # submitted owner IDs never control which profile changes - it's always the session's
        self.companyProfile = CompanyProfile(
            designerId=session["userId"], companyName=companyName.strip(),
            description=description.strip(), services=services.strip(),
            email=email.strip(), phone=phone.strip(), address=address.strip())

        if not self.validateInput(self.companyProfile):
            return self.displayErrorMessage(MSG_FIX_FIELDS)
        if self.updateCompanyProfileController.updateCompanyProfile(self.companyProfile):
            return self.displaySuccessMessage(MSG_UPDATED)
        # the only way update fails is no Active profile to change
        return self.displayNotFoundMessage()

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
