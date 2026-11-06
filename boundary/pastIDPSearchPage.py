# Boundary: PastIDPSearchPage - UC29 Search past IDPs (US29)
# templates: pastIDPs.html (the search bar sits on the past IDPs list), interiorDesignerBase.html
# precondition: the designer is already logged in (US13), so there's no extra access check here

from flask import render_template, session

from control.searchPastIDPController import SearchPastIDPController

MSG_NO_RESULTS = "No past IDPs match your search"
MSG_KEYWORD_TOO_LONG = "The keyword can be at most 100 characters"
KEYWORD_LIMIT = 100


class PastIDPSearchPage:
    def __init__(self):
        self.searchPastIDPController = SearchPastIDPController()
        self.keyword = ""

    # UC29 Search past IDPs
    # the keyword rule. an empty keyword is fine - it shows all past IDPs. returns the error, or None
    def validateKeyword(self, keyword):
        if len(keyword) > KEYWORD_LIMIT:
            return MSG_KEYWORD_TOO_LONG
        return None

    # UC29 Search past IDPs
    # designer typed a keyword and pressed Search
    def submitSearch(self, keyword):
        self.keyword = keyword.strip()
        error = self.validateKeyword(self.keyword)
        if error:
            return self.displayErrorMessage(error)           # the controller is never called
        results = self.searchPastIDPController.searchPastIDPs(session["userId"], self.keyword)
        if not results:
            return self.displayNoResultsMessage(MSG_NO_RESULTS)
        return self.displaySearchResults(results)

    # UC29 Search past IDPs
    # the matching past IDPs, keyword kept in the box (wireframe 4a)
    def displaySearchResults(self, results):
        return render_template("pastIDPs.html", idps=results, keyword=self.keyword, activePage="pastIDPs")

    # UC29 Search past IDPs
    # nothing matched (wireframe 4b)
    def displayNoResultsMessage(self, msg):
        return render_template("pastIDPs.html", idps=[], keyword=self.keyword, infoMessage=msg,
                               activePage="pastIDPs")

    # UC29 Search past IDPs
    # keyword too long - same page with the error
    def displayErrorMessage(self, msg):
        return render_template("pastIDPs.html", idps=[], keyword=self.keyword[:KEYWORD_LIMIT],
                               errorMessage=msg, activePage="pastIDPs"), 400
