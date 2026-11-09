# Boundary: UpdateUserAccountPage - UC10 Update user account (US10)
# template: templates/updateUserAccount.html

from flask import render_template, redirect, url_for, flash

from control.updateUserAccountController import UpdateUserAccountController
from control.searchUserProfileController import SearchUserProfileController
from entity.userAccount import UserAccount

MSG_UPDATED = "User account updated successfully"
MSG_REQUIRED = "Please fill in all required fields"
MSG_INVALID = "Invalid profile or username already exists"
MSG_NOT_FOUND = "Account not found"
MSG_FIELD_REQUIRED = "This field is required"


class UpdateUserAccountPage:
    # UC10 Update user account
    # starts with an empty form and no errors
    def __init__(self):
        self.updateUserAccountController = UpdateUserAccountController()
        self.account = UserAccount()    # what's in the form right now
        self.fieldErrors = {}

    # UC10 Update user account
    # admin clicked Update - load the account, then the profile drop-down, so the form starts filled in
    def clickUpdate(self, userId):
        account = self.updateUserAccountController.getUserAccount(userId)
        if account is not None:
            # drop-down = every profile, borrowed from US7 (same as US8)
            profiles = SearchUserProfileController().searchUserProfiles("")
            return self.displayUpdateForm(account, profiles)
        return self.displayNotFound()

    def displayUpdateForm(self, account, profiles, msg=None):
        # passed as "form" so the typed username can't clash with the header's names
        return render_template("updateUserAccount.html", activePage="accounts",
                               userId=account.userId, form=account,
                               profiles=profiles, fieldErrors=self.fieldErrors,
                               errorMessage=msg)

    # UC10 Update user account
    # admin clicked Save - the page checks all the input, then the controller just updates it
    def submitUpdate(self, userId, username, fullName, email, phone, profileId):
        # the page trims the input first, then puts the form into a UserAccount
        self.account = UserAccount(userId=userId, username=username.strip(), fullName=fullName.strip(),
                                   email=email.strip(), phone=phone.strip(), profileId=profileId)

        # missing field -> controller never gets called (outer alt in the seq diagram)
        if not self.validateInput(self.account):
            return self.displayErrorMessage(MSG_REQUIRED)

        updated = self.updateUserAccountController.updateUserAccount(self.account)
        if updated:
            return self.displaySuccessMessage(MSG_UPDATED)

        # alt flow 5a - suspended profile, username taken or the account itself is suspended
        return self.displayErrorMessage(MSG_INVALID)

    # UT10.7 - same required fields as US8, minus the password
    def validateInput(self, account):
        self.fieldErrors = {}

        if not account.username:
            self.fieldErrors["username"] = MSG_FIELD_REQUIRED
        if not account.fullName:
            self.fieldErrors["fullName"] = MSG_FIELD_REQUIRED
        if account.profileId is None:
            self.fieldErrors["profileId"] = MSG_FIELD_REQUIRED

        return len(self.fieldErrors) == 0

    def displaySuccessMessage(self, msg):
        # go to the account's details page with the message (step 7)
        flash(msg, "success")
        return redirect(url_for("viewUserAccount", userId=self.account.userId))

    def displayErrorMessage(self, msg):
        # the form again with what was typed - the drop-down is loaded again the same way
        profiles = SearchUserProfileController().searchUserProfiles("")
        return self.displayUpdateForm(self.account, profiles, msg)

    def displayNotFound(self):
        # alt flow 2a - no account with this id
        return render_template("updateUserAccount.html", activePage="accounts",
                               userId=None, errorMessage=MSG_NOT_FOUND)
