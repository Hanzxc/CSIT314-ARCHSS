# Boundary: SuspendIDPCategoryPage - UC44 Suspend IDP category (US44)
# the Suspend button + "Are you sure?" box on templates/viewIDPCategory.html

from flask import flash, redirect, render_template, session, url_for

from control.suspendIDPCategoryController import SuspendIDPCategoryController
from control.viewIDPCategoryController import ViewIDPCategoryController

MSG_SUSPENDED = "IDP category suspended successfully"
MSG_CANNOT_SUSPEND = "This IDP category cannot be suspended"


class SuspendIDPCategoryPage:
    def __init__(self):
        self.suspendIDPCategoryController = SuspendIDPCategoryController()
        self.categoryId = None

    def checkAccess(self):
        if "userId" not in session:
            return redirect(url_for("platformManagerLogin"))
        if not self.suspendIDPCategoryController.canSuspendIDPCategory(session["userId"]):
            return render_template("platformManagerAccessDenied.html"), 403
        return None

    def clickSuspend(self, categoryId):
        # manager clicked Suspend on the details page -> ask them first
        denied = self.checkAccess()
        if denied is not None:
            return denied
        self.categoryId = categoryId
        return self.displayConfirmation()

    def displayConfirmation(self):
        # shows the details page again but with the "Are you sure?" box on top (wireframe 4b).
        # borrowing the US42 controller just to load the category for the page behind the box
        viewIDPCategoryController = ViewIDPCategoryController()
        category = viewIDPCategoryController.viewIDPCategory(self.categoryId)
        if category is None or not category.isActive():
            return self.displayErrorMessage(MSG_CANNOT_SUSPEND)
        idps = viewIDPCategoryController.getIDPsInCategory(self.categoryId)
        return render_template("viewIDPCategory.html", activePage="categories",
                               category=category, idps=idps, showConfirmation=True)

    def confirmSuspend(self):
        # manager clicked OK in the box
        denied = self.checkAccess()
        if denied is not None:
            return denied
        success = self.suspendIDPCategoryController.suspendIDPCategory(self.categoryId)
        if success:
            return self.displaySuccessMessage(MSG_SUSPENDED)
        return self.displayErrorMessage(MSG_CANNOT_SUSPEND)

    def cancelSuspend(self):
        # alt flow 3a - nothing changes, just close the box
        return self.closeConfirmation()

    def closeConfirmation(self):
        # back to the normal details page (no box)
        return redirect(url_for("viewIDPCategory", categoryId=self.categoryId))

    def displaySuccessMessage(self, msg):
        # details page will now show the Suspended badge (wireframe 4c)
        flash(msg, "success")
        return redirect(url_for("viewIDPCategory", categoryId=self.categoryId))

    def displayErrorMessage(self, msg):
        flash(msg, "error")
        return redirect(url_for("viewIDPCategory", categoryId=self.categoryId))
