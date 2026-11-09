# Boundary: UpdateUserProfilePage - UC5 Update user profile (US5)
# template: templates/updateUserProfile.html

from flask import render_template, redirect, url_for, flash

from control.updateUserProfileController import UpdateUserProfileController
from control.createUserProfileController import CreateUserProfileController
from entity.userProfile import UserProfile

MSG_UPDATED = "User profile updated successfully"
MSG_CANNOT_UPDATE = "This user profile could not be updated - the name is already used or the profile is suspended"
MSG_FIX_FIELDS = "Please fix the highlighted fields"
MSG_NAME_LENGTH = "Profile name must be 3-50 characters"
MSG_NO_PERMISSION = "Tick at least one permission"
MSG_NOT_FOUND = "User profile not found"


class UpdateUserProfilePage:
    # UC5 Update user profile
    # profileId gets filled in by clickUpdate() or the route
    def __init__(self):
        self.updateUserProfileController = UpdateUserProfileController()
        self.profileId = None       # set by clickUpdate() / the route, used by submitUpdate()
        self.profile = UserProfile()    # what's in the form right now
        self.fieldErrors = {}

    # UC5 Update user profile
    # admin clicked Update - load the profile, then the permission list, so the form starts filled in
    def clickUpdate(self, profileId):
        self.profileId = profileId
        profile = self.updateUserProfileController.getUserProfile(profileId)
        if profile is not None:
            # the tick boxes are US3's form data, so borrow US3's controller for them
            permissionList = CreateUserProfileController().getAllPermissions()
            return self.displayUpdateForm(profile, permissionList)
        return self.displayNotFound()

    def displayUpdateForm(self, profile, permissionList, msg=None):
        # fill the boxes from the profile so the current permissions are already ticked
        return render_template("updateUserProfile.html", activePage="profiles",
                               profileId=self.profileId,
                               profileName=profile.profileName,
                               description=profile.description,
                               permissions=profile.permissions,
                               status=profile.status,
                               permissionList=permissionList,
                               fieldErrors=self.fieldErrors,
                               errorMessage=msg)

    def submitUpdate(self, profileName, description, permissions):
        # the page trims the spaces first, then puts the form into a UserProfile
        self.profile = UserProfile(profileId=self.profileId, profileName=profileName.strip(),
                                   description=description.strip(), permissions=permissions)

        # bad input -> controller never gets called (outer alt in the seq diagram)
        if not self.validateInput(self.profile):
            return self.displayErrorMessage(MSG_FIX_FIELDS)

        updated = self.updateUserProfileController.updateUserProfile(self.profile)
        if updated:
            return self.displaySuccessMessage(MSG_UPDATED)

        # the profile is suspended or the name belongs to a different profile (alt flow 6a)
        return self.displayErrorMessage(MSG_CANNOT_UPDATE)

    # UT5.9 - same rules as US3
    def validateInput(self, profile):
        self.fieldErrors = {}

        if len(profile.profileName) < 3 or len(profile.profileName) > 50:
            self.fieldErrors["profileName"] = MSG_NAME_LENGTH

        if not profile.permissions:
            self.fieldErrors["permissions"] = MSG_NO_PERMISSION

        return len(self.fieldErrors) == 0

    def displaySuccessMessage(self, msg):
        # go to the updated profile's details page with the message (wireframe 4d)
        flash(msg, "success")
        return redirect(url_for("viewUserProfile", profileId=self.profileId))

    def displayErrorMessage(self, msg):
        # the form again with what was typed - the status badge and the tick boxes
        # are loaded again the same way as clickUpdate()
        savedProfile = self.updateUserProfileController.getUserProfile(self.profileId)
        self.profile.status = savedProfile.status if savedProfile is not None else ""
        permissionList = CreateUserProfileController().getAllPermissions()
        return self.displayUpdateForm(self.profile, permissionList, msg)

    def displayNotFound(self):
        # alt flow 2a - no profile with this id
        return render_template("updateUserProfile.html", activePage="profiles",
                               profileId=None, errorMessage=MSG_NOT_FOUND)
