# Control: PlatformManagerLogoutController - UC40 Platform manager log out (US40)
# no entity class needed, it only ends the session

from flask import session


class PlatformManagerLogoutController:
    # UT40.1 to UT40.4
    def logout(self):
        # True if a session was ended, False if there was no session left to end
        loggedOut = "userId" in session
        session.clear()     # removes the logged-in manager so the session can't be used again
        return loggedOut
