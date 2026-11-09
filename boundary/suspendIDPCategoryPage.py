# Boundary: SuspendIDPCategoryPage - UC44 Suspend IDP category (US44)
# the Suspend button + "Are you sure?" box on templates/viewIDPCategory.html
# precondition: the manager is already logged in (US39), so there's no extra access check here

from flask import flash, redirect, render_template, url_for

from control.suspendIDPCategoryController import SuspendIDPCategoryController
from control.viewIDPCategoryController import ViewIDPCategoryController

MSG_SUSPENDED = "IDP category suspended successfully"
MSG_CANNOT_SUSPEND = "This IDP category cannot be suspended"


class SuspendIDPCategoryPage:
    # UC44 Suspend IDP category
    # sets up the controllers - the box shows the category, so US42's controller is borrowed to load it
    def __init__(self):
        self.suspendIDPCategoryController = SuspendIDPCategoryController()
        self.viewIDPCategoryController = ViewIDPCategoryController()
        self.categoryId = None

    # UC44 Suspend IDP category
    # manager clicked Suspend on the details page -> load the category and ask them first.
    # no isActive() check here - the entity only suspends an Active row when they click OK
    def clickSuspend(self, categoryId):
        self.categoryId = categoryId
        idpCategory = self.viewIDPCategoryController.viewIDPCategory(categoryId)
        if idpCategory is not None:
            return self.displayConfirmation(idpCategory)
        return self.displayErrorMessage(MSG_CANNOT_SUSPEND)

    # UC44 Suspend IDP category
    # shows the details page again but with the "Are you sure?" box on top (wireframe 4b)
    def displayConfirmation(self, idpCategory):
        return render_template("viewIDPCategory.html", activePage="categories",
                               category=idpCategory, showConfirmation=True)

    # UC44 Suspend IDP category
    # manager clicked OK in the box - just call suspend
    def confirmSuspend(self):
        suspended = self.suspendIDPCategoryController.suspendIDPCategory(self.categoryId)
        if suspended:
            return self.displaySuccessMessage(MSG_SUSPENDED)
        return self.displayErrorMessage(MSG_CANNOT_SUSPEND)

    # UC44 Suspend IDP category
    # alt flow 3a - nothing changes, just close the box
    def cancelSuspend(self):
        return self.closeConfirmation()

    # UC44 Suspend IDP category
    # back to the normal details page (no box)
    def closeConfirmation(self):
        return redirect(url_for("viewIDPCategory", categoryId=self.categoryId))

    # UC44 Suspend IDP category
    # details page will now show the Suspended badge (wireframe 4c)
    def displaySuccessMessage(self, msg):
        flash(msg, "success")
        return redirect(url_for("viewIDPCategory", categoryId=self.categoryId))

    # UC44 Suspend IDP category
    # missing or already suspended - back to the details page with the error
    def displayErrorMessage(self, msg):
        flash(msg, "error")
        return redirect(url_for("viewIDPCategory", categoryId=self.categoryId))
