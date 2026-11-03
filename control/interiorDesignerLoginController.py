# Control: InteriorDesignerLoginController - UC13 Interior designer log in (US13)
"""US13: designer authentication and access checks using existing entities."""
from entity.userAccount import UserAccount
from entity.userProfile import UserProfile

REQUIRED_DESIGNER_PERMISSIONS = {"Manage company profile", "Manage own IDPs"}


class InteriorDesignerLoginController:
    # UC13 Interior designer log in
    # returns the account if the username/password is right AND it's an active designer, else None
    def login(self, username, password):
        # the page already made sure both boxes are filled in
        account = UserAccount().verifyCredentials(username, password)
        return account if self.isInteriorDesigner(account) else None

    # UC13 Interior designer log in
    # active account + active profile + the designer permissions = an interior designer
    def isInteriorDesigner(self, account):
        if account is None or not account.isActive():
            return False
        profile = UserProfile().getUserProfile(account.profileId)
        return (profile is not None and profile.isActive()
                and REQUIRED_DESIGNER_PERMISSIONS.issubset(profile.permissions))

    # UC13 Interior designer log in
    # used by the other designer pages to re-check the logged-in user is still a designer
    def getAuthenticatedDesigner(self, userId):
        account = UserAccount().getUserAccount(userId)
        return account if self.isInteriorDesigner(account) else None
