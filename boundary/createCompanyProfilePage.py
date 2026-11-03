# Boundary: CreateCompanyProfilePage - UC14 Create company profile (US14)
# templates: createCompanyProfile.html, interiorDesignerBase.html
# precondition: the designer is already logged in (US13), so there's no extra access check here

import re

from flask import flash, redirect, render_template, session, url_for

from control.createCompanyProfileController import CreateCompanyProfileController
from entity.companyProfile import CompanyProfile

MSG_CREATED = "Company profile created successfully"
MSG_FIX_FIELDS = "Please fix the highlighted fields"
MSG_EXISTS = "You already have a company profile"

FIELD_LIMITS = {"companyName": 100, "description": 2000, "services": 1000,
                "email": 254, "phone": 30, "address": 300}
REQUIRED_FIELDS = ("companyName", "description", "services")


# UC14 + UC16 - same field rules for create and update, so it lives out here and
# UpdateCompanyProfilePage imports it too
def getFieldErrors(companyProfile):
    # checks every field (required ones, max lengths, email format) and returns the errors
    errors = {}
    for field, limit in FIELD_LIMITS.items():
        value = getattr(companyProfile, field)
        if field in REQUIRED_FIELDS and not value:
            errors[field] = "This field is required"
        elif len(value) > limit:
            errors[field] = "Maximum " + str(limit) + " characters"
    if companyProfile.companyName and len(companyProfile.companyName) < 3:
        errors["companyName"] = "Company name must be 3-100 characters"
    if companyProfile.email and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", companyProfile.email):
        errors["email"] = "Enter a valid email address"
    return errors


class CreateCompanyProfilePage:
    # UC14 Create company profile
    # starts with an empty form and no errors
    def __init__(self):
        self.createCompanyProfileController = CreateCompanyProfileController()
        self.companyProfile = CompanyProfile()      # what's in the form (empty to start with)
        self.fieldErrors = {}

    # UC14 Create company profile
    # designer clicked Create - if they already have a company profile we show an error instead of the form
    def clickCreateCompanyProfile(self):
        if self.createCompanyProfileController.hasCompanyProfile(session["userId"]):
            return self.displayErrorMessage(MSG_EXISTS)
        return self.displayCreateForm()

    # UC14 Create company profile
    # shows the create form again, with whatever was typed and any errors
    def displayCreateForm(self, msg=None):
        return render_template("createCompanyProfile.html", company=self.companyProfile,
                               fieldErrors=self.fieldErrors, errorMessage=msg, activePage="company")

    # UC14 Create company profile
    # the page checks every field itself, true if there's nothing wrong
    def validateInput(self, companyProfile):
        self.fieldErrors = getFieldErrors(companyProfile)
        return len(self.fieldErrors) == 0

    # UC14 Create company profile
    # designer pressed Save - put the form into a CompanyProfile, check it, then just call create
    def submitCompanyProfile(self, companyName, description, services, email, phone, address):
        # owner always comes from the session, never from a posted form field.
        # spaces are trimmed here so the entity doesn't have to
        self.companyProfile = CompanyProfile(
            designerId=session["userId"], companyName=companyName.strip(),
            description=description.strip(), services=services.strip(),
            email=email.strip(), phone=phone.strip(), address=address.strip())

        if not self.validateInput(self.companyProfile):
            return self.displayErrorMessage(MSG_FIX_FIELDS)
        if self.createCompanyProfileController.createCompanyProfile(self.companyProfile):
            return self.displaySuccessMessage(MSG_CREATED)
        # the only way create fails is the entity finding they already have one
        return self.displayErrorMessage(MSG_EXISTS)

    # UC14 Create company profile
    # back to the dashboard with a green message
    def displaySuccessMessage(self, msg):
        flash(msg, "success")
        return redirect(url_for("interiorDesignerDashboard"))

    # UC14 Create company profile
    # stay on the form and show what went wrong
    def displayErrorMessage(self, msg):
        return self.displayCreateForm(msg)
