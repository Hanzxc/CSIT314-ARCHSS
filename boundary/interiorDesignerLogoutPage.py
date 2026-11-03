# Boundary: InteriorDesignerLogoutPage - UC19 Interior designer log out (US19)

from flask import flash, redirect, url_for

from control.interiorDesignerLogoutController import InteriorDesignerLogoutController

MSG_LOGGED_OUT = "You have logged out successfully"
MSG_SESSION_ENDED = "Your session has already ended"


class InteriorDesignerLogoutPage:
    # UC19 Interior designer log out
    # just sets up the controller
    def __init__(self):
        self.interiorDesignerLogoutController = InteriorDesignerLogoutController()

    # UC19 Interior designer log out
    # designer clicked Log out - the message depends on whether they were still logged in
    def clickLogout(self):
        if self.interiorDesignerLogoutController.logout():
            return self.displayLoginPage(MSG_LOGGED_OUT)
        return self.displayLoginPage(MSG_SESSION_ENDED)

    # UC19 Interior designer log out
    # back to the designer login page with the message
    def displayLoginPage(self, msg):
        flash(msg, "success" if msg == MSG_LOGGED_OUT else "info")
        return redirect(url_for("interiorDesignerLogin"))
