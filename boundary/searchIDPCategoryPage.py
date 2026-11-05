# Boundary: SearchIDPCategoryPage - UC45 Search IDP categories (US45)
# template: templates/idpCategories.html
# this is the IDP Categories list page too - empty search just lists everything (alt flow 1a)
# precondition: the manager is already logged in (US39), so there's no extra access check here

from flask import render_template

from control.searchIDPCategoryController import SearchIDPCategoryController

MSG_NO_RESULTS = "No IDP categories found"


class SearchIDPCategoryPage:
    # UC45 Search IDP categories
    # the keyword is kept so it stays in the search box after searching
    def __init__(self):
        self.searchIDPCategoryController = SearchIDPCategoryController()
        self.keyword = ""

    # UC45 Search IDP categories
    # manager clicked Search - tidy up the keyword ("  Kitchen " works the same as "Kitchen",
    # just spaces counts as empty) then just call search
    def searchIDPCategories(self, keyword):
        self.keyword = (keyword or "").strip()
        categories = self.searchIDPCategoryController.searchIDPCategories(self.keyword)

        # alt box in the seq diagram - found something or not
        if categories:
            return self.displayResults(categories)
        return self.displayNoResultsMessage()

    # UC45 Search IDP categories
    # name, description and status for each one, + a View link (wireframe 4a)
    def displayResults(self, categories):
        return render_template("idpCategories.html", activePage="categories",
                               categories=categories, keyword=self.keyword)

    # UC45 Search IDP categories
    # alt flow 3a - manager can just type something else and search again (wireframe 4c)
    def displayNoResultsMessage(self):
        return render_template("idpCategories.html", activePage="categories",
                               categories=[], keyword=self.keyword,
                               noResultsMessage=MSG_NO_RESULTS)
