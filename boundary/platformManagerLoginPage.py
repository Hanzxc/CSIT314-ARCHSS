"""US39 Boundary. The Boundary delegates all entity access to the Control."""
from flask import redirect, render_template, session, url_for

from control.platformManagerLoginController import PlatformManagerLoginController

MSG_EMPTY_FIELDS = "Please enter your username and password"
MSG_INVALID_LOGIN = "Invalid login details or access unavailable"


class PlatformManagerLoginPage:
    def __init__(self):
        self.platformManagerLoginController = PlatformManagerLoginController()

    def openLoginPage(self):
        return self.displayLoginForm()

    def displayLoginForm(self):
        return render_template("platformManagerLogin.html")

    def validateInput(self, username, password):
        return bool(username and username.strip() and password)

    def submitLogin(self, username, password):
        if not self.validateInput(username, password):
            return self.displayErrorMessage(MSG_EMPTY_FIELDS)
        account = self.platformManagerLoginController.login(username, password)
        if account is None:
            return self.displayErrorMessage(MSG_INVALID_LOGIN)
        return self.redirectToDashboard(account)

    def redirectToDashboard(self, account):
        session.clear()
        session["userId"] = account.userId
        session["profileId"] = account.profileId
        session["username"] = account.username
        return redirect(url_for("platformManagerDashboard"))

    def displayErrorMessage(self, msg):
        return render_template("platformManagerLogin.html", errorMessage=msg)

    def openDashboard(self):
        userId = session.get("userId")
        if userId is None:
            return redirect(url_for("platformManagerLogin"))
        account = self.platformManagerLoginController.getAuthenticatedManager(userId)
        if account is None:
            return render_template("platformManagerAccessDenied.html"), 403
        return render_template("platformManagerDashboard.html", account=account)
