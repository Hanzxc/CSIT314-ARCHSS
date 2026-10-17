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
        loggedOut = self.logoutController.logout()
        if loggedOut:
            return self.displayLoginPage(MSG_LOGGED_OUT)
        return self.displayLoginPage(MSG_SESSION_ENDED)

    def displayLoginPage(self, msg):
        # green tick for a normal log out (wireframe 4b), blue info box if the session had already ended (4c)
        if msg == MSG_LOGGED_OUT:
            return render_template("login.html", successMessage=msg)
        return render_template("login.html", infoMessage=msg)
