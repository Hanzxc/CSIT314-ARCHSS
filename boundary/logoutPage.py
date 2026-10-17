# Boundary: LogoutPage - UC2 Log out (US2)
# the Log out button in the header of every admin page, goes back to templates/login.html

from flask import render_template

from control.logoutController import LogoutController

MSG_LOGGED_OUT = "You have logged out successfully"
MSG_SESSION_ENDED = "Your session has already ended"


class LogoutPage:
    def __init__(self):
        self.logoutController = LogoutController()

    def clickLogout(self):
        # TODO:
        # - loggedOut = self.logoutController.logout()
        # - loggedOut True  -> return self.displayLoginPage(MSG_LOGGED_OUT)
        # - loggedOut False -> return self.displayLoginPage(MSG_SESSION_ENDED)
        pass

    def displayLoginPage(self, msg):
        # TODO: return render_template("login.html", successMessage=msg)
        pass
