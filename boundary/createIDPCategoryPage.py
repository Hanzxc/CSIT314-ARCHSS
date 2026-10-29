# Boundary: CreateIDPCategoryPage - UC41 Create IDP category (US41)
# templates: createIDPCategory.html, platformManagerBase.html

from flask import flash, redirect, render_template, session, url_for

from control.createIDPCategoryController import CreateIDPCategoryController

MSG_CREATED = "IDP category created successfully"
MSG_NAME_TAKEN = "An IDP category with this name already exists"
MSG_FIX_FIELDS = "Please fix the highlighted fields"
MSG_NAME_LENGTH = "Category name must be 3-50 characters"
MSG_DESCRIPTION_LENGTH = "Description must be 500 characters or fewer"


class CreateIDPCategoryPage:
    def __init__(self):
        self.createIDPCategoryController = CreateIDPCategoryController()
        self.fieldErrors = {}       # e.g. {"categoryName": MSG_NAME_LENGTH}

        # whatever the manager typed, so the form can be refilled if there's an error (alt flow 4a)
        self.categoryName = ""
        self.description = ""

    def checkAccess(self):
        if "userId" not in session:
            return redirect(url_for("platformManagerLogin"))
        if not self.createIDPCategoryController.canCreateIDPCategory(session["userId"]):
            return render_template("platformManagerAccessDenied.html"), 403
        return None

    def clickCreateIDPCategory(self):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        return self.displayCreateForm()

    def displayCreateForm(self, msg=None):
        return render_template("createIDPCategory.html", activePage="categories",
                               categoryName=self.categoryName, description=self.description,
                               fieldErrors=self.fieldErrors, errorMessage=msg)

    def submitIDPCategory(self, categoryName, description):
        denied = self.checkAccess()
        if denied is not None:
            return denied

        # remember what was typed first, in case we need to show the form again
        self.categoryName = categoryName
        self.description = description

        # bad input -> controller never gets called (outer alt in the seq diagram)
        if not self.validateInput(categoryName, description):
            return self.displayErrorMessage(MSG_FIX_FIELDS)

        success = self.createIDPCategoryController.createIDPCategory(categoryName, description)
        if success:
            return self.displaySuccessMessage(MSG_CREATED)

        # the only way it fails now is the name being taken (alt flow 5a)
        self.fieldErrors["categoryName"] = MSG_NAME_TAKEN
        return self.displayErrorMessage(MSG_NAME_TAKEN)

    # UT41.9 to UT41.12
    def validateInput(self, categoryName, description):
        self.fieldErrors = {}       # start fresh each time

        name = categoryName.strip()
        if len(name) < 3 or len(name) > 50:
            self.fieldErrors["categoryName"] = MSG_NAME_LENGTH

        if len(description.strip()) > 500:
            self.fieldErrors["description"] = MSG_DESCRIPTION_LENGTH

        return len(self.fieldErrors) == 0

    def displaySuccessMessage(self, msg):
        # back to the IDP Categories list, flash() keeps the message across the redirect (wireframe 4d)
        flash(msg, "success")
        return redirect(url_for("idpCategories"))

    def displayErrorMessage(self, msg):
        # same form again with the message on top + the bad field in red (wireframe 4c)
        return self.displayCreateForm(msg)
