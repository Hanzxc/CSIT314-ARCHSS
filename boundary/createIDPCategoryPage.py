# Boundary: CreateIDPCategoryPage - UC41 Create IDP category (US41)
# templates: createIDPCategory.html, platformManagerBase.html
# precondition: the manager is already logged in (US39), so there's no extra access check here

from flask import flash, redirect, render_template, url_for

from control.createIDPCategoryController import CreateIDPCategoryController
from entity.idpCategory import IDPCategory

MSG_CREATED = "IDP category created successfully"
MSG_NAME_TAKEN = "An IDP category with this name already exists"
MSG_FIX_FIELDS = "Please fix the highlighted fields"
MSG_NAME_LENGTH = "Category name must be 3-50 characters"
MSG_DESCRIPTION_LENGTH = "Description must be 500 characters or fewer"


# UC41 Create IDP category, UC43 Update IDP category
# the field rules, shared with US43 - an empty dict means nothing is wrong
def getFieldErrors(idpCategory):
    fieldErrors = {}
    if len(idpCategory.categoryName) < 3 or len(idpCategory.categoryName) > 50:
        fieldErrors["categoryName"] = MSG_NAME_LENGTH
    if len(idpCategory.description) > 500:
        fieldErrors["description"] = MSG_DESCRIPTION_LENGTH
    return fieldErrors


class CreateIDPCategoryPage:
    # UC41 Create IDP category
    # starts with an empty form and no errors
    def __init__(self):
        self.createIDPCategoryController = CreateIDPCategoryController()
        self.idpCategory = IDPCategory()     # what's in the form
        self.fieldErrors = {}               # e.g. {"categoryName": MSG_NAME_LENGTH}

    # UC41 Create IDP category
    # manager clicked "Create IDP category" - just show the empty form
    def clickCreateIDPCategory(self):
        return self.displayCreateForm()

    # UC41 Create IDP category
    # shows the form, with what was typed and any errors
    def displayCreateForm(self, msg=None):
        return render_template("createIDPCategory.html", activePage="categories",
                               categoryName=self.idpCategory.categoryName,
                               description=self.idpCategory.description,
                               fieldErrors=self.fieldErrors, errorMessage=msg)

    # UC41 Create IDP category
    # true if there's nothing wrong with the input
    def validateInput(self, idpCategory):
        self.fieldErrors = getFieldErrors(idpCategory)
        return len(self.fieldErrors) == 0

    # UC41 Create IDP category
    # manager pressed Create - put the form into an IDPCategory, check it, then just call create
    def submitIDPCategory(self, categoryName, description):
        self.idpCategory = IDPCategory(categoryName=categoryName.strip(), description=description.strip())

        # bad input -> controller never gets called (outer alt in the seq diagram)
        if not self.validateInput(self.idpCategory):
            return self.displayErrorMessage(MSG_FIX_FIELDS)

        if self.createIDPCategoryController.createIDPCategory(self.idpCategory):
            return self.displaySuccessMessage(MSG_CREATED)

        # the only way create fails is the name being taken (alt flow 5a)
        self.fieldErrors["categoryName"] = MSG_NAME_TAKEN
        return self.displayErrorMessage(MSG_NAME_TAKEN)

    # UC41 Create IDP category
    # back to the IDP Categories list with a green message (wireframe 4d)
    def displaySuccessMessage(self, msg):
        flash(msg, "success")
        return redirect(url_for("idpCategories"))

    # UC41 Create IDP category
    # same form again with the message on top + the bad field in red (wireframe 4c)
    def displayErrorMessage(self, msg):
        return self.displayCreateForm(msg)
