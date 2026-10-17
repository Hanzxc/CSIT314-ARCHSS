# Boundary: LoginPage - UC1 Log in (US1)
# template: templates/login.html

from flask import render_template, redirect, url_for, session

from control.loginController import LoginController

MSG_EMPTY_FIELDS = "Please enter your username and password"
MSG_INVALID_LOGIN = "Invalid login details or account suspended"   # same msg for every failed login


class LoginPage:
    def __init__(self):
        self.loginController = LoginController()

    def openLoginPage(self):
        return self.displayLoginForm()

    def displayLoginForm(self):
        return render_template("login.html")

    def submitLogin(self, username, password):
        # empty field -> the controller is never called (alt flow 4a)
        if not self.validateInput(username, password):
            return self.displayErrorMessage(MSG_EMPTY_FIELDS)

        account = self.loginController.login(username, password)
        if account is not None:
            return self.redirectToDashboard(account)
        return self.displayErrorMessage(MSG_INVALID_LOGIN)

    # UT1.9, UT1.10
    def validateInput(self, username, password):
        if not username.strip() or not password:
            return False
        return True

    def redirectToDashboard(self, account):
        # start the session - other pages read the logged-in user from here
        session["userId"] = account.userId
        session["profileId"] = account.profileId
        session["username"] = account.username
        return redirect(url_for("dashboard"))

    def displayErrorMessage(self, msg):
        return render_template("login.html", errorMessage=msg)
