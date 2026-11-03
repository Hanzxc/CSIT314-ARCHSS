# Control: ViewUserProfileController - UC4 View user profile (US4)

from entity.userProfile import UserProfile


class ViewUserProfileController:
    # UT4.5, UT4.6
    # just passes it through, gives None back if the id doesn't exist
    def getUserProfile(self, profileId):
        return UserProfile().getUserProfile(profileId)
