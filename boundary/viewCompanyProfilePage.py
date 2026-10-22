# Boundary: ViewCompanyProfilePage - UC15 View company profile (US15)
# templates: viewCompanyProfile.html, companyProfileNotFound.html

from flask import redirect, render_template, session, url_for

from control.viewCompanyProfileController import ViewCompanyProfileController

MSG_NOT_FOUND = "You have not created a company profile yet"


class ViewCompanyProfilePage:
    def __init__(self):
        self.viewCompanyProfileController = ViewCompanyProfileController()

    def checkAccess(self):
        if "userId" not in session:
            return redirect(url_for("interiorDesignerLogin"))
        if not self.viewCompanyProfileController.canViewCompanyProfile(session["userId"]):
            return render_template("interiorDesignerAccessDenied.html"), 403
        return None

    def clickView(self):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        # No companyId/designerId from the URL: the logged-in user owns the lookup.
        profile = self.viewCompanyProfileController.viewCompanyProfile(session["userId"])
        if profile is None:
            return self.displayErrorMessage(MSG_NOT_FOUND)
        return self.displayCompanyProfile(profile)

    def displayCompanyProfile(self, profile):
        return render_template("viewCompanyProfile.html", company=profile, activePage="company")

    def displayErrorMessage(self, msg):
        return render_template("companyProfileNotFound.html", errorMessage=msg, activePage="company"), 404
