# Control: UpdateUserProfileController - UC5 Update user profile (US5)

from entity.userProfile import UserProfile


class UpdateUserProfileController:
    # loads the current details into the form
    def getUserProfile(self, profileId):
        # TODO: return UserProfile().getUserProfile(profileId)
        pass

    # for the tick boxes on the form
    def getAllPermissions(self):
        # TODO: return UserProfile().getAllPermissions()
        pass

    # UT5.3 to UT5.8
    def updateUserProfile(self, profileId, profileName, description, permissions):
        # TODO (sequence diagram msgs 14-18):
        # - return False if profileName is empty or permissions is empty (UT5.6, UT5.7)
        # - nameTaken = UserProfile().isProfileNameTaken(profileName, profileId)
        # - only if nameTaken is False -> updated = UserProfile().updateUserProfile(...)
        # - return success (True / False), False if profileId doesn't exist (UT5.5)
        pass
