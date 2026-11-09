# Control: CreateUserProfileController - UC3 Create user profile (US3)

from entity.userProfile import UserProfile


class CreateUserProfileController:
    # UT3.1 - fills in the tick boxes on the form (US5 borrows it for its form too)
    def getAllPermissions(self):
        return UserProfile().getAllPermissions()

    # UT3.5, UT3.6
    # the page checks the input, the entity checks the name isn't taken - this just calls create
    def createUserProfile(self, profile):
        return UserProfile().createUserProfile(profile)
