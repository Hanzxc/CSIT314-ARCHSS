"""US13 Boundary. The Boundary delegates all entity access to the Control."""
from flask import redirect, render_template, session, url_for

from control.interiorDesignerLoginController import InteriorDesignerLoginController
from control.createCompanyProfileController import CreateCompanyProfileController

MSG_EMPTY_FIELDS = "Please enter your username and password"
MSG_INVALID_LOGIN = "Invalid login details or access unavailable"


class InteriorDesignerLoginPage:
    def __init__(self):
        self.interiorDesignerLoginController = InteriorDesignerLoginController()

    def openLoginPage(self):
        return self.displayLoginForm()

    def displayLoginForm(self):
        return render_template("interiorDesignerLogin.html")

    def validateInput(self, username, password):
        return bool(username and username.strip() and password)

    def submitLogin(self, username, password):
        if not self.validateInput(username, password):
            return self.displayErrorMessage(MSG_EMPTY_FIELDS)
        account = self.interiorDesignerLoginController.login(username, password)
        if account is None:
            return self.displayErrorMessage(MSG_INVALID_LOGIN)
        return self.redirectToDashboard(account)

    def redirectToDashboard(self, account):
        session.clear()
        session["userId"] = account.userId
        session["profileId"] = account.profileId
        session["username"] = account.username
        return redirect(url_for("interiorDesignerDashboard"))

    def displayErrorMessage(self, msg):
        return render_template("interiorDesignerLogin.html", errorMessage=msg)

    def openDashboard(self):
        userId = session.get("userId")
        if userId is None:
            return redirect(url_for("interiorDesignerLogin"))
        account = self.interiorDesignerLoginController.getAuthenticatedDesigner(userId)
        if account is None:
            return render_template("interiorDesignerAccessDenied.html"), 403
        return render_template("interiorDesignerDashboard.html", account=account,
                               activePage="dashboard",
                               hasCompanyProfile=CreateCompanyProfileController().hasCompanyProfile(userId))
