# Boundary: CreateUserProfilePage - UC3 Create user profile (US3)
# template: templates/createUserProfile.html

from flask import render_template, redirect, url_for, flash

from control.createUserProfileController import CreateUserProfileController
from entity.userProfile import UserProfile

MSG_CREATED = "User profile created successfully"
MSG_NAME_TAKEN = "A user profile with this name already exists"
MSG_FIX_FIELDS = "Please fix the highlighted fields"
MSG_NAME_LENGTH = "Profile name must be 3-50 characters"
MSG_NO_PERMISSION = "Tick at least one permission"


class CreateUserProfilePage:
    # UC3 Create user profile
    # starts with an empty form and no errors
    def __init__(self):
        self.createUserProfileController = CreateUserProfileController()
        self.profile = UserProfile()    # what's in the form, so it can be refilled if there's an error (alt flow 4a)
        self.fieldErrors = {}           # e.g. {"profileName": MSG_NAME_LENGTH, "permissions": MSG_NO_PERMISSION}

    # UC3 Create user profile
    # admin clicked "Create user profile" - get the permission tick boxes and show the form
    def clickCreateUserProfile(self):
        permissionList = self.createUserProfileController.getAllPermissions()
        return self.displayCreateForm(permissionList)

    # UC3 Create user profile
    # shows the form, refilled with what was typed and with any errors highlighted
    def displayCreateForm(self, permissionList, msg=None):
        return render_template("createUserProfile.html", activePage="profiles",
                               permissionList=permissionList,
                               profileName=self.profile.profileName,
                               description=self.profile.description,
                               permissions=self.profile.permissions,
                               fieldErrors=self.fieldErrors,
                               errorMessage=msg)

    def submitUserProfile(self, profileName, description, permissions):
        # the page trims the spaces first, then puts the form into a UserProfile
        self.profile = UserProfile(profileName=profileName.strip(), description=description.strip(),
                                   permissions=permissions)

        # bad input -> controller never gets called (outer alt in the seq diagram)
        if not self.validateInput(self.profile):
            return self.displayErrorMessage(MSG_FIX_FIELDS)

        created = self.createUserProfileController.createUserProfile(self.profile)
        if created:
            return self.displaySuccessMessage(MSG_CREATED)

        # the only way it fails is the entity finding the name is taken (alt flow 5a)
        self.fieldErrors["profileName"] = MSG_NAME_TAKEN
        return self.displayErrorMessage(MSG_NAME_TAKEN)

    # UT3.9 to UT3.12
    def validateInput(self, profile):
        self.fieldErrors = {}       # start fresh each time

        if len(profile.profileName) < 3 or len(profile.profileName) > 50:
            self.fieldErrors["profileName"] = MSG_NAME_LENGTH

        if not profile.permissions:
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
