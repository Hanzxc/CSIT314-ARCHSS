# Boundary: RestoreCompanyProfilePage - UC17 Delete company profile, restore (US17)
# the Restore button on the designer's own dashboard
# precondition: the designer is already logged in (US13), so there's no extra access check here

from secrets import compare_digest, token_urlsafe

from flask import flash, redirect, session, url_for

from control.restoreCompanyProfileController import RestoreCompanyProfileController

MSG_RESTORED = "Company profile restored successfully"
MSG_RESTORE_FAILED = "Company profile could not be restored. Please reopen the dashboard and try again"


class RestoreCompanyProfilePage:
    # UC17 Delete company profile, restore
    # just sets up the controller
    def __init__(self):
        self.restoreCompanyProfileController = RestoreCompanyProfileController()

    # UC17 Delete company profile, restore
    # if the designer has a deleted (suspended) profile, make a token for the Restore button
    def prepareRestore(self, designerId):
        profile = self.restoreCompanyProfileController.getSuspendedCompanyProfile(designerId)
        if profile is None:
            session.pop("companyRestoreConfirmation", None)
            return None
        token = token_urlsafe(24)
        session["companyRestoreConfirmation"] = {
            "designerId": designerId, "companyId": profile.companyId,
            "revision": profile.revision, "token": token}
        # Do not return business details to the suspended dashboard.
        return token

    # UC17 Delete company profile, restore
    # designer clicked Restore - check the token, then make the profile Active again
    def submitRestore(self, confirmationToken):
        designerId = session["userId"]
        confirmation = session.pop("companyRestoreConfirmation", None)
        if (not confirmation or confirmation.get("designerId") != designerId
                or not isinstance(confirmation.get("revision"), int)
                or not confirmationToken
                or not compare_digest(confirmation["token"], confirmationToken)):
            return self.displayFailure()
        if not self.restoreCompanyProfileController.restoreCompanyProfile(
                designerId, confirmation["companyId"], confirmation["revision"]):
            return self.displayFailure()
        session.pop("companyDeleteConfirmation", None)
        flash(MSG_RESTORED, "success")
        return redirect(url_for("viewCompanyProfile"))

    # UC17 Delete company profile, restore
    # restore didn't work, so back to the dashboard with an error
    def displayFailure(self):
        flash(MSG_RESTORE_FAILED, "error")
        return redirect(url_for("interiorDesignerDashboard"))
