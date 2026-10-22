# Boundary: InteriorDesignerLogoutPage - UC19 Interior designer log out (US19)

from flask import flash, redirect, url_for

from control.interiorDesignerLogoutController import InteriorDesignerLogoutController

MSG_LOGGED_OUT = "You have logged out successfully"
MSG_SESSION_ENDED = "Your session has already ended"


class InteriorDesignerLogoutPage:
    def __init__(self):
        self.interiorDesignerLogoutController = InteriorDesignerLogoutController()

    def clickLogout(self):
        loggedOut = self.interiorDesignerLogoutController.logout()
        if loggedOut:
            return self.displayLoginPage(MSG_LOGGED_OUT)
        return self.displayLoginPage(MSG_SESSION_ENDED)

    def displayLoginPage(self, msg):
        flash(msg, "success" if msg == MSG_LOGGED_OUT else "info")
        return redirect(url_for("interiorDesignerLogin"))
