# Control: CreateUserAccountController - UC8 Create user account (US8)

from entity.userAccount import UserAccount
from entity.userProfile import UserProfile


class CreateUserAccountController:
    # not on the class diagram - the page needs the profiles for the drop-down,
    # and it isn't allowed to talk to the entity itself (B-C-E)
    def getAllUserProfiles(self):
        return UserProfile().searchUserProfiles("")

    # UT8.1 to UT8.4
    def createUserAccount(self, username, password, fullName, email, phone, profileId):
        # the page checks this too but the controller shouldn't trust that
        if not username or not username.strip() or not password \
                or not fullName or not fullName.strip() or profileId is None:
            return False

        # business rules (step 5) - the group must be active and the username free
        profile = UserProfile().getUserProfile(profileId)
        profileActive = profile is not None and profile.isActive()
        usernameTaken = UserAccount().isUsernameTaken(username)

        success = False
        if profileActive and not usernameTaken:
            # opt box in the seq diagram, only save when both checks are OK
            success = UserAccount().createUserAccount(username, password, fullName,
                                                      email or "", phone or "", profileId)
        return success
