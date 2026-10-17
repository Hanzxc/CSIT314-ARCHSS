# Control: CreateUserProfileController - UC3 Create user profile (US3)

from entity.userProfile import UserProfile


class CreateUserProfileController:
    # used to fill in the tick boxes on the form
    def getAllPermissions(self):
        # TODO: permissionList = UserProfile().getAllPermissions(), return permissionList
        pass

    # UT3.5 to UT3.8
    def createUserProfile(self, profileName, description, permissions):
        # TODO (sequence diagram msgs 10-14):
        # - return False if profileName is empty or permissions is empty (UT3.7, UT3.8)
        # - nameTaken = UserProfile().isProfileNameTaken(profileName)
        # - only if nameTaken is False -> created = UserProfile().createUserProfile(...)
        # - return success (True / False)
        pass
