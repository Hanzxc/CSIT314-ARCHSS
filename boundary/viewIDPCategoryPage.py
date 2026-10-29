# Boundary: ViewIDPCategoryPage - UC42 View IDP category (US42)
# template: templates/viewIDPCategory.html

from flask import redirect, render_template, session, url_for

from control.viewIDPCategoryController import ViewIDPCategoryController

MSG_NOT_FOUND = "IDP category not found"
MSG_NO_IDPS = "No IDPs are in this category yet"


class ViewIDPCategoryPage:
    def __init__(self):
        self.viewIDPCategoryController = ViewIDPCategoryController()

    def checkAccess(self):
        if "userId" not in session:
            return redirect(url_for("platformManagerLogin"))
        if not self.viewIDPCategoryController.canViewIDPCategory(session["userId"]):
            return render_template("platformManagerAccessDenied.html"), 403
        return None

    def selectIDPCategory(self, categoryId):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        category = self.viewIDPCategoryController.viewIDPCategory(categoryId)
        if category is None:
            return self.displayErrorMessage(MSG_NOT_FOUND)
        idps = self.viewIDPCategoryController.getIDPsInCategory(categoryId)
        return self.displayIDPCategory(category, idps)

    def displayIDPCategory(self, category, idps):
        # name, description, status badge and the IDPs grouped in it (wireframes 4b, 4c)
        return render_template("viewIDPCategory.html", activePage="categories",
                               category=category, idps=idps, noIDPsMessage=MSG_NO_IDPS)

    def displayErrorMessage(self, msg):
        # wireframe 4d - just the message and a link back to the list
        return render_template("viewIDPCategory.html", activePage="categories",
                               category=None, errorMessage=msg)
