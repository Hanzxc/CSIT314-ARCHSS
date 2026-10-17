# Control: LogoutController - UC2 Log out (US2)
# no entity class needed, it only ends the session

from flask import session


class LogoutController:
    # UT2.1 to UT2.3
    def logout(self):
        # TODO:
        # - if "userId" is in session -> session.clear(), loggedOut = True
        # - else (session already ended) -> loggedOut = False
        # - return loggedOut
        pass
