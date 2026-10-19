# Control: CreateUserProfileController - UC3 Create user profile (US3)

from entity.userProfile import UserProfile


class CreateUserProfileController:
    # used to fill in the tick boxes on the form
    def getAllPermissions(self):
        permissionList = UserProfile().getAllPermissions()
        return permissionList

    # UT3.5 to UT3.8
    def createUserProfile(self, profileName, description, permissions):
        # the page checks this too but the controller shouldn't trust that (UT3.7, UT3.8)
        if not profileName or not profileName.strip() or not permissions:
            return False

        # business rule - no 2 profiles with the same name (seq diagram msgs 10-11)
        nameTaken = UserProfile().isProfileNameTaken(profileName)

        success = False
        if not nameTaken:
            # opt box in the seq diagram, only save when the name is free
            success = UserProfile().createUserProfile(profileName, description, permissions)
        return success
