# Control: PlatformManagerLogoutController - UC40 Platform manager log out (US40)
# No entity is needed: logout changes the browser session, not account records.

from control.logoutController import LogoutController


class PlatformManagerLogoutController:
    # UC40 Platform manager log out
    # reuses the normal log out (US2) - True if a session was ended, False if it had already ended
    def logout(self):
        return LogoutController().logout()
