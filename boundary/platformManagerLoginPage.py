# Boundary: PlatformManagerLoginPage - UC39 Platform manager log in (US39)
# handles the shared /login page when "Log in as" is Platform Manager
# templates: login.html (shared with US1, US13, US30), platformManagerDashboard.html

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
        return render_template("login.html", selectedRole="manager")

    # UT39.10 to UT39.13
    # both boxes have to be filled in (spaces only doesn't count)
    def validateInput(self, username, password):
        if not username.strip() or not password:
            return False
        return True

    # UC39 Platform manager log in
    # empty field -> the controller is never called (alt flow 4a)
    def submitLogin(self, username, password):
        if not self.validateInput(username, password):
            return self.displayErrorMessage(MSG_EMPTY_FIELDS)

        # the page trims the spaces from the username (not the password) before it calls login()
        account = self.platformManagerLoginController.login(username.strip(), password)
        if account is not None:
            return self.redirectToDashboard(account)
        return self.displayErrorMessage(MSG_INVALID_LOGIN)

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
        return render_template("login.html", errorMessage=msg, selectedRole="manager")

    # UC39 Platform manager log in
    # being logged in is checked by managerLoginRequired in app.py, so this just renders
    def openDashboard(self):
        return render_template("platformManagerDashboard.html")
