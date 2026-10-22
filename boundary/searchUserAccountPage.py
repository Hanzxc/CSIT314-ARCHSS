# Boundary: SearchUserAccountPage - UC12 Search user account (US12)
# template: templates/userAccounts.html
# this is the User Accounts list page too - empty search just lists everything (alt flow 1a)

from flask import render_template

from control.searchUserAccountController import SearchUserAccountController

MSG_NO_RESULTS = "No user accounts found"


class SearchUserAccountPage:
    def __init__(self):
        self.searchUserAccountController = SearchUserAccountController()
        self.keyword = ""       # kept so it stays in the search box after searching

    def searchUserAccounts(self, keyword):
        self.keyword = keyword
        accounts = self.searchUserAccountController.searchUserAccounts(keyword)

        # alt box in the seq diagram - found something or not
        if accounts:
            return self.displayResults(accounts)
        return self.displayNoResultsMessage()

    def displayResults(self, accounts):
        # username, full name, email and status for each one, + a View link (step 3)
        return render_template("userAccounts.html", activePage="accounts",
                               accounts=accounts, keyword=self.keyword)

    def displayNoResultsMessage(self):
        # alt flow 3a - admin can just type something else and search again
        return render_template("userAccounts.html", activePage="accounts",
                               accounts=[], keyword=self.keyword,
                               noResultsMessage=MSG_NO_RESULTS)
