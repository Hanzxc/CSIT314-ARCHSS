# Boundary: PlatformManagerLogoutPage - UC40 Platform manager log out (US40)

from flask import flash, redirect, url_for

from control.platformManagerLogoutController import PlatformManagerLogoutController

MSG_LOGGED_OUT = "You have logged out successfully"
MSG_SESSION_ENDED = "Your session has already ended"


class PlatformManagerLogoutPage:
    def __init__(self):
        self.platformManagerLogoutController = PlatformManagerLogoutController()

    def clickLogout(self):
        loggedOut = self.platformManagerLogoutController.logout()
        if loggedOut:
            return self.displayLoginPage(MSG_LOGGED_OUT)
        return self.displayLoginPage(MSG_SESSION_ENDED)

    def displayLoginPage(self, msg):
        # platformManagerLogin.html already shows flashed messages (wireframes 4b, 4c)
        flash(msg, "success" if msg == MSG_LOGGED_OUT else "info")
        return redirect(url_for("platformManagerLogin"))
