# Boundary: PlatformManagerLoginPage - UC39 Platform manager log in (US39)
"""US39 Boundary. The Boundary delegates all entity access to the Control."""
from flask import redirect, render_template, session, url_for

from control.platformManagerLoginController import PlatformManagerLoginController

MSG_EMPTY_FIELDS = "Please enter your username and password"
MSG_INVALID_LOGIN = "Invalid login details or access unavailable"


class PlatformManagerLoginPage:
    # UC39 Platform manager log in
    # just sets up the controller
    def __init__(self):
        self.platformManagerLoginController = PlatformManagerLoginController()

    # UC39 Platform manager log in
    # manager opened the login page
    def openLoginPage(self):
        return self.displayLoginForm()

    # UC39 Platform manager log in
    # shows the empty login form
    def displayLoginForm(self):
        return render_template("platformManagerLogin.html")

    # UC39 Platform manager log in
    # both boxes have to be filled in (spaces only doesn't count)
    def validateInput(self, username, password):
        return bool(username and username.strip() and password)

    # UC39 Platform manager log in
    # check the boxes are filled, then ask the controller if this is a real active platform manager
    def submitLogin(self, username, password):
        if not self.validateInput(username, password):
            return self.displayErrorMessage(MSG_EMPTY_FIELDS)
        account = self.platformManagerLoginController.login(username, password)
        if account is None:
            return self.displayErrorMessage(MSG_INVALID_LOGIN)
        return self.redirectToDashboard(account)

    # UC39 Platform manager log in
    # login worked - start a fresh session for this manager and go to their dashboard
    def redirectToDashboard(self, account):
        session.clear()
        session["userId"] = account.userId
        session["profileId"] = account.profileId
        session["username"] = account.username
        return redirect(url_for("platformManagerDashboard"))

    # UC39 Platform manager log in
    # show the login form again with the error message
    def displayErrorMessage(self, msg):
        return render_template("platformManagerLogin.html", errorMessage=msg)

    # UC39 Platform manager log in
    # the platform manager dashboard - only shown if they're still an active manager
    def openDashboard(self):
        userId = session.get("userId")
        if userId is None:
            return redirect(url_for("platformManagerLogin"))
        account = self.platformManagerLoginController.getAuthenticatedManager(userId)
        if account is None:
            return render_template("platformManagerAccessDenied.html"), 403
        return render_template("platformManagerDashboard.html", account=account)
