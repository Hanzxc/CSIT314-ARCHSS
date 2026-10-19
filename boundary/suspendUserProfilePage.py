# Boundary: SuspendUserProfilePage - UC6 Suspend user profile (US6)
# the Suspend button + "Are you sure?" box on templates/viewUserProfile.html

from flask import render_template, redirect, url_for, session, flash

from control.suspendUserProfileController import SuspendUserProfileController
from control.viewUserProfileController import ViewUserProfileController

MSG_SUSPENDED = "User profile suspended successfully"
MSG_CANNOT_SUSPEND = "This user profile cannot be suspended"


class SuspendUserProfilePage:
    def __init__(self):
        self.suspendUserProfileController = SuspendUserProfileController()
        self.profileId = None

    def clickSuspend(self, profileId):
        # admin clicked Suspend on the details page -> ask them first
        self.profileId = profileId
        return self.displayConfirmation()

    def displayConfirmation(self):
        # shows the details page again but with the "Are you sure?" box on top (wireframe 4b).
        # did it in plain HTML instead of a JS confirm() so it works even with JS off.
        # borrowing the US4 controller just to load the profile for the page behind the box
        profile = ViewUserProfileController().getUserProfile(self.profileId)
        if profile is None:
            return self.displayErrorMessage(MSG_CANNOT_SUSPEND)
        return render_template("viewUserProfile.html", activePage="profiles",
                               profile=profile, showConfirmation=True)

    def confirmSuspend(self):
        # admin clicked OK in the box
        adminProfileId = session["profileId"]
        success = self.suspendUserProfileController.suspendUserProfile(self.profileId, adminProfileId)
        if success:
            return self.displaySuccessMessage(MSG_SUSPENDED)
        return self.displayErrorMessage(MSG_CANNOT_SUSPEND)

    def cancelSuspend(self):
        # alt flow 3a - nothing changes, just close the box
        return self.closeConfirmation()

    def closeConfirmation(self):
        # back to the normal details page (no box)
        return redirect(url_for("viewUserProfile", profileId=self.profileId))

    def displaySuccessMessage(self, msg):
        # details page will now show the Suspended badge (wireframe 4c)
        flash(msg, "success")
        return redirect(url_for("viewUserProfile", profileId=self.profileId))

    def displayErrorMessage(self, msg):
        flash(msg, "error")
        return redirect(url_for("viewUserProfile", profileId=self.profileId))
