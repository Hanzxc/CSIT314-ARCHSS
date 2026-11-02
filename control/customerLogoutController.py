"""US36: end the current browser session without querying account records."""
from flask import session

from control.logoutController import LogoutController


class CustomerLogoutController:
    def logout(self):
        loggedOut = LogoutController().logout()
        # Discard orphaned session data even when authentication has already ended.
        session.clear()
        return loggedOut
