# Boundary: ViewCompanyProfilePage - UC15 View company profile (US15)
# templates: viewCompanyProfile.html, companyProfileNotFound.html
# precondition: the designer is already logged in (US13), so there's no extra access check here

from flask import render_template, session

from control.viewCompanyProfileController import ViewCompanyProfileController

MSG_NOT_FOUND = "You have not created a company profile yet"


class ViewCompanyProfilePage:
    # UC15 View company profile
    # just sets up the controller
    def __init__(self):
        self.viewCompanyProfileController = ViewCompanyProfileController()

    # UC15 View company profile
    # designer opened their company profile
    def clickView(self):
        # No companyId/designerId from the URL: the logged-in user owns the lookup.
        profile = self.viewCompanyProfileController.viewCompanyProfile(session["userId"])
        if profile is None:
            return self.displayErrorMessage(MSG_NOT_FOUND)
        return self.displayCompanyProfile(profile)

    # UC15 View company profile
    # shows all the company details
    def displayCompanyProfile(self, profile):
        return render_template("viewCompanyProfile.html", company=profile, activePage="company")

    # UC15 View company profile
    # shows the "no company profile" page (404) when there's nothing to show
    def displayErrorMessage(self, msg):
        return render_template("companyProfileNotFound.html", errorMessage=msg, activePage="company"), 404
