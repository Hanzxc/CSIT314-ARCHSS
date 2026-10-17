# Boundary: UpdateUserProfilePage - UC5 Update user profile (US5)
# template: templates/updateUserProfile.html

from flask import render_template, redirect, url_for

from control.updateUserProfileController import UpdateUserProfileController

MSG_UPDATED = "User profile updated successfully"
MSG_NAME_TAKEN = "A user profile with this name already exists"
MSG_FIX_FIELDS = "Please fix the highlighted fields"
MSG_NAME_LENGTH = "Profile name must be 3-50 characters"
MSG_NO_PERMISSION = "Tick at least one permission"
MSG_NOT_FOUND = "User profile not found"


class UpdateUserProfilePage:
    def __init__(self):
        self.updateUserProfileController = UpdateUserProfileController()
        self.profileId = None       # set by clickUpdate() / the route, used by submitUpdate()
        self.fieldErrors = {}

    def clickUpdate(self, profileId):
        # TODO (sequence diagram msgs 2-10):
        # - self.profileId = profileId
        # - profile = self.updateUserProfileController.getUserProfile(profileId)
        # - permissionList = self.updateUserProfileController.getAllPermissions()
        # - return self.displayUpdateForm(profile, permissionList)
        pass

    def displayUpdateForm(self, profile, permissionList):
        # TODO: render_template("updateUserProfile.html", profile=profile, permissionList=permissionList)
        # current permissions are already ticked
        pass

    def submitUpdate(self, profileName, description, permissions):
        # TODO (sequence diagram msgs 12-23):
        # - if not self.validateInput(...) -> return self.displayErrorMessage(MSG_FIX_FIELDS)
        # - success = self.updateUserProfileController.updateUserProfile(self.profileId, ...)
        # - success True  -> return self.displaySuccessMessage(MSG_UPDATED)
        # - success False -> return self.displayErrorMessage(MSG_NAME_TAKEN)
        pass

    # UT5.9 - same rules as US3
    def validateInput(self, profileName, permissions):
        # TODO: name 3-50 chars, at least 1 permission, fill in self.fieldErrors, return True/False
        pass

    def displaySuccessMessage(self, msg):
        # TODO: go to the updated profile details page with the message
        pass

    def displayErrorMessage(self, msg):
        # TODO: show the form again with msg + self.fieldErrors, keep what was typed
        pass
