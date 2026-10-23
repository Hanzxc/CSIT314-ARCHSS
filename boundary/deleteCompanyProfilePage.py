# Boundary: DeleteCompanyProfilePage - UC17 Delete company profile (US17)

from secrets import compare_digest, token_urlsafe

from flask import flash, redirect, render_template, session, url_for

from control.deleteCompanyProfileController import DeleteCompanyProfileController

MSG_DELETED = "Company profile deleted successfully"
MSG_NOT_FOUND = "You have not created a company profile yet"
MSG_CONFIRM_AGAIN = "Please open the delete confirmation and try again"
MSG_FAILED = "Company profile could not be deleted. Please reopen the confirmation"


class DeleteCompanyProfilePage:
    def __init__(self):
        self.deleteCompanyProfileController = DeleteCompanyProfileController()

    def checkAccess(self):
        if "userId" not in session:
            return redirect(url_for("interiorDesignerLogin"))
        if not self.deleteCompanyProfileController.canDeleteCompanyProfile(session["userId"]):
            return render_template("interiorDesignerAccessDenied.html"), 403
        return None

    def clickDelete(self):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        profile = self.deleteCompanyProfileController.getCompanyProfile(session["userId"])
        if profile is None:
            session.pop("companyDeleteConfirmation", None)
            return self.displayNotFoundMessage()
        return self.displayConfirmation(profile)

    def displayConfirmation(self, profile):
        token = token_urlsafe(24)
        session["companyDeleteConfirmation"] = {
            "designerId": session["userId"], "companyId": profile.companyId, "revision": profile.revision, "token": token}
        return render_template("deleteCompanyProfile.html", company=profile,
                               confirmationToken=token, activePage="company")

    def submitDelete(self, choice, companyId, confirmationToken):
        denied = self.checkAccess()
        if denied is not None:
            return denied
        if choice == "cancel":
            return self.cancelDelete()
        if choice == "delete":
            return self.confirmDelete(companyId, confirmationToken)
        return self.displayErrorMessage(MSG_CONFIRM_AGAIN)

    def confirmDelete(self, companyId, confirmationToken):
        confirmation = session.get("companyDeleteConfirmation")
        designerId = session["userId"]
        if (not confirmation or confirmation.get("designerId") != designerId
                or confirmation.get("companyId") != companyId
                or not isinstance(confirmation.get("revision"), int) or not confirmationToken
                or not compare_digest(confirmation["token"], confirmationToken)):
            return self.displayErrorMessage(MSG_CONFIRM_AGAIN)
        # Consume once and bind to this activation, even when reactivation keeps the same companyId.
        session.pop("companyDeleteConfirmation", None)
        if self.deleteCompanyProfileController.deleteCompanyProfile(
                designerId, companyId, confirmation["revision"]):
            return self.displaySuccessMessage(MSG_DELETED)
        if self.deleteCompanyProfileController.getCompanyProfile(designerId) is None:
            return self.displayNotFoundMessage()
        return self.displayErrorMessage(MSG_FAILED)

    def cancelDelete(self):
        session.pop("companyDeleteConfirmation", None)
        return self.closeConfirmation()

    def closeConfirmation(self):
        return redirect(url_for("viewCompanyProfile"))

    def displaySuccessMessage(self, msg):
        flash(msg, "success")
        return redirect(url_for("interiorDesignerDashboard"))

    def displayErrorMessage(self, msg):
        return render_template("companyProfileDeleteError.html", errorMessage=msg,
                               activePage="company"), 400

    def displayNotFoundMessage(self):
        return render_template("companyProfileNotFound.html", errorMessage=MSG_NOT_FOUND,
                               activePage="company"), 404
