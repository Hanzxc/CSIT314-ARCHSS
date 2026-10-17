# Control: SuspendUserProfileController - UC6 Suspend user profile (US6)

from entity.userProfile import UserProfile


class SuspendUserProfileController:
    # adminProfileId = the profileId of the admin who is logged in (from the session)
    # UT6.1 to UT6.4
    def suspendUserProfile(self, profileId, adminProfileId):
        # TODO (sequence diagram msgs 5-11):
        # - profile = UserProfile().getUserProfile(profileId)
        # - return False if profile is None (UT6.4)
        # - active = profile.isActive()
        # - only if active AND profileId != adminProfileId
        #       -> suspended = UserProfile().suspendUserProfile(profileId)
        # - return success (True / False)
        pass
