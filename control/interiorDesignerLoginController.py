"""US13: designer authentication and access checks using existing entities."""
from entity.userAccount import UserAccount
from entity.userProfile import UserProfile

REQUIRED_DESIGNER_PERMISSIONS = {"Manage company profile", "Manage own IDPs"}


class InteriorDesignerLoginController:
    def login(self, username, password):
        if not username or not username.strip() or not password:
            return None
        account = UserAccount().verifyCredentials(username, password)
        return account if self.isInteriorDesigner(account) else None

    def isInteriorDesigner(self, account):
        if account is None or not account.isActive():
            return False
        profile = UserProfile().getUserProfile(account.profileId)
        return (profile is not None and profile.isActive()
                and REQUIRED_DESIGNER_PERMISSIONS.issubset(profile.permissions))

    def getAuthenticatedDesigner(self, userId):
        account = UserAccount().getUserAccount(userId)
        return account if self.isInteriorDesigner(account) else None
