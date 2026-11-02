"""US30: customer authentication using the shared account/profile entities."""
from entity.userAccount import UserAccount
from entity.userProfile import UserProfile

REQUIRED_CUSTOMER_PERMISSIONS = {"Search, view and save IDPs"}


class CustomerLoginController:
    def login(self, username, password):
        if not username or not username.strip() or not password:
            return None
        account = UserAccount().verifyCredentials(username, password)
        return account if self.isCustomer(account) else None

    def isCustomer(self, account):
        if account is None or not account.isActive():
            return False
        profile = UserProfile().getUserProfile(account.profileId)
        return (profile is not None and profile.isActive()
                and REQUIRED_CUSTOMER_PERMISSIONS.issubset(profile.permissions))

    def getAuthenticatedCustomer(self, userId):
        account = UserAccount().getUserAccount(userId)
        return account if self.isCustomer(account) else None
