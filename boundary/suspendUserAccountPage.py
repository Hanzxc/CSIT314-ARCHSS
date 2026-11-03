# Boundary: SuspendUserAccountPage - UC11 Suspend user account (US11)
# the Suspend button + confirmation box on templates/viewUserAccount.html

from flask import render_template, redirect, url_for, session, flash

from control.suspendUserAccountController import SuspendUserAccountController
from control.viewUserAccountController import ViewUserAccountController

MSG_SUSPENDED = "User account suspended successfully"
MSG_CANNOT_SUSPEND = "This user account cannot be suspended"


class SuspendUserAccountPage:
    # UC11 Suspend user account
    # userId gets filled in by the route
    def __init__(self):
        self.suspendUserAccountController = SuspendUserAccountController()
        self.userId = None

    def clickSuspend(self, userId):
        # admin clicked Suspend on the details page -> ask them first
        self.userId = userId
        return self.displayConfirmation()

    def displayConfirmation(self):
        # details page again with the confirmation box on top, same as US6.
        # borrowing the US9 controller to load the account + profile for the page behind the box
        viewController = ViewUserAccountController()
        account = viewController.viewUserAccount(self.userId)
        if account is None:
            return self.displayErrorMessage(MSG_CANNOT_SUSPEND)
        return render_template("viewUserAccount.html", activePage="accounts",
                               account=account, profile=viewController.profile,
                               showConfirmation=True)

    def confirmSuspend(self):
        # admin clicked Suspend in the box.
        # the page checks this one - the admin can't suspend their own account or
        # they'd lock themselves out (UT11.3)
        if self.userId == session["userId"]:
            return self.displayErrorMessage(MSG_CANNOT_SUSPEND)

        # already suspended / no such id -> the entity gives back False (UT11.2, UT11.4)
        if self.suspendUserAccountController.suspendUserAccount(self.userId):
            return self.displaySuccessMessage(MSG_SUSPENDED)
        return self.displayErrorMessage(MSG_CANNOT_SUSPEND)

    def cancelSuspend(self):
        # alt flow 3a - nothing changes, just close the box
        return self.closeConfirmation()

    # UC11 Suspend user account
    # close the box and go back to the account details
    def closeConfirmation(self):
        return redirect(url_for("viewUserAccount", userId=self.userId))

    def displaySuccessMessage(self, msg):
        # details page will now show the Suspended badge and no Suspend button
        flash(msg, "success")
        return redirect(url_for("viewUserAccount", userId=self.userId))

    # UC11 Suspend user account
    # back to the account details with a red message
    def displayErrorMessage(self, msg):
        flash(msg, "error")
        return redirect(url_for("viewUserAccount", userId=self.userId))
