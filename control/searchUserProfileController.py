# Control: SearchUserProfileController - UC7 Search user profiles (US7)
# US8 and US10 also use it for the profile drop-down (empty keyword = every profile)

from entity.userProfile import UserProfile


class SearchUserProfileController:
    # UT7.9 to UT7.11
    # the page already tidied the keyword (spaces trimmed), so just pass it on
    def searchUserProfiles(self, keyword):
        return UserProfile().searchUserProfiles(keyword)
