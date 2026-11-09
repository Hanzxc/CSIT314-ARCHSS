# Control: InteriorDesignerLoginController - UC13 Interior designer log in (US13)

from entity.userAccount import UserAccount

# /designer/login is only for interior designers - the profile needs both of these
REQUIRED_DESIGNER_PERMISSIONS = {"Manage company profile", "Manage own IDPs"}


class InteriorDesignerLoginController:
    # UT13.1 to UT13.8
    # returns the UserAccount, or None if the login isn't allowed - the entity does every check
    def login(self, username, password):
        return UserAccount().verifyCredentials(username, password, REQUIRED_DESIGNER_PERMISSIONS)
