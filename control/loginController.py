# Control: LoginController - UC1 Log in (US1)

from entity.userAccount import UserAccount
from entity.userProfile import UserProfile


class LoginController:
    # UT1.6 to UT1.8, UT6.6
    def login(self, username, password):
        # returns the UserAccount, or None if the login isn't allowed
        account = UserAccount().verifyCredentials(username, password)

        if account is not None:
            accountActive = account.isActive()
            profile = UserProfile().getUserProfile(account.profileId)
            profileActive = profile is not None and profile.isActive()

            # if the account OR its profile is suspended, don't let them in
            if not accountActive or not profileActive:
                account = None

        return account
