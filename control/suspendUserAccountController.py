# Control: SuspendUserAccountController - UC11 Suspend user account (US11)

from entity.userAccount import UserAccount


class SuspendUserAccountController:
    # adminUserId = the userId of the admin who is logged in (from the session)
    # UT11.1 to UT11.4
    def suspendUserAccount(self, userId, adminUserId):
        account = UserAccount().getUserAccount(userId)
        if account is None:
            return False        # no such account (UT11.4)

        active = account.isActive()

        success = False
        # can't suspend one that's already suspended (UT11.2),
        # and the admin can't suspend their own account or they'd lock themselves out (UT11.3)
        if active and userId != adminUserId:
            success = UserAccount().suspendUserAccount(userId)
        return success
