# Control: ViewUserAccountController - UC9 View user account (US9)
# the account's profile (group name) is fetched by the page through US4's ViewUserProfileController

from entity.userAccount import UserAccount


class ViewUserAccountController:
    # UT9.1 to UT9.4
    # just passes it through, gives None back if the id doesn't exist (US11 borrows it too)
    def viewUserAccount(self, userId):
        return UserAccount().getUserAccount(userId)
