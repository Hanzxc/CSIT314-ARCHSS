# Boundary: CreateUserAccountPage - UC8 Create user account (US8)
# template: templates/createUserAccount.html

from flask import render_template, redirect, url_for, flash

from control.createUserAccountController import CreateUserAccountController
from control.searchUserProfileController import SearchUserProfileController
from entity.userAccount import UserAccount

MSG_CREATED = "User account created successfully"
MSG_REQUIRED = "Please fill in all required fields"
MSG_INVALID = "Invalid profile or username already exists"
MSG_FIELD_REQUIRED = "This field is required"


class CreateUserAccountPage:
    # UC8 Create user account
    # starts with an empty form and no errors
    def __init__(self):
        self.createUserAccountController = CreateUserAccountController()
        self.account = UserAccount()    # what's in the form, so it can be refilled if there's an error (alt flow 4a)
        self.fieldErrors = {}           # e.g. {"username": MSG_FIELD_REQUIRED}

    # UC8 Create user account
    # admin clicked "Create user account" - get the profile drop-down first, then show the form.
    # the drop-down is a list of every profile, which is US7's job (search with an empty keyword),
    # so we borrow that controller instead of adding it to this one
    def clickCreateUserAccount(self):
        profiles = SearchUserProfileController().searchUserProfiles("")
        return self.displayCreateForm(profiles)

    def displayCreateForm(self, profiles, msg=None):
        # passed as "form" so the typed username can't clash with the header's names.
        # the password is never put back in the form on purpose
        return render_template("createUserAccount.html", activePage="accounts",
                               form=self.account, profiles=profiles,
                               fieldErrors=self.fieldErrors, errorMessage=msg)

    # UC8 Create user account
    # admin clicked Create - the page checks all the input, then the controller just creates it
    def submitCreateAccount(self, username, password, fullName, email, phone, profileId):
        # trim everything except the password (spaces there could be on purpose), then build the account
        self.account = UserAccount(username=username.strip(), password=password,
                                   fullName=fullName.strip(), email=email.strip(),
                                   phone=phone.strip(), profileId=profileId)

        # missing field -> controller never gets called (outer alt in the seq diagram)
        if not self.validateInput(self.account):
            return self.displayErrorMessage(MSG_REQUIRED)

        created = self.createUserAccountController.createUserAccount(self.account)
        if created:
            return self.displaySuccessMessage(MSG_CREATED)

        # alt flow 5a - suspended profile or username taken (the entity found the problem)
        return self.displayErrorMessage(MSG_INVALID)

    # UT8.7 - only checks the required ones are filled in, email and phone are optional
    def validateInput(self, account):
        self.fieldErrors = {}

        if not account.username:
            self.fieldErrors["username"] = MSG_FIELD_REQUIRED
        if not account.password:
            self.fieldErrors["password"] = MSG_FIELD_REQUIRED
        if not account.fullName:
            self.fieldErrors["fullName"] = MSG_FIELD_REQUIRED
        if account.profileId is None:
            self.fieldErrors["profileId"] = MSG_FIELD_REQUIRED

        return len(self.fieldErrors) == 0

    def displaySuccessMessage(self, msg):
        # back to the User Accounts list with the green message (step 7)
        flash(msg, "success")
        return redirect(url_for("accounts"))

    def displayErrorMessage(self, msg):
        # same form again with the message on top - the drop-down is loaded again the same way
        profiles = SearchUserProfileController().searchUserProfiles("")
        return self.displayCreateForm(profiles, msg)
