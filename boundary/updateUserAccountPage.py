# Boundary: UpdateUserAccountPage - UC10 Update user account (US10)
# template: templates/updateUserAccount.html

from flask import render_template, redirect, url_for, flash

from control.updateUserAccountController import UpdateUserAccountController
from control.searchUserProfileController import SearchUserProfileController

MSG_UPDATED = "User account updated successfully"
MSG_REQUIRED = "Please fill in all required fields"
MSG_INVALID = "Invalid profile or username already exists"
MSG_NOT_FOUND = "Account not found"
MSG_FIELD_REQUIRED = "This field is required"


class UpdateUserAccountPage:
    # UC10 Update user account
    # userId gets filled in by clickUpdate() or submitUpdate()
    def __init__(self):
        self.updateUserAccountController = UpdateUserAccountController()
        self.userId = None
        self.fieldErrors = {}

        # what's in the form right now (from the db at first, then whatever was typed).
        # called "form" so it doesn't clash with {{ username }} in base.html
        self.form = {"username": "", "fullName": "", "email": "", "phone": "", "profileId": None}
        self.status = ""

    # UC10 Update user account
    # admin clicked Update - load the account so the form starts filled in
    def clickUpdate(self, userId):
        self.userId = userId
        account = self.updateUserAccountController.getUserAccount(userId)
        if account is None:
            return self.displayNotFound()
        return self.displayUpdateForm(account)

    def displayUpdateForm(self, account, msg=None):
        # fill the boxes from the account the first time round
        if account is not None:
            self.form = {"username": account.username, "fullName": account.fullName,
                         "email": account.email or "", "phone": account.phone or "",
                         "profileId": account.profileId}
            self.status = account.status

        # drop-down = every profile, borrowed from US7 (same as US8)
        profiles = SearchUserProfileController().searchUserProfiles("")
        return render_template("updateUserAccount.html", activePage="accounts",
                               userId=self.userId, form=self.form, status=self.status,
                               profiles=profiles, fieldErrors=self.fieldErrors,
                               errorMessage=msg)

    # UC10 Update user account
    # admin clicked Save - the page checks all the input, then the controller just updates it
    def submitUpdate(self, userId, username, fullName, email, phone, profileId):
        self.userId = userId
        # keep what they typed so nothing gets wiped if there's an error
        self.form = {"username": username, "fullName": fullName, "email": email,
                     "phone": phone, "profileId": profileId}

        if not self.validateInput(username, fullName, email, phone, profileId):
            return self.displayErrorMessage(MSG_REQUIRED)

        if self.updateUserAccountController.updateUserAccount(
                userId, username.strip(), fullName.strip(),
                (email or "").strip(), (phone or "").strip(), profileId):
            return self.displaySuccessMessage(MSG_UPDATED)

        # it failed - either the account is gone, or it's alt flow 5a
        if self.updateUserAccountController.getUserAccount(userId) is None:
            return self.displayNotFound()
        return self.displayErrorMessage(MSG_INVALID)

    # UT10.7 - same required fields as US8, minus the password
    def validateInput(self, username, fullName, email, phone, profileId):
        self.fieldErrors = {}

        if not username or not username.strip():
            self.fieldErrors["username"] = MSG_FIELD_REQUIRED
        if not fullName or not fullName.strip():
            self.fieldErrors["fullName"] = MSG_FIELD_REQUIRED
        if profileId is None:
            self.fieldErrors["profileId"] = MSG_FIELD_REQUIRED

        return len(self.fieldErrors) == 0

    def displaySuccessMessage(self, msg):
        # go to the account's details page with the message (step 7)
        flash(msg, "success")
        return redirect(url_for("viewUserAccount", userId=self.userId))

    def displayErrorMessage(self, msg):
        # status isn't in the form so grab it again for the badge at the top
        account = self.updateUserAccountController.getUserAccount(self.userId)
        if account is not None:
            self.status = account.status
        # pass None as the account so it doesn't overwrite what they typed
        return self.displayUpdateForm(None, msg)

    def displayNotFound(self):
        # not on the class diagram, just so a bad id doesn't crash the page
        return render_template("updateUserAccount.html", activePage="accounts",
                               userId=None, errorMessage=MSG_NOT_FOUND)
