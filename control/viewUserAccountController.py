# Control: ViewUserAccountController - UC9 View user account (US9)

from entity.userAccount import UserAccount
from entity.userProfile import UserProfile


class ViewUserAccountController:
    def __init__(self):
        # the seq diagram sends back the account AND its profile (msgs 7, 8).
        # viewUserAccount() returns the account (UT9.1) and leaves the profile here for the page
        self.profile = None

    # UT9.1 to UT9.4
    def viewUserAccount(self, userId):
        self.profile = None
        account = UserAccount().getUserAccount(userId)

        # alt box - only look up the group if the account is really there (msgs 5, 6)
        if account is not None:
            self.profile = UserProfile().getUserProfile(account.profileId)
        return account
