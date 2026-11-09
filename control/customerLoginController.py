# Control: CustomerLoginController - UC30 Customer log in (US30)

from entity.userAccount import UserAccount

# /customer/login is only for customers - the profile needs this permission
REQUIRED_CUSTOMER_PERMISSIONS = {"Search, view and save IDPs"}


class CustomerLoginController:
    # UC30 Customer log in
    # returns the UserAccount, or None if the login isn't allowed - the entity does every check.
    # the page has already checked the input, so it isn't checked again here
    def login(self, username, password):
        return UserAccount().verifyCredentials(username, password, REQUIRED_CUSTOMER_PERMISSIONS)
