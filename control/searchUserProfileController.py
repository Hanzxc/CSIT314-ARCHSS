# Control: SearchUserProfileController - UC1.7 Search user profiles (US7)

from entity.userProfile import UserProfile


class SearchUserProfileController:
    # UT7.9 to UT7.11
    def searchUserProfiles(self, keyword):
        # tidy up the keyword first - "  Customer " should work the same as "Customer"
        # and just spaces counts as empty (shows everything)
        if keyword is None:
            keyword = ""
        keyword = keyword.strip()

        profiles = UserProfile().searchUserProfiles(keyword)
        return profiles
