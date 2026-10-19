# Boundary: SearchUserProfilePage - UC1.7 Search user profiles (US7)
# template: templates/userProfiles.html
# this is the User Profiles list page too - empty search just lists everything (alt flow 1a)

from flask import render_template

from control.searchUserProfileController import SearchUserProfileController

MSG_NO_RESULTS = "No user profiles found"


class SearchUserProfilePage:
    def __init__(self):
        self.searchUserProfileController = SearchUserProfileController()
        self.keyword = ""       # kept so it stays in the search box after searching

    def searchUserProfiles(self, keyword):
        self.keyword = keyword
        profiles = self.searchUserProfileController.searchUserProfiles(keyword)

        # alt box in the seq diagram - found something or not
        if profiles:
            return self.displayResults(profiles)
        return self.displayNoResultsMessage()

    def displayResults(self, profiles):
        # name, description and status for each one, + a View link
        return render_template("userProfiles.html", activePage="profiles",
                               profiles=profiles, keyword=self.keyword)

    def displayNoResultsMessage(self):
        # alt flow 3a - admin can just type something else and search again
        return render_template("userProfiles.html", activePage="profiles",
                               profiles=[], keyword=self.keyword,
                               noResultsMessage=MSG_NO_RESULTS)
