# Control: CreateUserAccountController - UC8 Create user account (US8)

from entity.userAccount import UserAccount


class CreateUserAccountController:
    # UT8.1 to UT8.4
    # the page checks the input, the entity checks for duplicates - this just calls create
    def createUserAccount(self, username, password, fullName, email, phone, profileId):
        return UserAccount().createUserAccount(username, password, fullName, email, phone, profileId)
