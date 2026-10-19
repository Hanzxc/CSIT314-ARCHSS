# Boundary: UpdateUserProfilePage - UC5 Update user profile (US5)
# template: templates/updateUserProfile.html

from flask import render_template, redirect, url_for, flash

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

        # what's in the form right now (from the db at first, then whatever was typed)
        self.profileName = ""
        self.description = ""
        self.permissions = []
        self.status = ""

    def clickUpdate(self, profileId):
        self.profileId = profileId
        profile = self.updateUserProfileController.getUserProfile(profileId)
        if profile is None:
            return self.displayNotFound()

        permissionList = self.updateUserProfileController.getAllPermissions()
        return self.displayUpdateForm(profile, permissionList)

    def displayUpdateForm(self, profile, permissionList, msg=None):
        # fill the boxes from the profile so the current permissions are already ticked
        if profile is not None:
            self.profileName = profile.profileName
            self.description = profile.description
            self.permissions = profile.permissions
            self.status = profile.status

        return render_template("updateUserProfile.html", activePage="profiles",
                               profileId=self.profileId,
                               profileName=self.profileName,
                               description=self.description,
                               permissions=self.permissions,
                               status=self.status,
                               permissionList=permissionList,
                               fieldErrors=self.fieldErrors,
                               errorMessage=msg)

    def submitUpdate(self, profileName, description, permissions):
        # keep what they typed so nothing gets wiped if there's an error
        self.profileName = profileName
        self.description = description
        self.permissions = permissions

        if not self.validateInput(profileName, permissions):
            return self.displayErrorMessage(MSG_FIX_FIELDS)

        success = self.updateUserProfileController.updateUserProfile(
            self.profileId, profileName, description, permissions)
        if success:
            return self.displaySuccessMessage(MSG_UPDATED)

        # it failed - either the profile is gone or the name is taken, need to tell which
        if self.updateUserProfileController.getUserProfile(self.profileId) is None:
            return self.displayNotFound()

        self.fieldErrors["profileName"] = MSG_NAME_TAKEN
        return self.displayErrorMessage(MSG_NAME_TAKEN)

    # UT5.9 - same rules as US3
    def validateInput(self, profileName, permissions):
        self.fieldErrors = {}

        name = profileName.strip()
        if len(name) < 3 or len(name) > 50:
            self.fieldErrors["profileName"] = MSG_NAME_LENGTH

        if not permissions:
            self.fieldErrors["permissions"] = MSG_NO_PERMISSION

        return len(self.fieldErrors) == 0

    def displaySuccessMessage(self, msg):
        # go to the updated profile's details page with the message (wireframe 4d)
        flash(msg, "success")
        return redirect(url_for("viewUserProfile", profileId=self.profileId))

    def displayErrorMessage(self, msg):
        # status isn't in the form so grab it again for the badge at the top
        profile = self.updateUserProfileController.getUserProfile(self.profileId)
        if profile is not None:
            self.status = profile.status

        permissionList = self.updateUserProfileController.getAllPermissions()
        # pass None as the profile so it doesn't overwrite what they typed
        return self.displayUpdateForm(None, permissionList, msg)

    def displayNotFound(self):
        # not on the class diagram, just a small helper so the page doesn't crash on a bad id
        return render_template("updateUserProfile.html", activePage="profiles",
                               profileId=None, errorMessage=MSG_NOT_FOUND)
