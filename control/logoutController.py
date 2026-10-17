# Control: LogoutController - UC2 Log out (US2)
# no entity class needed, it only ends the session

from flask import session


class LogoutController:
    # UT2.1 to UT2.3
    def logout(self):
        # True if a session was ended, False if there was no session left to end
        if "userId" in session:
            session.clear()     # removes the logged-in user so the session can't be used again
            loggedOut = True
        else:
            loggedOut = False
        return loggedOut
