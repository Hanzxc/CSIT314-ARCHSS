# Boundary: CreateUserProfilePage - UC3 Create user profile (US3)
# template: templates/createUserProfile.html

from flask import render_template, redirect, url_for

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

    def clickCreateUserProfile(self):
        # TODO:
        # - permissionList = self.createUserProfileController.getAllPermissions()
        # - return self.displayCreateForm(permissionList)
        pass

    def displayCreateForm(self, permissionList):
        # TODO: return render_template("createUserProfile.html", permissionList=permissionList, ...)
        # (when showing errors, also pass back what was typed so it isn't lost)
        pass

    def submitUserProfile(self, profileName, description, permissions):
        # TODO (sequence diagram msgs 8-19):
        # - if not self.validateInput(...) -> return self.displayErrorMessage(MSG_FIX_FIELDS)
        # - success = self.createUserProfileController.createUserProfile(...)
        # - success True  -> return self.displaySuccessMessage(MSG_CREATED)
        # - success False -> return self.displayErrorMessage(MSG_NAME_TAKEN)
        pass

    # UT3.9 to UT3.12
    def validateInput(self, profileName, permissions):
        # TODO:
        # - name must be 3-50 chars (after strip) -> else self.fieldErrors["profileName"] = MSG_NAME_LENGTH
        # - at least 1 permission ticked -> else self.fieldErrors["permissions"] = MSG_NO_PERMISSION
        # - return True if no errors, else False
        pass

    def displaySuccessMessage(self, msg):
        # TODO: back to the User Profiles list with the message
        pass

    def displayErrorMessage(self, msg):
        # TODO: show the form again with msg + self.fieldErrors highlighted
        pass
