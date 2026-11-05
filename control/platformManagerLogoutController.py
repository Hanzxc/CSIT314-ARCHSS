# Control: PlatformManagerLogoutController - UC40 Platform manager log out (US40)
# No entity is needed: logout changes the browser session, not account records.

from flask import session

from control.logoutController import LogoutController


class PlatformManagerLogoutController:
    # UC40 Platform manager log out
    # reuses the normal log out (US2), then clears anything left in the session
    def logout(self):
        loggedOut = LogoutController().logout()
        # Also discard orphaned data if authentication has already ended.
        session.clear()
        return loggedOut
