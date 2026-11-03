# Control: PlatformManagerLoginController - UC39 Platform manager log in (US39)
"""US39: manager authentication and access checks using existing entities."""
from entity.userAccount import UserAccount
from entity.userProfile import UserProfile

REQUIRED_MANAGER_PERMISSIONS = {"Manage IDP categories", "Generate reports"}


class PlatformManagerLoginController:
    # UC39 Platform manager log in
    # returns the account if the username/password is right AND it's an active platform manager, else None
    def login(self, username, password):
        # the page already made sure both boxes are filled in
        account = UserAccount().verifyCredentials(username, password)
        return account if self.isPlatformManager(account) else None

    # UC39 Platform manager log in
    # active account + active profile + the manager permissions = a platform manager
    def isPlatformManager(self, account):
        if account is None or not account.isActive():
            return False
        profile = UserProfile().getUserProfile(account.profileId)
        return (profile is not None and profile.isActive()
                and REQUIRED_MANAGER_PERMISSIONS.issubset(profile.permissions))

    # UC39 Platform manager log in
    # re-checks the logged-in user is still a platform manager
    def getAuthenticatedManager(self, userId):
        account = UserAccount().getUserAccount(userId)
        return account if self.isPlatformManager(account) else None
