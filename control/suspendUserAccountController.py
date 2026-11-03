# Control: SuspendUserAccountController - UC11 Suspend user account (US11)

from entity.userAccount import UserAccount


class SuspendUserAccountController:
    # UT11.1 to UT11.4
    # the page stops the admin suspending their own account, the entity only suspends an
    # Active account (already suspended / no such id -> False) - this just calls suspend
    def suspendUserAccount(self, userId):
        return UserAccount().suspendUserAccount(userId)
