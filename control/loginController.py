# Control: LoginController - UC1 Log in (US1)

from entity.userAccount import UserAccount

# /login is only for User Admins - the other roles log in on their own pages (US13, US30, US39)
REQUIRED_ADMIN_PERMISSIONS = {"Manage user accounts", "Manage user profiles"}


class LoginController:
    # UT1.6 to UT1.8, UT1.11
    # returns the UserAccount, or None if the login isn't allowed - the entity does every check
    def login(self, username, password):
        return UserAccount().verifyCredentials(username, password, REQUIRED_ADMIN_PERMISSIONS)
