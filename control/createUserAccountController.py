# Control: CreateUserAccountController - UC8 Create user account (US8)
# the profile drop-down is US7's job, so the page borrows SearchUserProfileController for it

from entity.userAccount import UserAccount


class CreateUserAccountController:
    # UT8.1 to UT8.4
    # the page checks the input, the entity checks the database - this just calls create
    def createUserAccount(self, account):
        return UserAccount().createUserAccount(account)
