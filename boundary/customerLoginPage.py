"""US30 Boundary: validate input, delegate authentication and start a session."""
from flask import redirect, render_template, session, url_for

from control.customerLoginController import CustomerLoginController

MSG_EMPTY_FIELDS = "Please enter your username and password"
MSG_INVALID_LOGIN = "Invalid login details or access unavailable"


class CustomerLoginPage:
    def __init__(self):
        self.customerLoginController = CustomerLoginController()

    def openLoginPage(self):
        return self.displayLoginForm()

    def displayLoginForm(self):
        return render_template("customerLogin.html")

    def validateInput(self, username, password):
        return bool(username and username.strip() and password)

    def submitLogin(self, username, password):
        if not self.validateInput(username, password):
            return self.displayErrorMessage(MSG_EMPTY_FIELDS)
        account = self.customerLoginController.login(username, password)
        if account is None:
            return self.displayErrorMessage(MSG_INVALID_LOGIN)
        return self.redirectToDashboard(account)

    def redirectToDashboard(self, account):
        session.clear()
        session["userId"] = account.userId
        session["profileId"] = account.profileId
        session["username"] = account.username
        return redirect(url_for("customerDashboard"))

    def displayErrorMessage(self, msg):
        return render_template("customerLogin.html", errorMessage=msg)

    def openDashboard(self):
        userId = session.get("userId")
        if userId is None:
            return redirect(url_for("customerLogin"))
        account = self.customerLoginController.getAuthenticatedCustomer(userId)
        if account is None:
            return render_template("customerAccessDenied.html"), 403
        return render_template("customerDashboard.html", account=account,
                               activePage="dashboard")
