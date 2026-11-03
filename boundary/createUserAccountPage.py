# Boundary: CreateUserAccountPage - UC8 Create user account (US8)
# template: templates/createUserAccount.html

from flask import render_template, redirect, url_for, flash

from control.createUserAccountController import CreateUserAccountController
from control.searchUserProfileController import SearchUserProfileController

MSG_CREATED = "User account created successfully"
MSG_REQUIRED = "Please fill in all required fields"
MSG_INVALID = "Invalid profile or username already exists"
MSG_FIELD_REQUIRED = "This field is required"


class CreateUserAccountPage:
    # UC8 Create user account
    # starts with an empty form and no errors
    def __init__(self):
        self.createUserAccountController = CreateUserAccountController()
        self.fieldErrors = {}       # e.g. {"username": MSG_FIELD_REQUIRED}

        # whatever the admin typed, so the form can be refilled if there's an error (alt flow 4a).
        # the password isn't kept on purpose - don't want it sitting in the page's HTML
        self.form = {"username": "", "fullName": "", "email": "", "phone": "", "profileId": None}

    # UC8 Create user account
    # admin clicked "Create user account" - just show the empty form
    def clickCreateUserAccount(self):
        return self.displayCreateForm()

    def displayCreateForm(self, msg=None):
        # the profile drop-down is a list of every profile, which is US7's job (search with
        # an empty keyword) - so we borrow that controller instead of adding it to this one.
        # passed as "form" not "username" etc. - base.html already uses {{ username }}
        # for "Logged in as ..." and we don't want to overwrite it
        profiles = SearchUserProfileController().searchUserProfiles("")
        return render_template("createUserAccount.html", activePage="accounts",
                               form=self.form, profiles=profiles,
                               fieldErrors=self.fieldErrors, errorMessage=msg)

    # UC8 Create user account
    # admin clicked Create - the page checks all the input, then the controller just creates it
    def submitCreateAccount(self, username, password, fullName, email, phone, profileId):
        self.form = {"username": username, "fullName": fullName, "email": email,
                     "phone": phone, "profileId": profileId}

        # missing field -> controller never gets called (outer alt in the seq diagram)
        if not self.validateInput(username, password, fullName, email, phone, profileId):
            return self.displayErrorMessage(MSG_REQUIRED)

        # tidy it up here so the controller/entity get clean values.
        # password is NOT stripped, spaces could be on purpose
        if self.createUserAccountController.createUserAccount(
                username.strip(), password, fullName.strip(),
                (email or "").strip(), (phone or "").strip(), profileId):
            return self.displaySuccessMessage(MSG_CREATED)

        # alt flow 5a - suspended profile or username taken (the entity found a duplicate)
        return self.displayErrorMessage(MSG_INVALID)

    # UT8.7 - only checks the required ones are filled in, email and phone are optional
    def validateInput(self, username, password, fullName, email, phone, profileId):
        self.fieldErrors = {}

        if not username or not username.strip():
            self.fieldErrors["username"] = MSG_FIELD_REQUIRED
        if not password:
            self.fieldErrors["password"] = MSG_FIELD_REQUIRED
        if not fullName or not fullName.strip():
            self.fieldErrors["fullName"] = MSG_FIELD_REQUIRED
        if profileId is None:
            self.fieldErrors["profileId"] = MSG_FIELD_REQUIRED

        return len(self.fieldErrors) == 0

    def displaySuccessMessage(self, msg):
        # back to the User Accounts list with the green message (step 7)
        flash(msg, "success")
        return redirect(url_for("accounts"))

    def displayErrorMessage(self, msg):
        # same form again with the message on top
        return self.displayCreateForm(msg)
