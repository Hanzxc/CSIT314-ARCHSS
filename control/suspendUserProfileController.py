# Control: SuspendUserProfileController - UC6 Suspend user profile (US6)

from entity.userProfile import UserProfile


class SuspendUserProfileController:
    # adminProfileId = the profileId of the admin who is logged in (from the session)
    # UT6.1 to UT6.4
    def suspendUserProfile(self, profileId, adminProfileId):
        profile = UserProfile().getUserProfile(profileId)
        if profile is None:
            return False        # no such profile (UT6.4)

        active = profile.isActive()

        success = False
        # can't suspend something that's already suspended (UT6.2),
        # and the admin can't suspend their own group or they'd lock themselves out (UT6.3)
        if active and profileId != adminProfileId:
            success = UserProfile().suspendUserProfile(profileId)
        return success
