# Control: CreateUserProfileController - UC3 Create user profile (US3)

from entity.userProfile import UserProfile


class CreateUserProfileController:
    # used to fill in the tick boxes on the form
    def getAllPermissions(self):
        return UserProfile().getAllPermissions()

    # UT3.5 to UT3.8
    # the page checks the input, the entity checks the name isn't taken - this just calls create
    def createUserProfile(self, profileName, description, permissions):
        return UserProfile().createUserProfile(profileName, description, permissions)
