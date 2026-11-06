# Boundary: SavedListPage - UC35 View saved list (US35) and UC34 Search saved list (US34)
# the customer's saved IDPs with a search bar on top. US35 and US34 each have their own controller.
# templates: savedList.html, customerBase.html
# precondition: the customer is already logged in (US30), so there's no extra access check here

from flask import render_template, session

from control.viewSavedListController import ViewSavedListController
from control.searchSavedListController import SearchSavedListController

MSG_NO_SAVED = "You have not saved any IDPs yet"
MSG_NO_RESULTS = "No saved IDPs match your search"
MSG_KEYWORD_TOO_LONG = "The keyword can be at most 100 characters"
KEYWORD_LIMIT = 100


class SavedListPage:
    def __init__(self):
        self.viewSavedListController = ViewSavedListController()
        self.searchSavedListController = SearchSavedListController()
        self.keyword = ""

    # ---------- UC35 View saved list ----------

    # UC35 View saved list
    # customer clicked "Saved IDPs" - show everything they saved, newest first (wireframe 4a)
    def openSavedList(self):
        savedIDPs = self.viewSavedListController.getSavedList(session["userId"])
        if not savedIDPs:
            return self.displayEmptyMessage(MSG_NO_SAVED)            # alt flow - nothing saved yet (4b)
        return self.displaySavedProjects(savedIDPs)

    # UC35 View saved list
    def displaySavedProjects(self, savedIDPs):
        return render_template("savedList.html", idps=savedIDPs, keyword="", activePage="savedIDPs")

    # UC35 View saved list
    def displayEmptyMessage(self, msg):
        return render_template("savedList.html", idps=[], keyword="", infoMessage=msg, activePage="savedIDPs")

    # ---------- UC34 Search saved list ----------

    # UC34 Search saved list
    # the keyword rule. an empty keyword is fine - it shows the whole saved list. returns the error, or None
    def validateKeyword(self, keyword):
        if len(keyword) > KEYWORD_LIMIT:
            return MSG_KEYWORD_TOO_LONG
        return None

    # UC34 Search saved list
    # customer typed a keyword and pressed Search
    def submitSearch(self, keyword):
        self.keyword = keyword.strip()
        error = self.validateKeyword(self.keyword)
        if error:
            return self.displayErrorMessage(error)                 # the controller is never called
        results = self.searchSavedListController.searchSavedList(session["userId"], self.keyword)
        if not results:
            return self.displayNoResultsMessage(MSG_NO_RESULTS)
        return self.displaySearchResults(results)

    # UC34 Search saved list
    # the matching saved IDPs, keyword kept in the box (wireframe 4a)
    def displaySearchResults(self, results):
        return render_template("savedList.html", idps=results, keyword=self.keyword, activePage="savedIDPs")

    # UC34 Search saved list
    # nothing matched (wireframe 4b)
    def displayNoResultsMessage(self, msg):
        return render_template("savedList.html", idps=[], keyword=self.keyword, infoMessage=msg,
                               activePage="savedIDPs")

    # UC34 Search saved list
    def displayErrorMessage(self, msg):
        return render_template("savedList.html", idps=[], keyword=self.keyword[:KEYWORD_LIMIT],
                               errorMessage=msg, activePage="savedIDPs"), 400
