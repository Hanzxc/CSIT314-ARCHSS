# Boundary: EditPastIDPPage - UC27 Update past IDP (US27)
# templates: editPastIDP.html, pastIDPNotFound.html, interiorDesignerBase.html
# precondition: the designer is already logged in (US13), so there's no extra access check here

from flask import flash, redirect, render_template, session, url_for

from control.updatePastIDPController import UpdatePastIDPController
from control.searchIDPCategoryController import SearchIDPCategoryController
from entity.idp import IDP

MSG_UPDATED = "Past IDP updated successfully"
MSG_FIX_FIELDS = "Please fill in all required fields"
MSG_NOT_FOUND = "Past IDP not found"
MSG_FAILED = "Past IDP could not be updated. Please try again"
MSG_FIELD_REQUIRED = "This field is required"
MSG_TITLE_LENGTH = "Title must be 3-100 characters"
MSG_CHOOSE_CATEGORY = "Choose an available category"

FIELD_LIMITS = {"title": 100, "description": 2000, "location": 200}


class EditPastIDPPage:
    # UC27 Update past IDP
    def __init__(self):
        self.updatePastIDPController = UpdatePastIDPController()
        self.idp = None                 # what's in the form
        self.fieldErrors = {}

    # UC27 Update past IDP
    # designer clicked Edit on one of their past IDPs - show the form filled in (wireframe 4a)
    def openEditForm(self, idpId):
        self.idp = self.updatePastIDPController.getPastIDP(session["userId"], idpId)
        if self.idp is None:
            return self.displayNotFoundMessage(MSG_NOT_FOUND)      # not theirs / already deleted
        return self.displayEditForm()

    # UC27 Update past IDP
    # same category rule as US25: only Active categories, borrowed from US45's controller
    def getAvailableCategories(self):
        categories = SearchIDPCategoryController().searchIDPCategories("")
        return sorted([category for category in categories if category.isActive()],
                      key=lambda category: category.categoryName.lower())

    # UC27 Update past IDP
    # the form with the current (or just typed) details and any errors
    def displayEditForm(self, msg=None):
        return render_template("editPastIDP.html", idp=self.idp, categories=self.getAvailableCategories(),
                               fieldErrors=self.fieldErrors, errorMessage=msg, activePage="pastIDPs")

    # UC27 Update past IDP
    # the same field rules as adding a past IDP. true if there's nothing wrong
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

    # UC27 Update past IDP
    # designer pressed "Save changes" - put the form into an IDP object, check it, then call update
    def submitUpdatedDetails(self, idpId, title, categoryId, description, location):
        self.idp = IDP(idpId=idpId, designerId=session["userId"], categoryId=categoryId, title=title.strip(),
                       description=description.strip(), location=location.strip(), projectType="Past")
        if not self.validateInput(self.idp):
            return self.displayErrorMessage(MSG_FIX_FIELDS)
        if self.updatePastIDPController.updatePastIDP(self.idp):
            return self.displaySuccessMessage(MSG_UPDATED)
        # not theirs, deleted meanwhile, or the category was suspended meanwhile
        if self.updatePastIDPController.getPastIDP(session["userId"], idpId) is None:
            return self.displayNotFoundMessage(MSG_NOT_FOUND)
        return self.displayErrorMessage(MSG_FAILED)

    # UC27 Update past IDP
    # back to that past IDP's details with a green message (wireframe 4c)
    def displaySuccessMessage(self, msg):
        flash(msg, "success")
        return redirect(url_for("viewPastIDP", idpId=self.idp.idpId))

    # UC27 Update past IDP
    # same form again with the message on top and the bad fields in red (wireframe 4b)
    def displayErrorMessage(self, msg):
        return self.displayEditForm(msg)

    # UC27 Update past IDP
    # the IDP isn't one of this designer's Active past IDPs (wireframe 4d)
    def displayNotFoundMessage(self, msg):
        return render_template("pastIDPNotFound.html", errorMessage=msg, activePage="pastIDPs"), 404
