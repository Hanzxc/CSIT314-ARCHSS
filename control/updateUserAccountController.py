# Control: UpdateUserAccountController - UC10 Update user account (US10)
# the profile drop-down is US7's job, so the page borrows SearchUserProfileController for it

from entity.userAccount import UserAccount


class UpdateUserAccountController:
    # US10's own loader - gets the current details for the form
    def getUserAccount(self, userId):
        return UserAccount().getUserAccount(userId)

    # UT10.1 to UT10.4
    # the page checks the input, the entity checks the database - this just calls update.
    # comes back False if the account is suspended or doesn't exist (UT10.4, UT10.15)
    def updateUserAccount(self, account):
        return UserAccount().updateUserAccount(account)
