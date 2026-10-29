# Control: PlatformManagerLogoutController - UC40 Platform manager log out (US40)
# No entity is needed: logout changes the browser session, not account records.

from flask import session

from control.logoutController import LogoutController


class PlatformManagerLogoutController:
    # UT40.1 to UT40.3
    def logout(self):
        loggedOut = LogoutController().logout()
        # Also discard any leftover data if authentication has already ended.
        session.clear()
        return loggedOut
