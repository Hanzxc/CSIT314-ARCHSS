# Boundary: UpdateCurrentIDPPage - UC22 Update current IDP (US22)
# templates: updateCurrentIDP.html, currentIDPNotFound.html
# precondition: the designer is already logged in (US13), so there's no extra access check here.
# no form token - the entity only updates the owner's Active Current IDP

from flask import flash, redirect, render_template, session, url_for

from control.updateCurrentIDPController import UpdateCurrentIDPController
from control.searchIDPCategoryController import SearchIDPCategoryController
from entity.idp import IDP

MSG_UPDATED = "Current IDP updated successfully"
MSG_FIX_FIELDS = "Please fix the highlighted fields"
MSG_NOT_FOUND = "Current IDP not found"
MSG_FIELD_REQUIRED = "This field is required"
MSG_TITLE_LENGTH = "Title must be 3-100 characters"
MSG_CHOOSE_CATEGORY = "Choose an available category"

FIELD_LIMITS = {"title": 100, "description": 2000, "location": 200}


class UpdateCurrentIDPPage:
    # UC22 Update current IDP
    # starts with no IDP and no errors
    def __init__(self):
        self.updateCurrentIDPController = UpdateCurrentIDPController()
        self.idpId = None
        self.idp = IDP()            # what's in the form
        self.fieldErrors = {}

    # UC22 Update current IDP
    # designer clicked "Update current IDP" on the preview - fill the form with the saved details
    def clickUpdate(self, idpId):
        self.idpId = idpId
        idp = self.updateCurrentIDPController.getCurrentIDP(session["userId"], idpId)
        if idp is not None:
            self.idp = idp
            return self.displayUpdateForm()
        return self.displayNotFoundMessage()

    # UC22 Update current IDP
    # shows the form with the current (or typed) values and any errors
    def displayUpdateForm(self, msg=None):
        categories = self.getAvailableCategories()
        return render_template("updateCurrentIDP.html", idpId=self.idpId, idp=self.idp,
                               categories=categories, fieldErrors=self.fieldErrors,
                               errorMessage=msg, activePage="currentIDPs")

    # UC22 Update current IDP
    # the drop-down only offers Active categories (US44). listing the categories is US45's job
    # (search with an empty keyword), so we borrow that controller, same as US20
    def getAvailableCategories(self):
        categories = SearchIDPCategoryController().searchIDPCategories("")
        return sorted([category for category in categories if category.isActive()],
                      key=lambda category: category.categoryName.lower())

    # UC22 Update current IDP
    # the same field rules as US20 - title and description are required, the category must be one
    # of the Active ones in the drop-down. true if there's nothing wrong
    def validateInput(self, idp):
        self.fieldErrors = {}
        for field, limit in FIELD_LIMITS.items():
            value = getattr(idp, field)
            if field in ("title", "description") and not value:
                self.fieldErrors[field] = MSG_FIELD_REQUIRED
            elif len(value) > limit:
                self.fieldErrors[field] = "Maximum " + str(limit) + " characters"
        if idp.title and len(idp.title) < 3:
            self.fieldErrors["title"] = MSG_TITLE_LENGTH

        availableIds = [category.categoryId for category in self.getAvailableCategories()]
        if idp.categoryId not in availableIds:
            self.fieldErrors["categoryId"] = MSG_CHOOSE_CATEGORY
        return len(self.fieldErrors) == 0

    # UC22 Update current IDP
    # designer pressed "Save changes" - trim the input, put it into an IDP, check it, then update
    def submitUpdate(self, idpId, title, categoryId, description, location):
        self.idpId = idpId
        # the owner is always the logged-in designer, never a form field
        self.idp = IDP(idpId, session["userId"], categoryId, title.strip(), description.strip(),
                       location.strip())

        # bad input -> controller never gets called (outer alt in the seq diagram)
        if not self.validateInput(self.idp):
            return self.displayErrorMessage(MSG_FIX_FIELDS)
        updated = self.updateCurrentIDPController.updateCurrentIDP(self.idp)
        if updated:
            return self.displaySuccessMessage(MSG_UPDATED)
        # the IDP or its category was suspended meanwhile, or it isn't this designer's
        return self.displayNotFoundMessage()

    # UC22 Update current IDP
    # back to the preview with a green message
    def displaySuccessMessage(self, msg):
        flash(msg, "success")
        return redirect(url_for("viewCurrentIDP", idpId=self.idpId))

    # UC22 Update current IDP
    # same form again with the message on top + the bad fields in red, typed values kept
    def displayErrorMessage(self, msg):
        return self.displayUpdateForm(msg)

    # UC22 Update current IDP
    # HTTP 404 with no project details
    def displayNotFoundMessage(self):
        return render_template("currentIDPNotFound.html", errorMessage=MSG_NOT_FOUND,
                               activePage="currentIDPs"), 404
