# Control: PlatformManagerLoginController - UC39 Platform manager log in (US39)

from entity.userAccount import UserAccount

# /manager/login is only for platform managers - the profile needs both of these
REQUIRED_MANAGER_PERMISSIONS = {"Manage IDP categories", "Generate reports"}


class PlatformManagerLoginController:
    # UT39.1 to UT39.8
    # returns the UserAccount, or None if the login isn't allowed - the entity does every check
    def login(self, username, password):
        return UserAccount().verifyCredentials(username, password, REQUIRED_MANAGER_PERMISSIONS)
