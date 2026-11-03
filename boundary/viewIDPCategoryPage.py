# Boundary: ViewIDPCategoryPage - UC42 View IDP category (US42)
# template: templates/viewIDPCategory.html
# precondition: the manager is already logged in (US39), so there's no extra access check here

from flask import render_template

from control.viewIDPCategoryController import ViewIDPCategoryController

MSG_NOT_FOUND = "IDP category not found"
MSG_NO_IDPS = "No IDPs are in this category yet"


class ViewIDPCategoryPage:
    # UC42 View IDP category
    # just sets up the controller
    def __init__(self):
        self.viewIDPCategoryController = ViewIDPCategoryController()

    # UC42 View IDP category
    # manager clicked View on a category - show it with the IDPs grouped in it
    def selectIDPCategory(self, categoryId):
        idpCategory = self.viewIDPCategoryController.viewIDPCategory(categoryId)
        if idpCategory is None:
            return self.displayErrorMessage(MSG_NOT_FOUND)
        idps = self.viewIDPCategoryController.getIDPsInCategory(categoryId)
        return self.displayIDPCategory(idpCategory, idps)

    # UC42 View IDP category
    # name, description, status badge and the IDPs grouped in it (wireframes 4b, 4c)
    def displayIDPCategory(self, idpCategory, idps):
        return render_template("viewIDPCategory.html", activePage="categories",
                               category=idpCategory, idps=idps, noIDPsMessage=MSG_NO_IDPS)

    # UC42 View IDP category
    # wireframe 4d - just the message and a link back to the list
    def displayErrorMessage(self, msg):
        return render_template("viewIDPCategory.html", activePage="categories",
                               category=None, errorMessage=msg)
