# Boundary: UpdateIDPCategoryPage - UC43 Update IDP category (US43)
# template: templates/updateIDPCategory.html
# precondition: the manager is already logged in (US39), so there's no extra access check here

from flask import flash, redirect, render_template, url_for

from boundary.createIDPCategoryPage import getFieldErrors
from control.updateIDPCategoryController import UpdateIDPCategoryController
from entity.idpCategory import IDPCategory

MSG_UPDATED = "IDP category updated successfully"
MSG_NAME_TAKEN = "An IDP category with this name already exists"
MSG_FIX_FIELDS = "Please fix the highlighted fields"
MSG_NOT_FOUND = "IDP category not found"


class UpdateIDPCategoryPage:
    # UC43 Update IDP category
    # starts with an empty form and no errors
    def __init__(self):
        self.updateIDPCategoryController = UpdateIDPCategoryController()
        self.categoryId = None              # set by clickUpdate() / the route, used by submitUpdate()
        self.idpCategory = IDPCategory()    # what's in the form
        self.fieldErrors = {}

    # UC43 Update IDP category
    # manager clicked Update - fill the form with the category's current details
    def clickUpdate(self, categoryId):
        self.categoryId = categoryId
        idpCategory = self.updateIDPCategoryController.getIDPCategory(categoryId)
        if idpCategory is None:
            return self.displayNotFoundMessage()
        self.idpCategory = idpCategory
        return self.displayUpdateForm()

    # UC43 Update IDP category
    # shows the update form, with what was typed and any errors.
    # status isn't in the form - it's only shown as a badge (US44 changes it)
    def displayUpdateForm(self, msg=None):
        return render_template("updateIDPCategory.html", activePage="categories",
                               categoryId=self.categoryId, categoryName=self.idpCategory.categoryName,
                               description=self.idpCategory.description, status=self.idpCategory.status,
                               fieldErrors=self.fieldErrors, errorMessage=msg)

    # UC43 Update IDP category
    # same field rules as US41, true if there's nothing wrong
    def validateInput(self, idpCategory):
        self.fieldErrors = getFieldErrors(idpCategory)
        return len(self.fieldErrors) == 0

    # UC43 Update IDP category
    # manager pressed Save - put the form into an IDPCategory, check it, then just call update
    def submitUpdate(self, categoryName, description):
        # keep what they typed so nothing gets wiped if there's an error.
        # status isn't in the form (only US44 changes it), so it's left as None and the badge is hidden
        self.idpCategory = IDPCategory(categoryId=self.categoryId, categoryName=categoryName.strip(),
                                       description=description.strip(), status=None)

        if not self.validateInput(self.idpCategory):
            return self.displayErrorMessage(MSG_FIX_FIELDS)
        if self.updateIDPCategoryController.updateIDPCategory(self.idpCategory):
            return self.displaySuccessMessage(MSG_UPDATED)

        # categories can't be deleted (no such use case), so the only way update fails is the name being taken
        self.fieldErrors["categoryName"] = MSG_NAME_TAKEN
        return self.displayErrorMessage(MSG_NAME_TAKEN)

    # UC43 Update IDP category
    # go to the updated category's details page with the message (wireframe 4d)
    def displaySuccessMessage(self, msg):
        flash(msg, "success")
        return redirect(url_for("viewIDPCategory", categoryId=self.categoryId))

    # UC43 Update IDP category
    # stay on the form and show what went wrong
    def displayErrorMessage(self, msg):
        return self.displayUpdateForm(msg)

    # UC43 Update IDP category
    # the category doesn't exist (anymore) - message and a link back to the list
    def displayNotFoundMessage(self):
        return render_template("updateIDPCategory.html", activePage="categories",
                               categoryId=None, errorMessage=MSG_NOT_FOUND)
