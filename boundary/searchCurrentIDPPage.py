# Boundary: SearchCurrentIDPPage - UC24 Search current IDPs (US24)
# template: searchCurrentIDPs.html
# precondition: the designer is already logged in (US13), so there's no extra access check here

from flask import render_template, session

from control.searchCurrentIDPController import SearchCurrentIDPController

MSG_NO_RESULTS = "No matching current IDPs found"
MSG_NO_IDPS = "You have no current IDPs to display"


class SearchCurrentIDPPage:
    # UC24 Search current IDPs
    # starts with an empty keyword
    def __init__(self):
        self.searchCurrentIDPController = SearchCurrentIDPController()
        self.keyword = ""

    # UC24 Search current IDPs
    # designer searched - the page trims the keyword (kept in the search box) and searches straight
    # away. the owner is always the logged-in designer
    def searchCurrentIDPs(self, keyword):
        self.keyword = (keyword or "").strip()
        idps = self.searchCurrentIDPController.searchCurrentIDPs(session["userId"], self.keyword)
        if idps:
            return self.displayResults(idps)
        return self.displayNoResultsMessage()

    # UC24 Search current IDPs
    # the matching project cards, newest first
    def displayResults(self, idps):
        return render_template("searchCurrentIDPs.html", idps=idps, keyword=self.keyword,
                               activePage="currentIDPs")

    # UC24 Search current IDPs
    # nothing matched - or, with an empty keyword, the designer has no current IDPs at all
    def displayNoResultsMessage(self):
        return render_template("searchCurrentIDPs.html", idps=[], keyword=self.keyword,
                               noResultsMessage=MSG_NO_RESULTS if self.keyword else MSG_NO_IDPS,
                               activePage="currentIDPs")
