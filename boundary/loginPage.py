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
        # TODO: return self.displayLoginForm()
        pass

    def displayLoginForm(self):
        # TODO: return render_template("login.html")
        pass

    def submitLogin(self, username, password):
        # TODO (sequence diagram msgs 4-19):
        # - if not self.validateInput(...) -> return self.displayErrorMessage(MSG_EMPTY_FIELDS)
        # - account = self.loginController.login(username, password)
        # - account not None -> return self.redirectToDashboard(account)
        # - account is None  -> return self.displayErrorMessage(MSG_INVALID_LOGIN)
        pass

    # UT1.9, UT1.10
    def validateInput(self, username, password):
        # TODO: return False if username or password is empty, else True
        pass

    def redirectToDashboard(self, account):
        # TODO:
        # - session["userId"] = account.userId
        # - session["profileId"] = account.profileId
        # - return redirect(url_for("dashboard"))
        pass

    def displayErrorMessage(self, msg):
        # TODO: return render_template("login.html", errorMessage=msg)
        pass
