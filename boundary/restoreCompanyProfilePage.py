# Boundary: RestoreCompanyProfilePage - UC17-R Restore company profile (US17)
# the Restore button on the designer's own dashboard (US13 shows it with hidden companyId + revision)
# precondition: the designer is already logged in (US13), so there's no extra access check here

from flask import flash, redirect, session, url_for

from control.restoreCompanyProfileController import RestoreCompanyProfileController

MSG_RESTORED = "Company profile restored successfully"
MSG_RESTORE_FAILED = "Company profile could not be restored. Please reopen the dashboard and try again"


class RestoreCompanyProfilePage:
    # UC17-R Restore company profile
    # just sets up the controller
    def __init__(self):
        self.restoreCompanyProfileController = RestoreCompanyProfileController()

    # UC17-R Restore company profile
    # designer clicked Restore - the owner comes from the session, the entity only restores
    # their Suspended row if the companyId and revision still match
    def submitRestore(self, companyId, revision):
        restored = self.restoreCompanyProfileController.restoreCompanyProfile(session["userId"], companyId, revision)
        if restored:
            return self.displaySuccessMessage(MSG_RESTORED)
        return self.displayErrorMessage(MSG_RESTORE_FAILED)

    # UC17-R Restore company profile
    # the company view with the saved details back (wireframe 4f)
    def displaySuccessMessage(self, msg):
        flash(msg, "success")
        return redirect(url_for("viewCompanyProfile"))

    # UC17-R Restore company profile
    # old dashboard or not Suspended any more - back to the dashboard with the error (wireframe 4g)
    def displayErrorMessage(self, msg):
        flash(msg, "error")
        return redirect(url_for("interiorDesignerDashboard"))
