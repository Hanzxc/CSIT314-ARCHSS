# Boundary: AddCurrentIDPPage - UC20 Add current IDP (US20)
# templates: addCurrentIDP.html, interiorDesignerBase.html
# precondition: the designer is already logged in (US13), so there's no extra access check here

from flask import flash, redirect, render_template, session, url_for

from control.addCurrentIDPController import AddCurrentIDPController
from control.searchIDPCategoryController import SearchIDPCategoryController
from entity.idp import IDP

MSG_ADDED = "Current IDP added successfully"
MSG_FIX_FIELDS = "Please fix the highlighted fields"
MSG_NO_CATEGORIES = "No IDP categories are available yet. Please try again later"
MSG_FAILED = "Current IDP could not be added. Please try again"
MSG_FIELD_REQUIRED = "This field is required"
MSG_TITLE_LENGTH = "Title must be 3-100 characters"
MSG_CHOOSE_CATEGORY = "Choose an available category"

FIELD_LIMITS = {"title": 100, "description": 2000, "location": 200}


class AddCurrentIDPPage:
    # UC20 Add current IDP
    # starts with an empty form and no errors
    def __init__(self):
        self.addCurrentIDPController = AddCurrentIDPController()
        self.idp = IDP()            # what's in the form
        self.fieldErrors = {}

    # UC20 Add current IDP
    # designer clicked "Add current IDP" on the dashboard - just show the empty form
    def clickAddCurrentIDP(self):
        return self.displayAddForm()

    # UC20 Add current IDP
    # the drop-down only offers Active categories (US44). listing the categories is US45's job
    # (search with an empty keyword), so we borrow that controller instead of adding it to this one
    def getAvailableCategories(self):
        categories = SearchIDPCategoryController().searchIDPCategories("")
        return sorted([category for category in categories if category.isActive()],
                      key=lambda category: category.categoryName.lower())

    # UC20 Add current IDP
    # shows the form, with what was typed and any errors (no form if there's nothing to choose)
    def displayAddForm(self, msg=None):
        categories = self.getAvailableCategories()
        if not categories and msg is None:
            msg = MSG_NO_CATEGORIES      # alt flow 2a - nothing to choose from yet (wireframe 4e)
        return render_template("addCurrentIDP.html", idp=self.idp, categories=categories,
                               fieldErrors=self.fieldErrors, errorMessage=msg, activePage="idps")

    # UC20 Add current IDP
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

    # UC20 Add current IDP
    # designer pressed "Add current IDP" - put the form into an IDP, check it, then just call add
    def submitCurrentIDP(self, title, categoryId, description, location):
        # the owner is always the logged-in designer, never a form field
        self.idp = IDP(designerId=session["userId"], categoryId=categoryId, title=title.strip(),
                       description=description.strip(), location=location.strip())

        # bad input -> controller never gets called (outer alt in the seq diagram)
        if not self.validateInput(self.idp):
            return self.displayErrorMessage(MSG_FIX_FIELDS)
        if self.addCurrentIDPController.addCurrentIDP(self.idp):
            return self.displaySuccessMessage(MSG_ADDED)
        # alt flow 5a - e.g. the category was suspended between checking and saving
        return self.displayErrorMessage(MSG_FAILED)

    # UC20 Add current IDP
    # back to the designer dashboard with a green message (wireframe 4d)
    def displaySuccessMessage(self, msg):
        flash(msg, "success")
        return redirect(url_for("interiorDesignerDashboard"))

    # UC20 Add current IDP
    # same form again with the message on top + the bad fields in red (wireframe 4c)
    def displayErrorMessage(self, msg):
        return self.displayAddForm(msg)
