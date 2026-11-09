# Boundary: PlatformManagerLogoutPage - UC40 Platform manager log out (US40)

from flask import flash, redirect, url_for

from control.platformManagerLogoutController import PlatformManagerLogoutController

MSG_LOGGED_OUT = "You have logged out successfully"
MSG_SESSION_ENDED = "Your session has already ended"


class PlatformManagerLogoutPage:
    # UC40 Platform manager log out
    # just sets up the controller
    def __init__(self):
        self.platformManagerLogoutController = PlatformManagerLogoutController()

    # UC40 Platform manager log out
    # manager clicked Log out - the message depends on whether they were still logged in
    def clickLogout(self):
        loggedOut = self.platformManagerLogoutController.logout()
        if loggedOut:
            return self.displayLoginPage(MSG_LOGGED_OUT)
        return self.displayLoginPage(MSG_SESSION_ENDED)

    # UC40 Platform manager log out
    # back to the manager login page with the message (wireframes 4b, 4c)
    def displayLoginPage(self, msg):
        flash(msg, "success" if msg == MSG_LOGGED_OUT else "info")
        return redirect(url_for("platformManagerLogin"))
