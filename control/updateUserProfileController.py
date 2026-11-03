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
    # the page checks the input, the entity checks the name isn't taken - this just calls update.
    # comes back False if profileId doesn't exist (UT5.5)
    def updateUserProfile(self, profileId, profileName, description, permissions):
        return UserProfile().updateUserProfile(profileId, profileName, description, permissions)
