# Control: UpdateUserAccountController - UC10 Update user account (US10)

from entity.userAccount import UserAccount
from entity.userProfile import UserProfile


class UpdateUserAccountController:
    # loads the current details into the form
    def getUserAccount(self, userId):
        return UserAccount().getUserAccount(userId)

    # not on the class diagram - for the profile drop-down, same as US8
    def getAllUserProfiles(self):
        return UserProfile().searchUserProfiles("")

    # UT10.1 to UT10.4
    def updateUserAccount(self, userId, username, fullName, email, phone, profileId):
        if not username or not username.strip() or not fullName or not fullName.strip() \
                or profileId is None:
            return False

        profile = UserProfile().getUserProfile(profileId)
        profileActive = profile is not None and profile.isActive()
        # pass userId in so keeping its OWN username is fine (UT10.5)
        usernameTaken = UserAccount().isUsernameTaken(username, userId)

        success = False
        if profileActive and not usernameTaken:
            # comes back False if userId doesn't exist (UT10.4)
            success = UserAccount().updateUserAccount(userId, username, fullName,
                                                      email or "", phone or "", profileId)
        return success
