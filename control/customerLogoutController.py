# Control: CustomerLogoutController - UC36 Customer log out (US36)
# no entity class needed, it only ends the session

from flask import session


class CustomerLogoutController:
    # UC36 Customer log out
    def logout(self):
        # True if a session was ended, False if there was no session left to end
        loggedOut = "userId" in session
        session.clear()     # removes the logged-in customer so the session can't be used again
        return loggedOut
