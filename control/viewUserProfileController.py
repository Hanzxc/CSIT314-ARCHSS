# Control: ViewUserProfileController - UC4 View user profile (US4)

from entity.userProfile import UserProfile


class ViewUserProfileController:
    # UT4.5, UT4.6
    def getUserProfile(self, profileId):
        # just passes it through, gives None back if the id doesn't exist
        profile = UserProfile().getUserProfile(profileId)
        return profile
