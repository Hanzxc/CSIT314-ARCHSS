# Control: InteriorDesignerLogoutController - UC19 Interior designer log out (US19)
# No entity is needed: logout changes the browser session, not company/account records.

from flask import session

from control.logoutController import LogoutController


class InteriorDesignerLogoutController:
    def logout(self):
        loggedOut = LogoutController().logout()
        # Also discard orphaned data if authentication has already ended.
        session.clear()
        return loggedOut
