# Control: UpdateUserProfileController - UC5 Update user profile (US5)

from entity.userProfile import UserProfile


class UpdateUserProfileController:
    # loads the current details into the form
    def getUserProfile(self, profileId):
        return UserProfile().getUserProfile(profileId)

    # for the tick boxes on the form
    def getAllPermissions(self):
        return UserProfile().getAllPermissions()

    # UT5.3 to UT5.8
    def updateUserProfile(self, profileId, profileName, description, permissions):
        # same as create - don't rely on the page having checked it (UT5.6, UT5.7)
        if not profileName or not profileName.strip() or not permissions:
            return False

        # pass profileId in so it doesn't count its OWN name as taken (seq diagram msgs 14-15)
        nameTaken = UserProfile().isProfileNameTaken(profileName, profileId)

        success = False
        if not nameTaken:
            # comes back False if profileId doesn't exist (UT5.5)
            success = UserProfile().updateUserProfile(profileId, profileName, description, permissions)
        return success
