# Boundary: CustomerLogoutPage - UC36 Customer log out (US36)
# the Log out button is in the header of every customer page (templates/customerBase.html)

from flask import flash, redirect, url_for

from control.customerLogoutController import CustomerLogoutController

MSG_LOGGED_OUT = "You have logged out successfully"
MSG_SESSION_ENDED = "Your session has already ended"


class CustomerLogoutPage:
    # UC36 Customer log out
    # just sets up the controller
    def __init__(self):
        self.customerLogoutController = CustomerLogoutController()

    # UC36 Customer log out
    # customer clicked Log out - the message depends on whether they were still logged in
    def clickLogout(self):
        loggedOut = self.customerLogoutController.logout()
        if loggedOut:
            return self.displayLoginPage(MSG_LOGGED_OUT)
        return self.displayLoginPage(MSG_SESSION_ENDED)

    # UC36 Customer log out
    # back to the customer login page with the message
    def displayLoginPage(self, msg):
        flash(msg, "success" if msg == MSG_LOGGED_OUT else "info")
        return redirect(url_for("customerLogin"))
