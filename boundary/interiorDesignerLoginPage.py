# Boundary: InteriorDesignerLoginPage - UC13 Interior designer log in (US13)
"""US13 Boundary. The Boundary delegates all entity access to the Control."""
from flask import redirect, render_template, session, url_for

from control.interiorDesignerLoginController import InteriorDesignerLoginController
from control.createCompanyProfileController import CreateCompanyProfileController
from boundary.restoreCompanyProfilePage import RestoreCompanyProfilePage

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
        return render_template("interiorDesignerLogin.html")

    # UC13 Interior designer log in
    # both boxes have to be filled in (spaces only doesn't count)
    def validateInput(self, username, password):
        return bool(username and username.strip() and password)

    # UC13 Interior designer log in
    # check the boxes are filled, then ask the controller if this is a real active designer
    def submitLogin(self, username, password):
        if not self.validateInput(username, password):
            return self.displayErrorMessage(MSG_EMPTY_FIELDS)
        account = self.interiorDesignerLoginController.login(username, password)
        if account is None:
            return self.displayErrorMessage(MSG_INVALID_LOGIN)
        return self.redirectToDashboard(account)

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
        return render_template("interiorDesignerLogin.html", errorMessage=msg)

    # UC13 Interior designer log in
    # the designer dashboard - also shows Restore if their company profile was deleted
    def openDashboard(self):
        userId = session.get("userId")
        if userId is None:
            return redirect(url_for("interiorDesignerLogin"))
        account = self.interiorDesignerLoginController.getAuthenticatedDesigner(userId)
        if account is None:
            return render_template("interiorDesignerAccessDenied.html"), 403
        return render_template("interiorDesignerDashboard.html", account=account,
                               activePage="dashboard",
                               hasCompanyProfile=CreateCompanyProfileController().hasCompanyProfile(userId),
                               restoreToken=RestoreCompanyProfilePage().prepareRestore(userId))
