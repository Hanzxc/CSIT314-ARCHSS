"""US36 Boundary: end the session and return to customer login."""
from flask import flash, redirect, url_for

from control.customerLogoutController import CustomerLogoutController

MSG_LOGGED_OUT = "You have logged out successfully"
MSG_SESSION_ENDED = "Your session has already ended"


class CustomerLogoutPage:
    def __init__(self):
        self.customerLogoutController = CustomerLogoutController()

    def clickLogout(self):
        loggedOut = self.customerLogoutController.logout()
        return self.displayLoginPage(MSG_LOGGED_OUT if loggedOut else MSG_SESSION_ENDED)

    def displayLoginPage(self, msg):
        flash(msg, "success" if msg == MSG_LOGGED_OUT else "info")
        return redirect(url_for("customerLogin"))
