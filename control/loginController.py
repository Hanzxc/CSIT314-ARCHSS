# Control: LoginController - UC1 Log in (US1)

from entity.userAccount import UserAccount
from entity.userProfile import UserProfile


class LoginController:
    # UT1.6 to UT1.8, UT6.6
    def login(self, username, password):
        # TODO (sequence diagram msgs 6-14):
        # - account = UserAccount().verifyCredentials(username, password)
        # - if account is not None:
        #       accountActive = account.isActive()
        #       profile = UserProfile().getUserProfile(account.profileId)
        #       profileActive = profile.isActive()
        #       if the account OR its profile is suspended -> account = None
        # - return account   (UserAccount, or None if login not allowed)
        pass
