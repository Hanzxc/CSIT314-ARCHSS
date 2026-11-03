# Control: SuspendUserProfileController - UC6 Suspend user profile (US6)

from entity.userProfile import UserProfile


class SuspendUserProfileController:
    # UT6.1 to UT6.4
    # the page stops the admin suspending their own group, the entity only suspends an
    # Active profile (already suspended / no such id -> False) - this just calls suspend
    def suspendUserProfile(self, profileId):
        return UserProfile().suspendUserProfile(profileId)
