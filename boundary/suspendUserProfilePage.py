# Boundary: SuspendUserProfilePage - UC6 Suspend user profile (US6)
# the Suspend button + "Are you sure?" box on templates/viewUserProfile.html

from flask import render_template, redirect, url_for, session

from control.suspendUserProfileController import SuspendUserProfileController

MSG_SUSPENDED = "User profile suspended successfully"
MSG_CANNOT_SUSPEND = "This user profile cannot be suspended"


class SuspendUserProfilePage:
    def __init__(self):
        self.suspendUserProfileController = SuspendUserProfileController()
        self.profileId = None

    def clickSuspend(self, profileId):
        # TODO: self.profileId = profileId, then self.displayConfirmation()
        pass

    def displayConfirmation(self):
        # TODO: show the "Are you sure?" box (can just be a JS confirm() in the template)
        pass

    def confirmSuspend(self):
        # TODO (sequence diagram msgs 4-15):
        # - adminProfileId = session["profileId"]
        # - success = self.suspendUserProfileController.suspendUserProfile(self.profileId, adminProfileId)
        # - success True  -> return self.displaySuccessMessage(MSG_SUSPENDED)
        # - success False -> return self.displayErrorMessage(MSG_CANNOT_SUSPEND)
        pass

    def cancelSuspend(self):
        # TODO: nothing changes -> self.closeConfirmation()
        pass

    def closeConfirmation(self):
        # TODO: hide the box, stay on the details page
        pass

    def displaySuccessMessage(self, msg):
        # TODO: back to the details page, profile now shows as Suspended
        pass

    def displayErrorMessage(self, msg):
        # TODO: back to the details page with the error
        pass
