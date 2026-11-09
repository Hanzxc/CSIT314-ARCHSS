# Boundary: LoginPage - UC1 Log in (US1)
# /login is only for User Admins - designers, customers and platform managers use their own
# login pages (US13, US30, US39), so here they just get MSG_INVALID_LOGIN
# template: templates/login.html

from flask import render_template, redirect, url_for, session

from control.loginController import LoginController

MSG_EMPTY_FIELDS = "Please enter your username and password"
MSG_INVALID_LOGIN = "Invalid login details or account suspended"


class LoginPage:
    # UC1 Log in
    # just sets up the controller
    def __init__(self):
        self.loginController = LoginController()
        self.username = ""      # kept so the username stays in the box after a failed login (wireframe 4b)

    # UC1 Log in
    # user opened the login page
    def openLoginPage(self):
        return self.displayLoginForm()

    # UC1 Log in
    # shows the empty login form
    def displayLoginForm(self):
        return render_template("login.html")

    def submitLogin(self, username, password):
        self.username = username

        # empty field -> the controller is never called (alt flow 4a)
        if not self.validateInput(username, password):
            return self.displayErrorMessage(MSG_EMPTY_FIELDS)

        # the page trims the spaces from the username (not the password) before it calls login()
        self.username = username.strip()
        account = self.loginController.login(self.username, password)
        if account is not None:
            return self.redirectToDashboard(account)
        return self.displayErrorMessage(MSG_INVALID_LOGIN)

    # UT1.9, UT1.10
    def validateInput(self, username, password):
        if not username.strip() or not password:
            return False
        return True

    def redirectToDashboard(self, account):
        # start a fresh session for the User Admin, then open their dashboard
        session.clear()
        session["userId"] = account.userId
        session["profileId"] = account.profileId
        session["username"] = account.username
        return redirect(url_for("dashboard"))

    # UC1 Log in
    # show the login form again with the error message (the password box is cleared)
    def displayErrorMessage(self, msg):
        return render_template("login.html", errorMessage=msg, username=self.username)
