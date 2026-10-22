"""US39: manager authentication and access checks using existing entities."""
from entity.userAccount import UserAccount
from entity.userProfile import UserProfile

REQUIRED_MANAGER_PERMISSIONS = {"Manage IDP categories", "Generate reports"}


class PlatformManagerLoginController:
    def login(self, username, password):
        if not username or not username.strip() or not password:
            return None
        account = UserAccount().verifyCredentials(username, password)
        return account if self.isPlatformManager(account) else None

    def isPlatformManager(self, account):
        if account is None or not account.isActive():
            return False
        profile = UserProfile().getUserProfile(account.profileId)
        return (profile is not None and profile.isActive()
                and REQUIRED_MANAGER_PERMISSIONS.issubset(profile.permissions))

    def getAuthenticatedManager(self, userId):
        account = UserAccount().getUserAccount(userId)
        return account if self.isPlatformManager(account) else None
