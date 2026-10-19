# Boundary: CreateUserProfilePage - UC3 Create user profile (US3)
# template: templates/createUserProfile.html

from flask import render_template, redirect, url_for, flash

from control.createUserProfileController import CreateUserProfileController

MSG_CREATED = "User profile created successfully"
MSG_NAME_TAKEN = "A user profile with this name already exists"
MSG_FIX_FIELDS = "Please fix the highlighted fields"
MSG_NAME_LENGTH = "Profile name must be 3-50 characters"
MSG_NO_PERMISSION = "Tick at least one permission"


class CreateUserProfilePage:
    def __init__(self):
        self.createUserProfileController = CreateUserProfileController()
        self.fieldErrors = {}       # e.g. {"profileName": MSG_NAME_LENGTH, "permissions": MSG_NO_PERMISSION}

        # whatever the admin typed, so the form can be refilled if there's an error (alt flow 4a)
        self.profileName = ""
        self.description = ""
        self.permissions = []

    def clickCreateUserProfile(self):
        permissionList = self.createUserProfileController.getAllPermissions()
        return self.displayCreateForm(permissionList)

    def displayCreateForm(self, permissionList, msg=None):
        return render_template("createUserProfile.html", activePage="profiles",
                               permissionList=permissionList,
                               profileName=self.profileName,
                               description=self.description,
                               permissions=self.permissions,
                               fieldErrors=self.fieldErrors,
                               errorMessage=msg)

    def submitUserProfile(self, profileName, description, permissions):
        # remember what was typed first, in case we need to show the form again
        self.profileName = profileName
        self.description = description
        self.permissions = permissions

        # bad input -> controller never gets called (outer alt in the seq diagram)
        if not self.validateInput(profileName, permissions):
            return self.displayErrorMessage(MSG_FIX_FIELDS)

        success = self.createUserProfileController.createUserProfile(profileName, description, permissions)
        if success:
            return self.displaySuccessMessage(MSG_CREATED)

        # the only way it fails now is the name being taken (alt flow 5a)
        self.fieldErrors["profileName"] = MSG_NAME_TAKEN
        return self.displayErrorMessage(MSG_NAME_TAKEN)

    # UT3.9 to UT3.12
    def validateInput(self, profileName, permissions):
        self.fieldErrors = {}       # start fresh each time

        name = profileName.strip()
        if len(name) < 3 or len(name) > 50:
            self.fieldErrors["profileName"] = MSG_NAME_LENGTH

        if not permissions:
            self.fieldErrors["permissions"] = MSG_NO_PERMISSION

        return len(self.fieldErrors) == 0

    def displaySuccessMessage(self, msg):
        # back to the User Profiles list, flash() keeps the message across the redirect (wireframe 4d)
        flash(msg, "success")
        return redirect(url_for("profiles"))

    def displayErrorMessage(self, msg):
        # same form again with the message on top + the bad fields in red (wireframe 4c)
        permissionList = self.createUserProfileController.getAllPermissions()
        return self.displayCreateForm(permissionList, msg)
