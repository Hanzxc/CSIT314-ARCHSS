# Boundary: DeleteCompanyProfilePage - UC17 Delete company profile (US17)
# template: templates/deleteCompanyProfile.html (the "are you sure?" box holds hidden companyId + revision)
# precondition: the designer is already logged in (US13), so there's no extra access check here.
# no token and nothing kept in the session - the entity's revision check stops an old box

from flask import flash, redirect, render_template, session, url_for

from control.deleteCompanyProfileController import DeleteCompanyProfileController

MSG_DELETED = "Company profile deleted successfully"
MSG_NOT_FOUND = "You have not created a company profile yet"
MSG_CONFIRM_AGAIN = "Please open the delete confirmation and try again"
MSG_FAILED = "Company profile could not be deleted. Please reopen the confirmation"


class DeleteCompanyProfilePage:
    # UC17 Delete company profile
    # just sets up the controller
    def __init__(self):
        self.deleteCompanyProfileController = DeleteCompanyProfileController()

    # UC17 Delete company profile
    # designer clicked Delete - show the "are you sure?" box if they have a profile
    def clickDelete(self):
        profile = self.deleteCompanyProfileController.getCompanyProfile(session["userId"])
        if profile is not None:
            return self.displayConfirmation(profile)
        return self.displayNotFoundMessage()

    # UC17 Delete company profile
    # the box names the company, its companyId + revision go in hidden fields
    def displayConfirmation(self, profile):
        return render_template("deleteCompanyProfile.html", company=profile, activePage="company")

    # UC17 Delete company profile
    # works out if they clicked Delete or Cancel in the confirmation box
    def submitDelete(self, choice, companyId, revision):
        if choice == "delete":
            return self.confirmDelete(companyId, revision)
        if choice == "cancel":
            return self.cancelDelete()
        return self.displayErrorMessage(MSG_CONFIRM_AGAIN)

    # UC17 Delete company profile
    # the owner always comes from the session. the entity only suspends the row if the
    # companyId and revision still match this owner's Active profile
    def confirmDelete(self, companyId, revision):
        deleted = self.deleteCompanyProfileController.deleteCompanyProfile(session["userId"], companyId, revision)
        if deleted:
            return self.displaySuccessMessage(MSG_DELETED)
        return self.displayErrorMessage(MSG_FAILED)

    # UC17 Delete company profile
    # alt flow - nothing changes, just close the box
    def cancelDelete(self):
        return self.closeConfirmation()

    # UC17 Delete company profile
    # back to the company profile page
    def closeConfirmation(self):
        return redirect(url_for("viewCompanyProfile"))

    # UC17 Delete company profile
    # back to the dashboard with a green message (it now offers Restore)
    def displaySuccessMessage(self, msg):
        flash(msg, "success")
        return redirect(url_for("interiorDesignerDashboard"))

    # UC17 Delete company profile
    # old or changed form, or no choice - show the error page, nothing is deleted
    def displayErrorMessage(self, msg):
        return render_template("companyProfileDeleteError.html", errorMessage=msg,
                               activePage="company"), 400

    # UC17 Delete company profile
    # shows the "no company profile" page (404) when there's nothing to show
    def displayNotFoundMessage(self):
        return render_template("companyProfileNotFound.html", errorMessage=MSG_NOT_FOUND,
                               activePage="company"), 404
