# Boundary: CustomerLoginPage - UC30 Customer log in (US30)
# handles the shared /login page when "Log in as" is Customer
# templates: login.html (shared with US1, US13, US39), customerDashboard.html

from flask import redirect, render_template, session, url_for

from control.customerLoginController import CustomerLoginController

MSG_EMPTY_FIELDS = "Please enter your username and password"
MSG_INVALID_LOGIN = "Invalid login details or access unavailable"


class CustomerLoginPage:
    # UC30 Customer log in
    # just sets up the controller
    def __init__(self):
        self.customerLoginController = CustomerLoginController()

    # UC30 Customer log in
    # customer opened the login page
    def openLoginPage(self):
        return self.displayLoginForm()

    # UC30 Customer log in
    # shows the empty login form
    def displayLoginForm(self):
        return render_template("login.html", selectedRole="customer")

    # UT30.12
    # both boxes have to be filled in (spaces only doesn't count)
    def validateInput(self, username, password):
        if not username or not username.strip() or not password:
            return False
        return True

    # UC30 Customer log in
    # empty field -> the controller is never called (alt flow)
    def submitLogin(self, username, password):
        if not self.validateInput(username, password):
            return self.displayErrorMessage(MSG_EMPTY_FIELDS)

        # the page trims the spaces from the username (not the password) before it calls login()
        username = username.strip()
        account = self.customerLoginController.login(username, password)
        if account is not None:
            return self.redirectToDashboard(account)
        return self.displayErrorMessage(MSG_INVALID_LOGIN)

    # UC30 Customer log in
    # login worked - start a fresh session for this customer and go to their dashboard
    def redirectToDashboard(self, account):
        session.clear()
        session["userId"] = account.userId
        session["profileId"] = account.profileId
        session["username"] = account.username
        return redirect(url_for("customerDashboard"))

    # UC30 Customer log in
    # show the login form again with the error message
    def displayErrorMessage(self, msg):
        return render_template("login.html", errorMessage=msg, selectedRole="customer")

    # UC30 Customer log in
    # being logged in is checked by customerLoginRequired in app.py, so this just renders.
    # the welcome line uses the username from the session - the account isn't loaded again
    def openDashboard(self):
        return render_template("customerDashboard.html", username=session["username"],
                               activePage="dashboard")
