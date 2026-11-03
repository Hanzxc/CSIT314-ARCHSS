# Boundary: LogoutPage - UC2 Log out (US2)
# the Log out button in the header of every admin page, goes back to templates/login.html

from flask import render_template

from control.logoutController import LogoutController

MSG_LOGGED_OUT = "You have logged out successfully"
MSG_SESSION_ENDED = "Your session has already ended"


class LogoutPage:
    # UC2 Log out
    # just sets up the controller
    def __init__(self):
        self.logoutController = LogoutController()

    # UC2 Log out
    # user clicked Log out - the message depends on whether they were still logged in
    def clickLogout(self):
        if self.logoutController.logout():
            return self.displayLoginPage(MSG_LOGGED_OUT)
        return self.displayLoginPage(MSG_SESSION_ENDED)

    def displayLoginPage(self, msg):
        # green tick for a normal log out (wireframe 4b), blue info box if the session had already ended (4c)
        if msg == MSG_LOGGED_OUT:
            return render_template("login.html", successMessage=msg)
        return render_template("login.html", infoMessage=msg)
