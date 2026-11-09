# Control: UpdateUserProfileController - UC5 Update user profile (US5)
# the permission tick boxes are US3's form data, so the page borrows CreateUserProfileController for them

from entity.userProfile import UserProfile


class UpdateUserProfileController:
    # US5's own loader - gets the current details for the form
    def getUserProfile(self, profileId):
        return UserProfile().getUserProfile(profileId)

    # UT5.3 to UT5.5, UT5.8
    # the page checks the input, the entity checks the profile is Active and the name isn't taken -
    # this just calls update
    def updateUserProfile(self, profile):
        return UserProfile().updateUserProfile(profile)
