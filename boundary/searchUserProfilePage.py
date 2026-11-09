# Boundary: SearchUserProfilePage - UC7 Search user profiles (US7)
# template: templates/userProfiles.html
# this is the User Profiles list page too - empty search just lists everything (alt flow 1a)

from flask import render_template

from control.searchUserProfileController import SearchUserProfileController

MSG_NO_RESULTS = "No user profiles found"


class SearchUserProfilePage:
    # UC7 Search user profiles
    # starts with an empty search box
    def __init__(self):
        self.searchUserProfileController = SearchUserProfileController()
        self.keyword = ""       # kept so it stays in the search box after searching

    # UC7 Search user profiles
    # admin clicked Search - ask the controller for matching profiles
    def searchUserProfiles(self, keyword):
        # tidy up the keyword first - "  Customer " should work the same as "Customer"
        # and just spaces counts as empty (shows everything)
        self.keyword = (keyword or "").strip()
        profiles = self.searchUserProfileController.searchUserProfiles(self.keyword)

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
