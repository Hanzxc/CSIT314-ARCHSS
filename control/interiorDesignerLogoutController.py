# Control: InteriorDesignerLogoutController - UC19 Interior designer log out (US19)
# no entity class needed, it only ends the session

from flask import session


class InteriorDesignerLogoutController:
    # UT19.1 to UT19.5
    def logout(self):
        # True if a session was ended, False if there was no session left to end
        loggedOut = "userId" in session
        session.clear()     # removes the logged-in designer so the session can't be used again
        return loggedOut
