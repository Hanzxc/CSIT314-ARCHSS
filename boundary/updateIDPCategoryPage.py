# Boundary: UpdateIDPCategoryPage - UC43 Update IDP category (US43)
# template: templates/updateIDPCategory.html

from flask import flash, redirect, render_template, session, url_for

from control.updateIDPCategoryController import UpdateIDPCategoryController

MSG_UPDATED = "IDP category updated successfully"
MSG_NAME_TAKEN = "An IDP category with this name already exists"
MSG_FIX_FIELDS = "Please fix the highlighted fields"
MSG_NAME_LENGTH = "Category name must be 3-50 characters"
MSG_DESCRIPTION_LENGTH = "Description must be 500 characters or fewer"
MSG_NOT_FOUND = "IDP category not found"


class UpdateIDPCategoryPage:
    def __init__(self):
        self.updateIDPCategoryController = UpdateIDPCategoryController()
        self.categoryId = None      # set by clickUpdate() / the route, used by submitUpdate()
        self.fieldErrors = {}

        # what's in the form right now (from the db at first, then whatever was typed)
        self.categoryName = ""
        self.description = ""
        self.status = ""

    def checkAccess(self):
        if "userId" not in session:
            return redirect(url_for("platformManagerLogin"))
        if not self.updateIDPCategoryController.canUpdateIDPCategory(session["userId"]):
            return render_template("platformManagerAccessDenied.html"), 403
        return None

    def clickUpdate(self, categoryId):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        self.categoryId = categoryId
        category = self.updateIDPCategoryController.getIDPCategory(categoryId)
        if category is None:
            return self.displayNotFoundMessage()
        return self.displayUpdateForm(category)

    def displayUpdateForm(self, category, msg=None):
        # fill the boxes from the category the first time
        if category is not None:
            self.categoryName = category.categoryName
            self.description = category.description
            self.status = category.status

        return render_template("updateIDPCategory.html", activePage="categories",
                               categoryId=self.categoryId, categoryName=self.categoryName,
                               description=self.description, status=self.status,
                               fieldErrors=self.fieldErrors, errorMessage=msg)

    def submitUpdate(self, categoryName, description):
        denied = self.checkAccess()
        if denied is not None:
            return denied

        # keep what they typed so nothing gets wiped if there's an error
        self.categoryName = categoryName
        self.description = description

        if not self.validateInput(categoryName, description):
            return self.displayErrorMessage(MSG_FIX_FIELDS)

        success = self.updateIDPCategoryController.updateIDPCategory(
            self.categoryId, categoryName, description)
        if success:
            return self.displaySuccessMessage(MSG_UPDATED)

        # it failed - either the category is gone or the name is taken, need to tell which
        if self.updateIDPCategoryController.getIDPCategory(self.categoryId) is None:
            return self.displayNotFoundMessage()

        self.fieldErrors["categoryName"] = MSG_NAME_TAKEN
        return self.displayErrorMessage(MSG_NAME_TAKEN)

    # UT43.9 - same rules as US41
    def validateInput(self, categoryName, description):
        self.fieldErrors = {}

        name = categoryName.strip()
        if len(name) < 3 or len(name) > 50:
            self.fieldErrors["categoryName"] = MSG_NAME_LENGTH

        if len(description.strip()) > 500:
            self.fieldErrors["description"] = MSG_DESCRIPTION_LENGTH

        return len(self.fieldErrors) == 0

    def displaySuccessMessage(self, msg):
        # go to the updated category's details page with the message (wireframe 4d)
        flash(msg, "success")
        return redirect(url_for("viewIDPCategory", categoryId=self.categoryId))

    def displayErrorMessage(self, msg):
        # status isn't in the form so grab it again for the badge at the top
        category = self.updateIDPCategoryController.getIDPCategory(self.categoryId)
        if category is not None:
            self.status = category.status
        # pass None as the category so it doesn't overwrite what they typed
        return self.displayUpdateForm(None, msg)

    def displayNotFoundMessage(self):
        # the category doesn't exist (anymore) - message and a link back to the list
        return render_template("updateIDPCategory.html", activePage="categories",
                               categoryId=None, errorMessage=MSG_NOT_FOUND)
