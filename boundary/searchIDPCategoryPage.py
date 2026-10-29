# Boundary: SearchIDPCategoryPage - UC45 Search IDP categories (US45)
# template: templates/idpCategories.html
# this is the IDP Categories list page too - empty search just lists everything (alt flow 1a)

from flask import redirect, render_template, session, url_for

from control.searchIDPCategoryController import SearchIDPCategoryController

MSG_NO_RESULTS = "No IDP categories found"


class SearchIDPCategoryPage:
    def __init__(self):
        self.searchIDPCategoryController = SearchIDPCategoryController()
        self.keyword = ""       # kept so it stays in the search box after searching

    def checkAccess(self):
        if "userId" not in session:
            return redirect(url_for("platformManagerLogin"))
        if not self.searchIDPCategoryController.canSearchIDPCategories(session["userId"]):
            return render_template("platformManagerAccessDenied.html"), 403
        return None

    def searchIDPCategories(self, keyword):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        self.keyword = keyword
        categories = self.searchIDPCategoryController.searchIDPCategories(keyword)

        # alt box in the seq diagram - found something or not
        if categories:
            return self.displayResults(categories)
        return self.displayNoResultsMessage()

    def displayResults(self, categories):
        # name, description and status for each one, + a View link (wireframe 4a)
        return render_template("idpCategories.html", activePage="categories",
                               categories=categories, keyword=self.keyword)

    def displayNoResultsMessage(self):
        # alt flow 3a - manager can just type something else and search again (wireframe 4c)
        return render_template("idpCategories.html", activePage="categories",
                               categories=[], keyword=self.keyword,
                               noResultsMessage=MSG_NO_RESULTS)
