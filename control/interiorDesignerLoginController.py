# Control: InteriorDesignerLoginController - UC13 Interior designer log in (US13)

from entity.userAccount import UserAccount
from entity.userProfile import UserProfile

# /designer/login is only for interior designers - the profile needs both of these
REQUIRED_DESIGNER_PERMISSIONS = {"Manage company profile", "Manage own IDPs"}


class InteriorDesignerLoginController:
    # UT13.1 to UT13.8
    # returns the UserAccount, or None if the login isn't allowed - the entity does every check
    def login(self, username, password):
        return UserAccount().verifyCredentials(username, password, REQUIRED_DESIGNER_PERMISSIONS)

    # kept only for US21-US24 until Sprint 3 is fixed; not part of UC13
    def isInteriorDesigner(self, account):
        if account is None or not account.isActive():
            return False
        profile = UserProfile().getUserProfile(account.profileId)
        return (profile is not None and profile.isActive()
                and REQUIRED_DESIGNER_PERMISSIONS.issubset(profile.permissions))

    # kept only for US21-US24 until Sprint 3 is fixed; not part of UC13
    def getAuthenticatedDesigner(self, userId):
        account = UserAccount().getUserAccount(userId)
        return account if self.isInteriorDesigner(account) else None
