# Boundary: InteriorDesignerLoginPage - UC13 Interior designer log in (US13)
# handles the shared /login page when "Log in as" is Interior Designer - the dashboard borrows US15's and US17-R's
# controllers to pick the Company Profile button
# templates: login.html (shared with US1, US30, US39), interiorDesignerDashboard.html

from flask import redirect, render_template, session, url_for

from control.interiorDesignerLoginController import InteriorDesignerLoginController
from control.viewCompanyProfileController import ViewCompanyProfileController
from control.restoreCompanyProfileController import RestoreCompanyProfileController

MSG_EMPTY_FIELDS = "Please enter your username and password"
MSG_INVALID_LOGIN = "Invalid login details or access unavailable"


class InteriorDesignerLoginPage:
    # UC13 Interior designer log in
    # just sets up the controller
    def __init__(self):
        self.interiorDesignerLoginController = InteriorDesignerLoginController()

    # UC13 Interior designer log in
    # designer opened the login page
    def openLoginPage(self):
        return self.displayLoginForm()

    # UC13 Interior designer log in
    # shows the empty login form
    def displayLoginForm(self):
        return render_template("login.html", selectedRole="designer")

    # UT13.10 to UT13.13
    # both boxes have to be filled in (spaces only doesn't count)
    def validateInput(self, username, password):
        if not username.strip() or not password:
            return False
        return True

    # UC13 Interior designer log in
    # empty field -> the controller is never called (alt flow 4a)
    def submitLogin(self, username, password):
        if not self.validateInput(username, password):
            return self.displayErrorMessage(MSG_EMPTY_FIELDS)

        # the page trims the spaces from the username (not the password) before it calls login()
        account = self.interiorDesignerLoginController.login(username.strip(), password)
        if account is not None:
            return self.redirectToDashboard(account)
        return self.displayErrorMessage(MSG_INVALID_LOGIN)

    # UC13 Interior designer log in
    # login worked - start a fresh session for this designer and go to their dashboard
    def redirectToDashboard(self, account):
        session.clear()
        session["userId"] = account.userId
        session["profileId"] = account.profileId
        session["username"] = account.username
        return redirect(url_for("interiorDesignerDashboard"))

    # UC13 Interior designer log in
    # show the login form again with the error message
    def displayErrorMessage(self, msg):
        return render_template("login.html", errorMessage=msg, selectedRole="designer")

    # UC13 Interior designer log in
    # being logged in is checked by designerLoginRequired in app.py, so this just renders.
    # US15's controller says if there's an Active profile (View), US17-R's if there's a
    # deleted one (Restore) - otherwise the card shows Create
    def openDashboard(self):
        designerId = session["userId"]
        companyProfile = ViewCompanyProfileController().viewCompanyProfile(designerId)
        suspendedProfile = RestoreCompanyProfileController().getSuspendedCompanyProfile(designerId)
        return render_template("interiorDesignerDashboard.html", activePage="dashboard",
                               companyProfile=companyProfile, suspendedProfile=suspendedProfile)
