# Boundary: AddPastIDPPage - UC25 Add past IDP (US25)
# templates: addPastIDP.html, interiorDesignerBase.html
# precondition: the designer is already logged in (US13), so there's no extra access check here

from flask import flash, redirect, render_template, session, url_for

from control.addPastIDPController import AddPastIDPController
from control.searchIDPCategoryController import SearchIDPCategoryController
from entity.idp import IDP

MSG_ADDED = "Past IDP added successfully"
MSG_FIX_FIELDS = "Please fill in all required fields"
MSG_NO_CATEGORIES = "No IDP categories are available yet. Please try again later"
MSG_FAILED = "Past IDP could not be added. Please try again"
MSG_FIELD_REQUIRED = "This field is required"
MSG_TITLE_LENGTH = "Title must be 3-100 characters"
MSG_CHOOSE_CATEGORY = "Choose an available category"

FIELD_LIMITS = {"title": 100, "description": 2000, "location": 200}


class AddPastIDPPage:
    # UC25 Add past IDP
    # starts with an empty form and no errors
    def __init__(self):
        self.addPastIDPController = AddPastIDPController()
        self.idp = IDP(projectType="Past")      # what's in the form
        self.fieldErrors = {}

    # UC25 Add past IDP
    # designer clicked "Add past IDP" - show the empty form (wireframe 4a)
    def openAddPastIDPForm(self):
        return self.displayPastIDPForm()

    # UC25 Add past IDP
    # the drop-down only offers Active categories. listing categories is US45's job
    # (search with an empty keyword), so we borrow that controller instead of adding it to this one
    def getAvailableCategories(self):
        categories = SearchIDPCategoryController().searchIDPCategories("")
        return sorted([category for category in categories if category.isActive()],
                      key=lambda category: category.categoryName.lower())

    # UC25 Add past IDP
    # the form, with what was typed and any errors (no form if there's no category to choose)
    def displayPastIDPForm(self, msg=None):
        categories = self.getAvailableCategories()
        if not categories and msg is None:
            msg = MSG_NO_CATEGORIES
        return render_template("addPastIDP.html", idp=self.idp, categories=categories,
                               fieldErrors=self.fieldErrors, errorMessage=msg, activePage="pastIDPs")

    # UC25 Add past IDP
    # the field rules - title and description are required, the category must be one of the
    # Active ones in the drop-down. true if there's nothing wrong
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

    # UC25 Add past IDP
    # designer pressed "Add past IDP" - put the form into an IDP object, check it, then call add
    def submitPastIDP(self, title, categoryId, description, location):
        # the owner is always the logged-in designer, never a form field
        self.idp = IDP(designerId=session["userId"], categoryId=categoryId, title=title.strip(),
                       description=description.strip(), location=location.strip(), projectType="Past")
        # bad input -> the controller is never called (outer alt in the seq diagram)
        if not self.validateInput(self.idp):
            return self.displayErrorMessage(MSG_FIX_FIELDS)
        if self.addPastIDPController.addPastIDP(self.idp):
            return self.displaySuccessMessage(MSG_ADDED)
        # e.g. the category was suspended between showing the form and saving
        return self.displayErrorMessage(MSG_FAILED)

    # UC25 Add past IDP
    # back to the past IDPs list with a green message (wireframe 4c)
    def displaySuccessMessage(self, msg):
        flash(msg, "success")
        return redirect(url_for("pastIDPs"))

    # UC25 Add past IDP
    # same form again with the message on top and the bad fields in red (wireframe 4b)
    def displayErrorMessage(self, msg):
        return self.displayPastIDPForm(msg)
