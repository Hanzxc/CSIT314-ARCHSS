# Boundary: SearchIDPPage - UC31 Search IDPs (US31)
# template: customerSearchIDPs.html
# precondition: the customer is already logged in (US30), so there's no extra access check here

from flask import render_template

from control.searchIDPController import SearchIDPController

MSG_NO_RESULTS = "No matching IDPs found"
MSG_NO_IDPS = "No IDPs are currently available"


class SearchIDPPage:
    # UC31 Search IDPs
    # starts with an empty keyword
    def __init__(self):
        self.searchIDPController = SearchIDPController()
        self.keyword = ""

    # UC31 Search IDPs
    # customer searched (or pressed Clear) - the page trims the keyword and keeps it in the search box.
    # an empty keyword lists every IDP a customer can see
    def searchIDPs(self, keyword):
        self.keyword = (keyword or "").strip()
        idps = self.searchIDPController.searchIDPs(self.keyword)
        if idps:
            return self.displayResults(idps)
        return self.displayNoResultsMessage()

    # UC31 Search IDPs
    # the matching IDP cards, newest first
    def displayResults(self, idps):
        return render_template("customerSearchIDPs.html", idps=idps, keyword=self.keyword,
                               activePage="searchIDPs")

    # UC31 Search IDPs
    # nothing matched - or, with an empty keyword, there's nothing to show at all
    def displayNoResultsMessage(self):
        return render_template("customerSearchIDPs.html", idps=[], keyword=self.keyword,
                               noResultsMessage=MSG_NO_RESULTS if self.keyword else MSG_NO_IDPS,
                               activePage="searchIDPs")
