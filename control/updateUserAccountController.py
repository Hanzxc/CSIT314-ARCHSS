# Control: UpdateUserAccountController - UC10 Update user account (US10)

from entity.userAccount import UserAccount


class UpdateUserAccountController:
    # loads the current details into the form
    def getUserAccount(self, userId):
        return UserAccount().getUserAccount(userId)

    # UT10.1 to UT10.4
    # the page checks the input, the entity checks for duplicates - this just calls update.
    # comes back False if userId doesn't exist (UT10.4)
    def updateUserAccount(self, userId, username, fullName, email, phone, profileId):
        return UserAccount().updateUserAccount(userId, username, fullName, email, phone, profileId)
