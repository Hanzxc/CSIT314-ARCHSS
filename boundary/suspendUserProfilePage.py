# Boundary: SuspendUserProfilePage - UC6 Suspend user profile (US6)
# the Suspend button + "Are you sure?" box on templates/viewUserProfile.html

from flask import render_template, redirect, url_for, session, flash

from control.suspendUserProfileController import SuspendUserProfileController
from control.viewUserProfileController import ViewUserProfileController

MSG_SUSPENDED = "User profile suspended successfully"
MSG_CANNOT_SUSPEND = "This user profile cannot be suspended"


class SuspendUserProfilePage:
    # UC6 Suspend user profile
    # profileId gets filled in by clickSuspend() or the route
    def __init__(self):
        self.suspendUserProfileController = SuspendUserProfileController()
        self.profileId = None

    def clickSuspend(self, profileId):
        # admin clicked Suspend on the details page -> ask them first.
        # the box shows the profile, so borrow US4's controller to load it
        self.profileId = profileId
        profile = ViewUserProfileController().getUserProfile(profileId)
        if profile is not None:
            return self.displayConfirmation(profile)
        return self.displayErrorMessage(MSG_CANNOT_SUSPEND)

    def displayConfirmation(self, profile):
        # shows the details page again but with the "Are you sure?" box on top (wireframe 4b).
        # did it in plain HTML instead of a JS confirm() so it works even with JS off
        return render_template("viewUserProfile.html", activePage="profiles",
                               profile=profile, showConfirmation=True)

    def confirmSuspend(self):
        # admin clicked Suspend in the box.
        # the page checks this one - the admin can't suspend their own group or
        # they'd lock themselves out (UT6.3)
        if self.profileId != session["profileId"]:
            # already suspended / no such id -> the entity gives back False (UT6.2, UT6.4)
            suspended = self.suspendUserProfileController.suspendUserProfile(self.profileId)
            if suspended:
                return self.displaySuccessMessage(MSG_SUSPENDED)
            return self.displayErrorMessage(MSG_CANNOT_SUSPEND)
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

    # UC6 Suspend user profile
    # back to the profile details with a red message
    def displayErrorMessage(self, msg):
        flash(msg, "error")
        return redirect(url_for("viewUserProfile", profileId=self.profileId))
